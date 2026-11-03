"""Buat bundle konfigurasi lab di folder privat DI LUAR Git (jalankan di host, bukan di VM).

Isi bundle (semua nilai dibuat acak; tidak ada yang berasal dari repo):
  ca.crt                      CA lab (publik); private key CA dibuang setelah menandatangani
  source/source.env           env Source (token + pseudonym key)
  source/tls.crt, tls.key     sertifikat Source (SAN IP 172.16.202.21)
  source/test-accounts.json   akun fiktif demo-user-01/02
  monitor/monitor.env         env Monitor (token yang SAMA, hash password operator)
  monitor/tls.crt, tls.key    sertifikat Monitor (SAN IP 172.16.202.22)
  KREDENSIAL-PRIVAT.txt       password operator dan akun demo (satu-satunya tempat password asli)

Salin source/ + ca.crt ke VM A dan monitor/ + ca.crt ke VM B; setup.sh memasangnya.
Perintah menolak folder yang sudah berisi sesuatu agar secret lama tidak tertimpa.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from loglab.contract import (ContractError, check_ca_pair, load_contract, parse_env,  # noqa: E402
                             render_env, validate_pair)
from loglab.security import hash_password  # noqa: E402

CA_DAYS = 365
CERT_DAYS = 365


def _openssl(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(["openssl", *args], check=True, capture_output=True, cwd=cwd)


def _make_ca(out: Path) -> Path:
    key = out / "ca.key"
    _openssl("ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", str(key))
    _openssl("req", "-x509", "-new", "-key", str(key), "-sha256", "-days", str(CA_DAYS),
             "-subj", "/CN=LogLab Lab CA", "-addext", "basicConstraints=critical,CA:TRUE",
             "-addext", "keyUsage=critical,keyCertSign,cRLSign", "-out", str(out / "ca.crt"))
    return key


def _make_leaf(directory: Path, ca_dir: Path, ca_key: Path, common_name: str, ip: str) -> None:
    key, csr, crt, ext = (directory / "tls.key", directory / "tls.csr", directory / "tls.crt", directory / "ext.cnf")
    _openssl("ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", str(key))
    _openssl("req", "-new", "-key", str(key), "-subj", f"/CN={common_name}", "-out", str(csr))
    ext.write_text(f"subjectAltName=IP:{ip}\nbasicConstraints=critical,CA:FALSE\n"
                   "keyUsage=critical,digitalSignature\nextendedKeyUsage=serverAuth\n", encoding="utf-8")
    _openssl("x509", "-req", "-in", str(csr), "-CA", str(ca_dir / "ca.crt"), "-CAkey", str(ca_key),
             "-CAcreateserial", "-days", str(CERT_DAYS), "-sha256", "-extfile", str(ext), "-out", str(crt),
             cwd=directory)
    for leftover in (csr, ext, directory / "ca.srl"):
        leftover.unlink(missing_ok=True)
    _openssl("verify", "-CAfile", str(ca_dir / "ca.crt"), str(crt))


def _fill(template: str, **values: str) -> str:
    lines = []
    for line in template.splitlines():
        key, sep, _ = line.partition("=")
        lines.append(f"{key}={values[key]}" if sep and key in values else line)
    return "\n".join(lines) + "\n"


def build(out: Path) -> list[str]:
    if shutil.which("openssl") is None:
        raise SystemExit("openssl tidak ditemukan")
    contract = load_contract()
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"GAGAL: {out} tidak kosong; tidak menimpa bundle yang ada.")
    out.mkdir(parents=True, exist_ok=True)
    os.chmod(out, 0o700)
    os.umask(0o077)

    roles = contract["roles"]
    token, pseudonym_key = secrets.token_hex(32), secrets.token_hex(32)
    operator_password = secrets.token_urlsafe(18)
    demo = {name: secrets.token_urlsafe(18) for name in roles["source"]["demo_usernames"]}

    (out / "source").mkdir()
    (out / "monitor").mkdir()
    with tempfile.TemporaryDirectory() as scratch_name:  # private key CA hanya hidup selama pembuatan
        scratch = Path(scratch_name)
        ca_key = _make_ca(scratch)
        shutil.copy2(scratch / "ca.crt", out / "ca.crt")
        _make_leaf(out / "source", scratch, ca_key, "loglab-source", roles["source"]["ip"])
        _make_leaf(out / "monitor", scratch, ca_key, "loglab-monitor", roles["monitor"]["ip"])

    (out / "source" / "source.env").write_text(
        _fill(render_env(contract, "source"), LOGLAB_SOURCE_TOKEN=token, LOGLAB_PSEUDONYM_KEY=pseudonym_key),
        encoding="utf-8")
    (out / "monitor" / "monitor.env").write_text(
        _fill(render_env(contract, "monitor"), LOGLAB_SOURCE_TOKEN=token,
              LOGLAB_OPERATOR_PASSWORD_HASH=hash_password(operator_password)), encoding="utf-8")
    (out / "source" / "test-accounts.json").write_text(json.dumps(demo, indent=2) + "\n", encoding="utf-8")
    (out / "KREDENSIAL-PRIVAT.txt").write_text(
        "PRIVAT. Jangan masuk Git, chat, atau laporan.\n"
        f"operator ({roles['monitor']['ip']}): {contract_operator(contract)} / {operator_password}\n"
        + "".join(f"{name}: {password}\n" for name, password in demo.items()), encoding="utf-8")

    for path in out.rglob("*"):
        os.chmod(path, 0o700 if path.is_dir() else 0o600)

    # Pemeriksaan sebelum bundle diserahkan: env pasangan cocok dan CA identik.
    validate_pair(contract, parse_env(out / "source" / "source.env"), parse_env(out / "monitor" / "monitor.env"))
    check_ca_pair(out / "ca.crt", out / "ca.crt")
    return sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())


def contract_operator(contract: dict) -> str:
    values = contract["roles"]["monitor"].get("operator_username")
    if isinstance(values, str):
        return values
    return "operator"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, required=True, help="folder tujuan (harus kosong/belum ada, di luar repo)")
    args = parser.parse_args(argv)
    out = args.out.expanduser().resolve()
    repo = Path(__file__).resolve().parents[1]
    if out == repo or repo in out.parents:
        print("GAGAL: bundle harus berada di luar repo Git.", file=sys.stderr)
        return 2
    try:
        files = build(out)
    except (ContractError, subprocess.CalledProcessError) as exc:
        print(f"GAGAL: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(f"Bundle dibuat di {out} ({len(files)} berkas):")
    for name in files:
        print("  " + name)
    print("Password asli hanya ada di KREDENSIAL-PRIVAT.txt. Salin source/ dan ca.crt ke VM A, monitor/ dan ca.crt ke VM B.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
