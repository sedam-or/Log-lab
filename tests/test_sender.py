"""Tes sender Source (E-04). Transport memakai ReceiverStub atau app Monitor asli (in-process).

ReceiverStub bukan Monitor asli; kelas TestSenderAgainstRealMonitor memakai monitor_app.create_app
lewat ASGI sehingga validasi/commit/receipt Monitor ikut diuji, tetapi TLS dan jaringan tidak.
"""
import asyncio
import json
import secrets
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

import httpx

from loglab import sender as sender_module
from loglab.config import Settings
from loglab.db import connect
from loglab.events import validate_source_status
from loglab.monitor_app import create_app as create_monitor_app
from loglab.security import hash_password
from loglab.sender import (STATUS_PATH, EVENTS_PATH, Sender, SenderLockError,
                           backoff_delay)
from loglab.source_service import SourceService
from loglab.testing import ReceiverStub

PASSWORD = "a-long-fictitious-password"


class FakeClock:
    def __init__(self, start=1_000_000.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class SenderTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.token = secrets.token_hex(32)
        self.settings = Settings.for_test("source", Path(tmp.name), source_token=self.token)
        self.service = SourceService(self.settings)
        self.stub = ReceiverStub(self.token)
        self.clock = FakeClock()
        self.posts = []

    def make_events(self, n):
        stored_hash = hash_password(PASSWORD)
        for _ in range(n):
            self.service.process_login("demo-user-01", PASSWORD, stored_hash)

    def sender(self, post=None, **kw):
        return Sender(self.settings, post or self.recording(self.stub.post), clock=self.clock,
                      rng=lambda: 0.0, **kw)

    def recording(self, inner):
        def post(path, payload, token):
            self.posts.append((path, json.loads(json.dumps(payload))))
            return inner(path, payload, token)
        return post

    def rows(self):
        with connect(self.settings.db_path) as db:
            return [dict(r) for r in db.execute("SELECT * FROM outbox ORDER BY sequence")]


class TestSenderDelivery(SenderTestCase):
    def test_e4_01_receipt_cocok_disimpan_sebagai_ack(self):
        self.make_events(1)
        result = self.sender().run_once()
        self.assertEqual(result, {"acked": 1, "retried": 0, "held": 0})
        row = self.rows()[0]
        self.assertEqual((row["state"], row["receipt_status"]), ("acked", "stored"))
        self.assertIsNotNone(row["acked_at"])
        self.assertEqual(len(self.stub.events), 1)

    def test_e4_02_receipt_salah_tidak_menjadi_ack(self):
        self.make_events(1)
        event_id = self.rows()[0]["event_id"]
        for broken in (
            lambda r: {**r, "event_digest": "0" * 64},
            lambda r: {**r, "event_id": "11111111-1111-4111-8111-111111111111"},
            lambda r: {**r, "source_id": "login-lab-b"},
            lambda r: {**r, "status": "accepted"},
            lambda r: {k: v for k, v in r.items() if k != "status"},
        ):
            def post(path, payload, token, broken=broken):
                code, body = self.stub.post(path, payload, token)
                return code, broken(body)
            self.sender(post).run_once()
            row = self.rows()[0]
            self.assertEqual(row["state"], "pending", "receipt salah tidak boleh menjadi ACK")
            self.assertEqual(row["last_error"], "receipt_mismatch")
            self.assertEqual(row["event_id"], event_id)
            self.clock.advance(60)

    def test_e4_03_timeout_429_5xx_diulang_dengan_identitas_sama(self):
        self.make_events(1)
        before = self.rows()[0]
        scripted = iter([TimeoutError("x"), (429, {"error": "rate_limited"}), (503, {"error": "service_unavailable"})])

        def post(path, payload, token):
            step = next(scripted, None)
            if step is None:
                return self.stub.post(path, payload, token)
            if isinstance(step, Exception):
                raise step
            return step

        sender = self.sender(self.recording(post))
        for expected_attempts, reason in ((1, "transport:TimeoutError"), (2, "http_429:rate_limited"), (3, "http_503:service_unavailable")):
            self.assertEqual(sender.run_once()["retried"], 1)
            row = self.rows()[0]
            self.assertEqual((row["state"], row["attempts"], row["last_error"]), ("pending", expected_attempts, reason))
            # belum jatuh tempo: tidak dikirim lagi
            self.assertEqual(sender.run_once(), {"acked": 0, "retried": 0, "held": 0})
            self.clock.advance(31)
        self.assertEqual(sender.run_once()["acked"], 1)
        after = self.rows()[0]
        self.assertEqual(after["payload_json"], before["payload_json"])
        self.assertEqual(after["event_id"], before["event_id"])
        self.assertEqual(len({json.dumps(p, sort_keys=True) for _, p in self.posts}), 1)
        self.assertEqual(len(self.stub.events), 1)

    def test_e4_04_receipt_hilang_lalu_duplicate_tidak_menambah_record(self):
        self.make_events(1)
        lost = {"first": True}

        def post(path, payload, token):
            code, body = self.stub.post(path, payload, token)  # Monitor menyimpan event
            if lost["first"]:
                lost["first"] = False
                raise TimeoutError("receipt hilang")
            return code, body

        sender = self.sender(post)
        self.assertEqual(sender.run_once()["retried"], 1)
        self.assertEqual(self.rows()[0]["state"], "pending")
        self.clock.advance(31)
        self.assertEqual(sender.run_once()["acked"], 1)
        row = self.rows()[0]
        self.assertEqual((row["state"], row["receipt_status"]), ("acked", "duplicate"))
        self.assertEqual(len(self.stub.events), 1)

    def test_e4_05_proses_berhenti_sebelum_dan_sesudah_ack(self):
        self.make_events(1)
        first = self.sender()
        with mock.patch.object(Sender, "_ack", side_effect=RuntimeError("crash sebelum commit ACK")):
            with self.assertRaises(RuntimeError):
                first.run_once()
        self.assertEqual(self.rows()[0]["state"], "pending")  # ACK belum ter-commit
        restarted = self.sender()  # proses baru membaca ulang dari database
        self.assertEqual(restarted.run_once()["acked"], 1)
        self.assertEqual(self.rows()[0]["receipt_status"], "duplicate")
        self.assertEqual(len(self.stub.events), 1)
        sent = len(self.posts)
        self.assertEqual(self.sender().run_once(), {"acked": 0, "retried": 0, "held": 0})
        self.assertEqual(len(self.posts), sent, "event yang sudah ACK tidak dikirim lagi")

    def test_response_permanen_menahan_event_dengan_alasan_aman(self):
        self.make_events(3)
        codes = {1: (409, {"error": "event_conflict"}), 2: (422, {"error": "invalid_event"}), 3: (401, {"error": "unauthorized"})}
        counter = {"n": 0}

        def post(path, payload, token):
            counter["n"] += 1
            return codes[counter["n"]]

        result = self.sender(post).run_once()
        self.assertEqual(result, {"acked": 0, "retried": 0, "held": 3})
        rows = self.rows()
        self.assertEqual([r["state"] for r in rows], ["held"] * 3)
        self.assertEqual([r["last_error"] for r in rows], ["http_409:event_conflict", "http_422:invalid_event", "http_401:unauthorized"])
        self.assertTrue(all(r["payload_json"] for r in rows), "event ditahan, bukan dihapus")
        self.clock.advance(3600)
        self.assertEqual(self.sender(post).run_once(), {"acked": 0, "retried": 0, "held": 0})
        self.assertNotIn(self.token, json.dumps(rows))

    def test_event_dikirim_berurut_dan_berhenti_pada_kegagalan_sementara(self):
        self.make_events(3)
        self.stub.available = False
        self.sender().run_once()
        self.assertEqual(len(self.posts), 1, "tidak menunggu timeout untuk tiap event")
        self.stub.available = True
        self.clock.advance(31)
        self.sender().run_once()
        sequences = [p["sequence"] for path, p in self.posts if path == EVENTS_PATH]
        self.assertEqual(sequences, [1, 1, 2, 3])
        self.assertEqual([r["state"] for r in self.rows()], ["acked"] * 3)


class TestBackoff(unittest.TestCase):
    def test_jadwal_backoff_dan_jitter(self):
        self.assertEqual([backoff_delay(n, rng=lambda: 0.0) for n in range(1, 9)], [1, 2, 4, 8, 16, 30, 30, 30])
        self.assertEqual(backoff_delay(3, rng=lambda: 1.0), 4 * 1.2)
        for _ in range(200):
            self.assertTrue(30 <= backoff_delay(9) <= 36)


class TestSourceStatus(SenderTestCase):
    def test_status_awal_dan_sepuluh_field(self):
        status = self.sender().build_status()
        validate_source_status(status)
        self.assertEqual(len(status), 10)
        self.assertEqual((status["committed_sequence"], status["acknowledged_sequence"]), (0, 0))

    def test_e4_06_watermark_kontigu_tidak_meloncat(self):
        self.make_events(3)
        codes = iter([None, (409, {"error": "event_conflict"}), None])

        def post(path, payload, token):
            step = next(codes)
            return self.stub.post(path, payload, token) if step is None else step

        self.sender(post).run_once()
        self.assertEqual([r["state"] for r in self.rows()], ["acked", "held", "acked"])
        status = self.sender().build_status()
        self.assertEqual(status["committed_sequence"], 3)
        self.assertEqual(status["acknowledged_sequence"], 1, "2 belum ACK, jadi watermark berhenti di 1")
        self.assertEqual((status["held_count"], status["pending_count"]), (1, 0))

    def test_semua_ack_watermark_sama_dengan_committed(self):
        self.make_events(2)
        sender = self.sender()
        sender.run_once()
        status = sender.build_status()
        self.assertEqual((status["committed_sequence"], status["acknowledged_sequence"], status["pending_count"]), (2, 2, 0))

    def test_heartbeat_terkirim_dan_gagal_tidak_mengubah_outbox(self):
        self.make_events(1)
        sender = self.sender()
        self.assertTrue(sender.send_heartbeat())
        self.assertEqual(len(self.stub.statuses), 1)
        self.assertEqual(self.posts[-1][0], STATUS_PATH)
        before = self.rows()
        self.stub.available = False
        self.assertFalse(sender.send_heartbeat())
        self.assertEqual(self.rows(), before)

    def test_counter_rejected_berasal_dari_enqueue_rejected(self):
        self.make_events(1)
        with mock.patch("loglab.source_service.OUTBOX_MAX_EVENTS", 1):
            ok, event = self.service.process_login("demo-user-01", PASSWORD, hash_password(PASSWORD))
        self.assertTrue(ok)
        self.assertIsNone(event, "outbox penuh: event baru ditolak, auth tetap berhasil")
        status = self.sender().build_status()
        self.assertEqual(status["rejected_count"], 1)
        self.assertEqual(status["offered_count"], status["accepted_local_count"] + status["rejected_count"])
        self.assertEqual(len(self.rows()), 1, "event lama tetap utuh")


class TestSenderLock(SenderTestCase):
    def test_hanya_satu_sender_aktif(self):
        first, second = self.sender(), self.sender()
        first.acquire_lock()
        try:
            with self.assertRaises(SenderLockError):
                second.acquire_lock()
        finally:
            first.release_lock()
        second.acquire_lock()  # lock dilepas -> sender lain boleh mengambil
        second.release_lock()

    def test_run_forever_tidak_berjalan_bila_lock_dipegang_lain(self):
        holder = self.sender()
        holder.acquire_lock()
        self.make_events(1)
        stop = threading.Event()
        try:
            self.sender().run_forever(stop)  # kembali segera tanpa mengirim
        finally:
            holder.release_lock()
        self.assertEqual(self.posts, [])

    def test_run_forever_mengirim_event_dan_heartbeat(self):
        self.make_events(2)
        stop = threading.Event()
        sender = Sender(self.settings, self.stub.post)
        with mock.patch.object(sender_module, "TICK_SECONDS", 0.01):
            thread = threading.Thread(target=sender.run_forever, args=(stop,))
            thread.start()
            deadline = time.time() + 5
            while time.time() < deadline and not (
                all(r["state"] == "acked" for r in self.rows()) and self.stub.statuses
            ):
                time.sleep(0.02)
            stop.set()
            thread.join(5)
        self.assertEqual([r["state"] for r in self.rows()], ["acked", "acked"])
        self.assertEqual(len(self.stub.statuses), 1)
        self.assertFalse(thread.is_alive())


class TestSenderAgainstRealMonitor(unittest.IsolatedAsyncioTestCase):
    """Source asli -> app Monitor asli (in-process). Menguji validasi, commit sebelum receipt, duplicate."""

    async def asyncSetUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.token = secrets.token_hex(32)
        self.source = Settings.for_test("source", Path(tmp.name), source_token=self.token)
        self.monitor = Settings.for_test("monitor", Path(tmp.name), source_token=self.token)
        self.service = SourceService(self.source)
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=create_monitor_app(self.monitor)), base_url="https://monitor.test"
        )
        self.addAsyncCleanup(self.client.aclose)
        loop = asyncio.get_running_loop()

        def post(path, payload, token):
            future = asyncio.run_coroutine_threadsafe(
                self.client.post(path, json=payload, headers={"Authorization": "Bearer " + token}), loop
            )
            response = future.result(10)
            return response.status_code, response.json()

        self.clock = FakeClock()
        self.sender = Sender(self.source, post, clock=self.clock, rng=lambda: 0.0)

    def monitor_count(self, table):
        with connect(self.monitor.db_path) as db:
            return db.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]

    async def test_event_sampai_ke_monitor_dan_heartbeat_tersimpan(self):
        stored_hash = hash_password(PASSWORD)
        for _ in range(3):
            self.service.process_login("demo-user-01", PASSWORD, stored_hash)
        result = await asyncio.to_thread(self.sender.run_once)
        self.assertEqual(result["acked"], 3)
        self.assertEqual(self.monitor_count("monitor_events"), 3)
        self.assertTrue(await asyncio.to_thread(self.sender.send_heartbeat))
        with connect(self.monitor.db_path) as db:
            row = db.execute("SELECT committed_sequence, acknowledged_sequence, pending_count FROM source_status").fetchone()
        self.assertEqual(tuple(row), (3, 3, 0))

    async def test_token_salah_ditahan_dan_event_tidak_tersimpan(self):
        self.service.process_login("demo-user-01", PASSWORD, hash_password(PASSWORD))
        wrong = Settings.for_test("source", Path(self.source.db_path).parent.parent, source_token=secrets.token_hex(32))
        # pakai DB Source yang sama, tetapi token berbeda dari Monitor
        object.__setattr__(wrong, "db_path", self.source.db_path)
        object.__setattr__(wrong, "sender_lock", self.source.sender_lock)
        loop = asyncio.get_running_loop()

        def post(path, payload, token):
            future = asyncio.run_coroutine_threadsafe(
                self.client.post(path, json=payload, headers={"Authorization": "Bearer " + token}), loop
            )
            response = future.result(10)
            return response.status_code, response.json()

        result = await asyncio.to_thread(Sender(wrong, post, clock=self.clock).run_once)
        self.assertEqual(result["held"], 1)
        self.assertEqual(self.monitor_count("monitor_events"), 0)
        with connect(self.source.db_path) as db:
            error = db.execute("SELECT last_error FROM outbox").fetchone()[0]
        self.assertEqual(error, "http_401:unauthorized")

    async def test_monitor_mati_lalu_pulih_tanpa_duplikat(self):
        stored_hash = hash_password(PASSWORD)
        for _ in range(2):
            self.service.process_login("demo-user-01", PASSWORD, stored_hash)
        original = self.sender._post
        down = {"on": True}

        def flaky(path, payload, token):
            if down["on"]:
                raise TimeoutError("monitor mati")
            return original(path, payload, token)

        self.sender._post = flaky
        self.assertEqual((await asyncio.to_thread(self.sender.run_once))["retried"], 1)
        self.assertEqual(self.monitor_count("monitor_events"), 0)
        down["on"] = False
        self.clock.advance(31)
        self.assertEqual((await asyncio.to_thread(self.sender.run_once))["acked"], 2)
        self.assertEqual(self.monitor_count("monitor_events"), 2)
        self.assertEqual((await asyncio.to_thread(self.sender.run_once))["acked"], 0)


if __name__ == "__main__":
    unittest.main()
