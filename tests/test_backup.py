import sqlite3
import tempfile
import unittest
from pathlib import Path

from loglab.backup import create_atomic_backup
from loglab.db import connect


class BackupTests(unittest.TestCase):
    def test_backup_is_atomic_and_integrity_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.sqlite3"
            destination = root / "backup.sqlite3"
            with connect(source) as db:
                db.execute("CREATE TABLE evidence(value TEXT NOT NULL)")
                db.execute("INSERT INTO evidence VALUES('committed')")
            result = create_atomic_backup(source, destination)
            self.assertEqual(result["integrity"], "ok")
            self.assertEqual(destination.stat().st_mode & 0o777, 0o640)
            with connect(destination) as db:
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(db.execute("SELECT value FROM evidence").fetchone()[0], "committed")


if __name__ == "__main__":
    unittest.main()
