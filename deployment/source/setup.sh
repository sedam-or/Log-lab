#!/usr/bin/env bash
# Pasang peran Source di guest Debian 13 (VM A, hostname loglab-source). Aman dipanggil ulang:
# env, secret, sertifikat, akun, dan data yang sudah ada tidak ditimpa.
#
# Pakai (dari ~/LogLab, sebagai user loglab):   sudo bash deployment/source/setup.sh
# Opsi lingkungan:
#   LOGLAB_SKIP_FIREWALL=1   lewati pemasangan firewall (mis. saat masih SSH lewat NAT)
set -euo pipefail

SERVICE_USER="loglab-svc"
LAB_USER="loglab"
WANTED_HOSTNAME="loglab-source"
SOURCE_IP="172.16.202.21"
SOURCE_PORT="8443"
CONF_DIR="/etc/loglab"
DATA_DIR="/var/lib/loglab"
ENV_FILE="${CONF_DIR}/source.env"
ACCOUNTS_FILE="${CONF_DIR}/test-accounts.json"
DB_FILE="${DATA_DIR}/source.sqlite3"
UNIT_DIR="/etc/systemd/system"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${HERE}/../.." && pwd)"
PYTHON="${PROJECT_DIR}/.venv/bin/python"

say()  { printf '==> %s\n' "$*"; }
fail() { printf 'GAGAL: %s\n' "$*" >&2; exit 1; }

check_root() {
    [ "$(id -u)" -eq 0 ] || fail "jalankan dengan sudo: sudo bash deployment/source/setup.sh"
}

check_os() {
    say "Memeriksa OS dan Python"
    # shellcheck disable=SC1091
    . /etc/os-release
    [ "${ID:-}" = "debian" ] && [ "${VERSION_ID:-}" = "13" ] || fail "OS harus Debian 13 (ditemukan: ${PRETTY_NAME:-tidak diketahui})"
    [ -x "$PYTHON" ] || fail "virtualenv belum ada. Jalankan dulu sebagai user ${LAB_USER}: make dev-setup"
    "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) else 1)' || fail "Python virtualenv harus 3.13"
    "$PYTHON" -c 'import loglab' || fail "package loglab belum terpasang di virtualenv (jalankan make dev-setup)"
}

install_packages() {
    say "Memasang paket sistem yang dibutuhkan"
    local missing=() package
    for package in nftables acl curl openssl ca-certificates; do
        dpkg -s "$package" >/dev/null 2>&1 || missing+=("$package")
    done
    if [ "${#missing[@]}" -gt 0 ]; then
        apt-get update -qq
        DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${missing[@]}"
    fi
}

set_hostname() {
    [ "$(hostname)" = "$WANTED_HOSTNAME" ] && return 0
    say "Mengatur hostname menjadi ${WANTED_HOSTNAME}"
    hostnamectl set-hostname "$WANTED_HOSTNAME"
    if grep -q '^127\.0\.1\.1' /etc/hosts; then
        sed -i "s/^127\.0\.1\.1.*/127.0.1.1\t${WANTED_HOSTNAME}/" /etc/hosts
    else
        printf '127.0.1.1\t%s\n' "$WANTED_HOSTNAME" >> /etc/hosts
    fi
}

ensure_service_user_and_dirs() {
    say "Menyiapkan user ${SERVICE_USER} dan folder (izin sesuai kontrak)"
    if ! getent passwd "$SERVICE_USER" >/dev/null; then
        adduser --system --group --no-create-home --home "$DATA_DIR" --shell /usr/sbin/nologin "$SERVICE_USER"
    fi
    install -d -o root -g "$SERVICE_USER" -m 0750 "$CONF_DIR"
    install -d -o "$SERVICE_USER" -g "$SERVICE_USER" -m 0700 "$DATA_DIR"
}

grant_project_access() {
    say "Memberi ${SERVICE_USER} akses baca source/virtualenv (tanpa membuka .ssh)"
    local home
    home="$(getent passwd "$LAB_USER" | cut -d: -f6)"
    [ "$PROJECT_DIR" = "${home}/LogLab" ] || fail "repo harus berada di ${home}/LogLab sesuai kontrak (sekarang: ${PROJECT_DIR})"
    setfacl -m "u:${SERVICE_USER}:x" "$home"
    setfacl -m "u:${SERVICE_USER}:rx" "$PROJECT_DIR"
    setfacl -R -m "u:${SERVICE_USER}:rX" "${PROJECT_DIR}/src" "${PROJECT_DIR}/.venv" "${PROJECT_DIR}/config"
    runuser -u "$SERVICE_USER" -- "$PYTHON" -c 'import loglab.source_main' || fail "${SERVICE_USER} tidak dapat memuat aplikasi"
    if runuser -u "$SERVICE_USER" -- ls "${home}/.ssh" >/dev/null 2>&1; then
        fail "${SERVICE_USER} dapat membaca ${home}/.ssh; perbaiki izin sebelum melanjutkan"
    fi
}

ensure_env() {
    if [ -e "$ENV_FILE" ]; then
        say "Env sudah ada, tidak ditimpa: ${ENV_FILE}"
    else
        say "Membuat ${ENV_FILE} dari template (berisi placeholder)"
        install -m 0600 -o root -g root "${PROJECT_DIR}/config/source.example.env" "$ENV_FILE"
    fi
    chown root:root "$ENV_FILE"
    chmod 0600 "$ENV_FILE"
}

