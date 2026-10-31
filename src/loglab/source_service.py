import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from loglab.config import Settings
from loglab.db import connect, initialize_source
from loglab.events import build_event, validate_event
from loglab.security import pseudonym, verify_password


class SourceService:
    def __init__(self, settings: Settings):
        self.settings = settings
        initialize_source(self.settings.db_path)

    def process_login(
        self,
        username: str,
        password_attempt: str,
        stored_hash: str,
        client_id: str = "client-uji-1",
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Putuskan hasil auth, lalu simpan event ke outbox dalam satu transaksi.

        Hasil auth tidak berubah walau penyimpanan gagal (EP-02).
        Jika enqueue gagal, event = None dan counter enqueue_rejected naik.
        """
        is_success = verify_password(password_attempt, stored_hash)
        key = self.settings.pseudonym_key
        if key is None:
            raise RuntimeError("pseudonym_key belum diatur untuk source")

        try:
            with connect(self.settings.db_path) as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    stream_id = conn.execute(
                        "SELECT value FROM meta WHERE key='stream_id'"
                    ).fetchone()[0]
                    sequence = int(
                        conn.execute(
                            "SELECT value FROM meta WHERE key='next_sequence'"
                        ).fetchone()[0]
                    )
                    event = build_event(
                        source_id=self.settings.source_id,
                        stream_id=stream_id,
                        sequence=sequence,
                        occurred_at=datetime.now(timezone.utc).strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        event_type="login.success" if is_success else "login.failure",
                        account_token=pseudonym(key, "account", username),
                        client_token=pseudonym(key, "client", client_id),
                        reason_code="SUCCESS" if is_success else "INVALID_CREDENTIALS",
                    )
                    validate_event(event)
                    conn.execute(
                        "INSERT INTO outbox "
                        "(event_id, stream_id, sequence, payload_json, state, created_at) "
                        "VALUES (?, ?, ?, ?, 'pending', ?)",
                        (
                            event["event_id"],
                            stream_id,
                            sequence,
                            json.dumps(event, sort_keys=True, separators=(",", ":")),
                            event["occurred_at"],
                        ),
                    )
                    conn.execute(
                        "UPDATE meta SET value=? WHERE key='next_sequence'",
                        (str(sequence + 1),),
                    )
                    conn.execute(
                        "UPDATE counters SET value = value + 1 WHERE key='offered'"
                    )
                    conn.execute(
                        "UPDATE counters SET value = value + 1 WHERE key='accepted_local'"
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
        except sqlite3.Error:
            self._count_enqueue_rejected()
            return is_success, None

        return is_success, event

    def _count_enqueue_rejected(self) -> None:
        try:
            with connect(self.settings.db_path) as conn:
                conn.execute("UPDATE counters SET value = value + 1 WHERE key='offered'")
                conn.execute(
                    "UPDATE counters SET value = value + 1 WHERE key='enqueue_rejected'"
                )
                conn.commit()
        except sqlite3.Error:
            pass
