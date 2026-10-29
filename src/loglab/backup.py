from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import tempfile
from pathlib import Path

from .db import backup_database


def create_atomic_backup(source: Path, destination: Path) -> dict[str, str | int]:
    source = source.resolve()
    destination = destination.resolve()
    if not source.is_file() or source == destination:
        raise ValueError("source database must exist and differ from destination")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    fd, temporary_name = tempfile.mkstemp(prefix=".loglab-backup-", suffix=".sqlite3", dir=destination.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        backup_database(source, temporary)
        os.chmod(temporary, 0o640)
        hasher = hashlib.sha256()
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        digest = hasher.hexdigest()
        size = temporary.stat().st_size
        os.replace(temporary, destination)
        directory_fd = os.open(destination.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return {"destination": str(destination), "bytes": size, "sha256": digest, "integrity": "ok"}
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an atomic, integrity-checked SQLite backup.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    result = create_atomic_backup(args.source, args.destination)
    print(f"backup_ok bytes={result['bytes']} sha256={result['sha256']} integrity={result['integrity']}")


if __name__ == "__main__":
    main()
