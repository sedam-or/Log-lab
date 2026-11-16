#!/usr/bin/env bash
# Menyiapkan folder privat untuk uji container lokal (Modul 7). HANYA UNTUK LAB.
# Semua secret dibuat acak di sini dan tidak pernah masuk Git atau laporan. Pakai:
#   bash deployment/container/make-private.sh /folder/kosong
# Output: source.env, monitor.env, tls-source/, tls-monitor/, test-accounts.json,
# operator-password.txt (chmod 600). CA privat dibuat sementara lalu dihapus.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${1:?pakai: make-private.sh FOLDER_KOSONG}"

if [[ -d "$OUT" && -n "$(ls -A "$OUT" 2>/dev/null)" ]]; then
  echo "Folder harus kosong: $OUT" >&2
  exit 2
fi

umask 077
mkdir -p "$OUT/tls-source" "$OUT/tls-monitor"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# CA lab sementara (kunci CA tidak disimpan di folder privat).
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes \
  -keyout "$WORK/ca.key" -out "$OUT/ca.crt" -days 30 -subj "/CN=LogLab lab CA (uji)" \
  -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign" -addext "subjectKeyIdentifier=hash" 2>/dev/null

# Sertifikat per peran dengan SAN IP sesuai kontrak (.21 Source, .22 Monitor).
issue() {
  local role="$1" ip="$2" dir="$OUT/tls-$1"
  cp "$OUT/ca.crt" "$dir/ca.crt"
  openssl req -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes \
    -keyout "$dir/tls.key" -out "$WORK/$role.csr" -subj "/CN=loglab-$role" 2>/dev/null
  printf 'subjectAltName=IP:%s\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature\nextendedKeyUsage=serverAuth\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n' "$ip" > "$WORK/$role.ext"
  openssl x509 -req -in "$WORK/$role.csr" -CA "$OUT/ca.crt" -CAkey "$WORK/ca.key" -CAcreateserial \
    -days 30 -extfile "$WORK/$role.ext" -out "$dir/tls.crt" 2>/dev/null
  # UID container (10001) berbeda dengan UID pemilik di host; kunci uji lab dibuat terbaca.
  # Di VM, kunci dimiliki root:loglab-svc dengan izin 0640 (lihat deployment/source/setup.sh).
  chmod 0755 "$dir"
  chmod 0644 "$dir/tls.key" "$dir/tls.crt" "$dir/ca.crt"
}
issue source 172.16.202.21
issue monitor 172.16.202.22
rm -f "$OUT/ca.crt" "$OUT/ca.srl"

# Secret acak. Nilai tidak dicetak ke layar.
TOKEN="$(openssl rand -hex 32)"
PSEUDO="$(openssl rand -hex 32)"
OP_PASS="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-24)"
printf '%s\n' "$OP_PASS" > "$OUT/operator-password.txt"

HASH="$(PYTHONPATH="$ROOT/src" python3 -c 'import sys; from loglab.security import hash_password; print(hash_password(sys.argv[1]))' "$OP_PASS")"

sed -e "s|__SET_ONCE_PER_LAB__|$TOKEN|" -e "s|__GENERATE_SOURCE_ONLY__|$PSEUDO|" \
  "$ROOT/config/source.example.env" > "$OUT/source.env"
# Compose menginterpolasi `$` di env_file; setiap `$` pada hash ditulis `$$` (Compose mengembalikannya ke `$`).
HASH_ESCAPED="${HASH//\$/'$$'}"
sed -e "s|__SET_ONCE_PER_LAB__|$TOKEN|" -e "s|__HASH_OPERATOR_PASSWORD__|$HASH_ESCAPED|" \
  "$ROOT/config/monitor.example.env" > "$OUT/monitor.env"
chmod 0600 "$OUT"/*.env "$OUT/operator-password.txt"

# Dua akun fiktif untuk uji login (kontrak: demo-user-01/02).
PYTHON_ACCOUNTS_OUT="$OUT/test-accounts.json" python3 - <<'PY'
import json, os, pathlib, secrets
accounts = {name: secrets.token_urlsafe(18) for name in ("demo-user-01", "demo-user-02")}
path = pathlib.Path(os.environ["PYTHON_ACCOUNTS_OUT"])
path.write_text(json.dumps(accounts), encoding="utf-8")
path.chmod(0o600)
PY

echo "OK: folder privat dibuat di $OUT (env, TLS lab, akun uji). Tidak ada nilai yang dicetak."
