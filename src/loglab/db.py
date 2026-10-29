from __future__ import annotations

from contextlib import closing
import sqlite3
import uuid
from pathlib import Path

SOURCE_SCHEMA_VERSION = 1
MONITOR_SCHEMA_VERSION = 1


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc, tb):
        try:
            return super().__exit__(exc_type, exc, tb)
        finally:
            self.close()


def connect(path: Path | str) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    db = sqlite3.connect(path, timeout=5, isolation_level=None, factory=ClosingConnection)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout = 5000")
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA synchronous = FULL")
    return db


def initialize_source(path: Path | str) -> None:
    with connect(path) as db:
        if db.execute("PRAGMA user_version").fetchone()[0] > 1:
            raise sqlite3.DatabaseError("database schema is newer than this foundation")
        db.executescript("""
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS counters(key TEXT PRIMARY KEY, value INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS auth_accounts(
            username TEXT PRIMARY KEY COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
        );
        CREATE TABLE IF NOT EXISTS outbox(
            event_id TEXT PRIMARY KEY,
            stream_id TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            state TEXT NOT NULL CHECK(state IN ('pending','acked','held')),
            attempts INTEGER NOT NULL DEFAULT 0,
            next_attempt REAL NOT NULL DEFAULT 0,
            last_error TEXT,
            receipt_status TEXT,
            created_at TEXT NOT NULL,
            acked_at TEXT,
            UNIQUE(stream_id, sequence)
        );
        CREATE INDEX IF NOT EXISTS outbox_due ON outbox(state, next_attempt, sequence);
        """)
        db.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('stream_id', ?)", (str(uuid.uuid4()),))
        db.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('next_sequence','1')")
        for key in ("offered", "accepted_local", "enqueue_rejected", "request_rejected"):
            db.execute("INSERT OR IGNORE INTO counters(key,value) VALUES(?,0)", (key,))
        db.execute(f"PRAGMA user_version = {SOURCE_SCHEMA_VERSION}")


def initialize_monitor(path: Path | str) -> None:
    with connect(path) as db:
        if db.execute("PRAGMA user_version").fetchone()[0] > 1:
            raise sqlite3.DatabaseError("database schema is newer than this foundation")
        db.executescript("""
        CREATE TABLE IF NOT EXISTS monitor_events(
            source_id TEXT NOT NULL,
            stream_id TEXT NOT NULL,
            event_id TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            occurred_at TEXT NOT NULL,
            event_type TEXT NOT NULL,
            account_token TEXT NOT NULL,
            client_token TEXT NOT NULL,
            reason_code TEXT NOT NULL,
            event_digest TEXT NOT NULL,
            received_at TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            PRIMARY KEY(source_id, event_id),
            UNIQUE(source_id, stream_id, sequence)
        );
        CREATE INDEX IF NOT EXISTS events_time ON monitor_events(occurred_at DESC, event_id);
        CREATE INDEX IF NOT EXISTS events_account ON monitor_events(account_token, occurred_at DESC);
        CREATE INDEX IF NOT EXISTS events_client ON monitor_events(client_token, occurred_at DESC);
        CREATE INDEX IF NOT EXISTS events_type ON monitor_events(event_type, occurred_at DESC);
        CREATE INDEX IF NOT EXISTS events_source_received ON monitor_events(source_id, stream_id, received_at DESC);
        CREATE TABLE IF NOT EXISTS source_status(
            source_id TEXT NOT NULL,
            stream_id TEXT NOT NULL,
            committed_sequence INTEGER NOT NULL,
            acknowledged_sequence INTEGER NOT NULL,
            pending_count INTEGER NOT NULL,
            held_count INTEGER NOT NULL,
            rejected_count INTEGER NOT NULL,
            offered_count INTEGER NOT NULL,
            accepted_local_count INTEGER NOT NULL,
            source_time TEXT NOT NULL,
            received_at TEXT NOT NULL,
            clock_offset_ms INTEGER NOT NULL,
            PRIMARY KEY(source_id, stream_id)
        );
        CREATE TABLE IF NOT EXISTS ingest_rejections(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at TEXT NOT NULL,
            source_id TEXT,
            reason_code TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS snapshots(
            snapshot_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            stream_id TEXT NOT NULL,
            client_token TEXT NOT NULL,
            window_start TEXT NOT NULL,
            window_end TEXT NOT NULL,
            revision INTEGER NOT NULL,
            input_hash TEXT NOT NULL,
            quality TEXT NOT NULL,
            quality_reason TEXT NOT NULL,
            features_json TEXT NOT NULL,
            membership_json TEXT NOT NULL,
            sealed_at TEXT NOT NULL,
            PRIMARY KEY(snapshot_id, revision),
            UNIQUE(source_id, stream_id, client_token, window_start, revision)
        );
        CREATE INDEX IF NOT EXISTS snapshot_latest ON snapshots(window_end DESC, revision DESC);
        CREATE TABLE IF NOT EXISTS analysis_results(
            snapshot_id TEXT NOT NULL,
            revision INTEGER NOT NULL,
            model_hash TEXT NOT NULL,
            result_kind TEXT NOT NULL,
            state TEXT NOT NULL,
            label TEXT,
            score REAL,
            reason TEXT NOT NULL,
            evidence_json TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(snapshot_id, revision, model_hash, result_kind),
            FOREIGN KEY(snapshot_id, revision) REFERENCES snapshots(snapshot_id, revision)
        );
        CREATE TABLE IF NOT EXISTS operators(
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
        );
        CREATE TABLE IF NOT EXISTS sessions(
            token_hash TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            csrf_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS session_expiry ON sessions(expires_at);
        """)
        db.execute("CREATE INDEX IF NOT EXISTS snapshot_latest ON snapshots(window_end DESC, revision DESC)")
        db.execute(f"PRAGMA user_version = {MONITOR_SCHEMA_VERSION}")


def backup_database(source: Path | str, destination: Path | str) -> None:
    """Create a transactionally consistent SQLite backup."""
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file() or source == destination:
        raise ValueError("source must exist and differ from backup destination")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(source.as_uri()+"?mode=ro", uri=True)) as src, closing(sqlite3.connect(destination)) as dst:
        src.backup(dst)
        result = dst.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise sqlite3.DatabaseError(f"backup integrity check failed: {result}")
