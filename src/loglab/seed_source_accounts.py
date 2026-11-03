"""Menyiapkan akun fiktif Source. Aman dijalankan berulang (E3-05).

Daftar akun dibaca dari `test-accounts.json` (kontrak: /etc/loglab/test-accounts.json, tidak
dikomit), berisi objek {"demo-user-01": "<password>", "demo-user-02": "<password>", ...}.
Berkas boleh dibaca dari path atau dari stdin (`-`) agar root dapat menyalurkannya ke akun
layanan tanpa melonggarkan izin berkas. Akun yang sudah ada tidak ditimpa.
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict

from loglab.db import connect, initialize_source
from loglab.security import hash_password

REQUIRED_USERNAMES = ("demo-user-01", "demo-user-02")
MIN_PASSWORD_LENGTH = 12


def seed_accounts(db_path, accounts: Dict[str, str]) -> int:
    """Tambah akun yang belum ada. Mengembalikan jumlah akun baru."""
    for username, password in accounts.items():
        if not username:
            raise ValueError("username tidak boleh kosong")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"password minimal {MIN_PASSWORD_LENGTH} karakter untuk '{username}'"
            )
    initialize_source(db_path)
    added = 0
    with connect(db_path) as conn:
        for username, password in accounts.items():
            exists = conn.execute(
                "SELECT 1 FROM auth_accounts WHERE username = ?", (username,)
            ).fetchone()
            if exists:
                continue
            conn.execute(
                "INSERT INTO auth_accounts (username, password_hash, active) "
                "VALUES (?, ?, 1)",
                (username, hash_password(password)),
            )
            added += 1
        conn.commit()
    return added


def parse_accounts(text: str) -> Dict[str, str]:
    """Baca isi test-accounts.json; tolak bentuk salah tanpa mencetak password."""
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise ValueError("test-accounts.json bukan JSON yang valid") from exc
    if not isinstance(data, dict) or not data:
        raise ValueError("test-accounts.json harus objek {username: password}")
    for username, password in data.items():
        if not isinstance(username, str) or not isinstance(password, str):
            raise ValueError("username dan password harus berupa teks")
    missing = [name for name in REQUIRED_USERNAMES if name not in data]
    if missing:
        raise ValueError("akun wajib belum ada: " + ", ".join(missing))
    return data


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Seed akun fiktif Source")
    parser.add_argument(
        "--accounts-file",
        default="/etc/loglab/test-accounts.json",
        help="path test-accounts.json, atau '-' untuk membaca stdin",
    )
    args = parser.parse_args(argv)
    db_path = os.environ.get("LOGLAB_DB_PATH", "")
    if not db_path:
        print("LOGLAB_DB_PATH belum diatur", file=sys.stderr)
        return 2
    try:
        if args.accounts_file == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.accounts_file).read_text(encoding="utf-8")
        accounts = parse_accounts(text)
        added = seed_accounts(Path(db_path), accounts)
    except (OSError, ValueError) as exc:
        print(f"Seed gagal: {exc}", file=sys.stderr)
        return 2
    print(f"Akun baru ditambahkan: {added} dari {len(accounts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