validate_env() {
    say "Memvalidasi env terhadap kontrak (nilai tidak ditampilkan)"
    if ! "$PYTHON" "${PROJECT_DIR}/scripts/check_contract.py" --role source --env "$ENV_FILE"; then
        cat >&2 <<MSG

Env belum valid. Isi dua nilai rahasia di ${ENV_FILE}, lalu jalankan setup lagi:
  LOGLAB_SOURCE_TOKEN  : 64 huruf hex, SAMA persis dengan milik Monitor (sepakati dengan Arhasya)
                         contoh membuat:  openssl rand -hex 32
  LOGLAB_PSEUDONYM_KEY : 64 huruf hex, HANYA ada di Source (jangan dibagikan ke Monitor)
                         contoh membuat:  openssl rand -hex 32
MSG
        exit 1
    fi
}

check_tls() {
    say "Memeriksa sertifikat TLS"
    local file
    for file in ca.crt tls.crt tls.key; do
        [ -s "${CONF_DIR}/${file}" ] || fail "${CONF_DIR}/${file} belum ada. Minta CA/sertifikat lab dari integrator (SAN harus IP ${SOURCE_IP})."
    done
    chown root:"$SERVICE_USER" "${CONF_DIR}/tls.key" "${CONF_DIR}/tls.crt" "${CONF_DIR}/ca.crt"
    chmod 0640 "${CONF_DIR}/tls.key"
    chmod 0644 "${CONF_DIR}/tls.crt" "${CONF_DIR}/ca.crt"
    openssl verify -CAfile "${CONF_DIR}/ca.crt" "${CONF_DIR}/tls.crt" >/dev/null || fail "tls.crt tidak diterbitkan oleh ca.crt"
    openssl x509 -in "${CONF_DIR}/tls.crt" -noout -ext subjectAltName | grep -q "IP Address:${SOURCE_IP}" \
        || fail "SAN sertifikat tidak memuat IP ${SOURCE_IP}"
    runuser -u "$SERVICE_USER" -- test -r "${CONF_DIR}/tls.key" || fail "${SERVICE_USER} tidak bisa membaca tls.key"
    if [ -e "${CONF_DIR}/ca.key" ]; then
        printf 'PERINGATAN: %s/ca.key ada di VM ini. Kontrak melarang private key CA di VM; pindahkan ke tempat privat.\n' "$CONF_DIR" >&2
    fi
}

seed_accounts() {
    if [ ! -s "$ACCOUNTS_FILE" ]; then
        printf 'BELUM SIAP: %s belum ada. Isi objek {"demo-user-01": "<password>", "demo-user-02": "<password>"} (password minimal 12 karakter, tidak masuk Git), lalu jalankan setup lagi.\n' "$ACCOUNTS_FILE" >&2
        exit 4
    fi
    chown root:root "$ACCOUNTS_FILE"
    chmod 0600 "$ACCOUNTS_FILE"
    say "Menyiapkan akun fiktif dari ${ACCOUNTS_FILE} (akun yang sudah ada tidak ditimpa)"
    # Berkas root-only disalurkan lewat stdin agar loglab-svc tidak perlu membacanya langsung.
    runuser -u "$SERVICE_USER" -- env "LOGLAB_DB_PATH=${DB_FILE}" "$PYTHON" -m loglab.seed_source_accounts --accounts-file - < "$ACCOUNTS_FILE" \
        || fail "seed akun gagal (isi berkas tidak ditampilkan)"
}

install_units() {
    say "Memasang service systemd"
    install -m 0644 -o root -g root "${HERE}/loglab-source.service" "${UNIT_DIR}/loglab-source.service"
    systemctl daemon-reload
}

install_firewall() {
    if [ "${LOGLAB_SKIP_FIREWALL:-0}" = "1" ]; then
        say "Firewall dilewati (LOGLAB_SKIP_FIREWALL=1)"
        return 0
    fi
    say "Memasang firewall (default-deny; hanya host)"
    nft -c -f "${HERE}/source.nft" || fail "sintaks source.nft ditolak nft; firewall lama tidak diubah"
    if [ -e /etc/nftables.conf ] && [ ! -e /etc/nftables.conf.pre-loglab ]; then
        cp -p /etc/nftables.conf /etc/nftables.conf.pre-loglab
    fi
    install -m 0644 -o root -g root "${HERE}/source.nft" /etc/nftables.conf
    systemctl enable nftables >/dev/null
    systemctl restart nftables
    printf 'CATATAN: SSH baru hanya diterima dari 172.16.202.1. Sesi yang sedang terbuka tetap hidup; console VMware selalu bisa dipakai untuk pemulihan.\n'
}

has_source_ip() {
    ip -4 -o addr show | grep -q " ${SOURCE_IP}/"
}

start_service() {
    systemctl enable loglab-source.service >/dev/null
    if ! has_source_ip; then
        printf 'BELUM SIAP: IP %s belum terpasang di VM ini. Atur adapter host-only (IP statis), lalu jalankan setup lagi.\n' "$SOURCE_IP" >&2
        exit 3
    fi
    say "Menjalankan loglab-source.service"
    systemctl restart loglab-source.service
}

health_check() {
    say "Menunggu /health lewat HTTPS dengan CA lab"
    for _ in $(seq 1 30); do
        if curl -fsS --cacert "${CONF_DIR}/ca.crt" "https://${SOURCE_IP}:${SOURCE_PORT}/health" 2>/dev/null | grep -q '"state":"ready"'; then
            say "SIAP: Source menjawab health. Ini baru bukti proses hidup, bukan bukti event sampai ke Monitor."
            return 0
        fi
        sleep 1
    done
    systemctl --no-pager --lines=15 status loglab-source.service >&2 || true
    fail "health check gagal setelah 30 detik; lihat: journalctl -u loglab-source.service -n 50"
}

main() {
    check_root
    check_os
    install_packages
    set_hostname
    ensure_service_user_and_dirs
    grant_project_access
    ensure_env
    validate_env
    check_tls
    seed_accounts
    install_units
    install_firewall
    start_service
    health_check
}

main "$@"
