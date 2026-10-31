import json
import re
import tempfile
import unittest
from pathlib import Path

from loglab.config import Settings
from loglab.db import connect
from loglab.security import hash_password
from loglab.source_service import SourceService

PASSWORD = "a-long-fictitious-password"


def make_app(tmp_dir):
    settings = Settings.for_test("source", Path(tmp_dir))
    return settings, SourceService(settings)


class TestErnaOutbox(unittest.TestCase):
    def test_login_success_creates_outbox_event(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings, app = make_app(tmp_dir)
            hashed = hash_password(PASSWORD)

            success, event = app.process_login("user_erna", PASSWORD, hashed)
            self.assertTrue(success)
            self.assertEqual(event["event_type"], "login.success")
            self.assertEqual(event["reason_code"], "SUCCESS")
            self.assertEqual(event["sequence"], 1)

            with connect(settings.db_path) as conn:
                row = conn.execute(
                    "SELECT * FROM outbox WHERE event_id = ?", (event["event_id"],)
                ).fetchone()
                self.assertIsNotNone(row)
                self.assertEqual(row["state"], "pending")
                payload = json.loads(row["payload_json"])
                self.assertEqual(payload, event)

    def test_login_failure_creates_outbox_event(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings, app = make_app(tmp_dir)
            hashed = hash_password(PASSWORD)

            success, event = app.process_login("user_erna", "wrong-password-123", hashed)
            self.assertFalse(success)
            self.assertEqual(event["event_type"], "login.failure")
            self.assertEqual(event["reason_code"], "INVALID_CREDENTIALS")

            with connect(settings.db_path) as conn:
                row = conn.execute(
                    "SELECT * FROM outbox WHERE event_id = ?", (event["event_id"],)
                ).fetchone()
                self.assertIsNotNone(row)
                self.assertEqual(row["state"], "pending")

    def test_event_has_no_secret_or_real_name(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            _, app = make_app(tmp_dir)
            hashed = hash_password(PASSWORD)
            _, event = app.process_login("user_erna", PASSWORD, hashed)

            text = json.dumps(event)
            self.assertNotIn("user_erna", text)
            self.assertNotIn(PASSWORD, text)
            self.assertRegex(event["account_token"], r"^[0-9a-f]{64}$")
            self.assertRegex(event["client_token"], r"^[0-9a-f]{64}$")

    def test_sequence_and_counters(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings, app = make_app(tmp_dir)
            hashed = hash_password(PASSWORD)

            _, e1 = app.process_login("user_erna", PASSWORD, hashed)
            _, e2 = app.process_login("user_erna", "wrong-password-123", hashed)
            self.assertEqual([e1["sequence"], e2["sequence"]], [1, 2])

            with connect(settings.db_path) as conn:
                counters = {
                    r["key"]: r["value"]
                    for r in conn.execute("SELECT key, value FROM counters")
                }
            self.assertEqual(counters["offered"], 2)
            self.assertEqual(counters["accepted_local"], 2)
            self.assertEqual(counters["enqueue_rejected"], 0)


if __name__ == "__main__":
    unittest.main()
