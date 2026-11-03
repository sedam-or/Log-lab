"""Sender Source: kirim outbox ke Monitor, validasi receipt, retry, dan heartbeat status (E-04).

Aturan (SRS event-pipeline EP-03, EP-06, EP-07):
- Event dikirim berurut sequence dengan identitas dan payload yang sama pada setiap retry.
- ACK lokal hanya setelah receipt cocok (source_id, event_id, event_digest) dan commit lokal berhasil.
- Timeout, jaringan, 429 dan 5xx dicoba ulang dengan backoff 1, 2, 4 ... 30 detik (jitter 0-20%).
- 400/401/409/413/422 (dan 4xx lain) menahan event (`held`) dengan alasan aman; tidak dihapus.
- Heartbeat setiap 5 detik berisi sepuluh field; watermark ACK adalah sequence tertinggi yang
  seluruh pendahulunya sudah ACK (kontigu).
- Hanya satu sender aktif untuk satu database: file lock pada `LOGLAB_SENDER_LOCK`.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import logging
import random
import threading
import time
from pathlib import Path
from typing import Any, Callable

import httpx

from .config import Settings
from .db import connect
from .events import canonical_json, utc_now, validate_receipt, validate_source_status

EVENTS_PATH = "/api/v1/events"
STATUS_PATH = "/api/v1/source-status"
REQUEST_TIMEOUT_SECONDS = 3.0
BACKOFF_BASE_SECONDS = 1.0
BACKOFF_MAX_SECONDS = 30.0
JITTER_MAX = 0.20
HEARTBEAT_SECONDS = 5.0
BATCH_LIMIT = 50
TICK_SECONDS = 0.5

PERMANENT_STATUSES = frozenset({400, 401, 409, 413, 422})
log = logging.getLogger("loglab.sender")

Post = Callable[[str, dict, str], "tuple[int, Any]"]


class HttpPost:
    """Transport HTTPS ke Monitor: bearer token, CA lab, timeout 3 detik."""

    def __init__(self, settings: Settings):
        self._token = settings.source_token
        self._client = httpx.Client(
            base_url=settings.monitor_url,
            verify=str(settings.ca_bundle),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    def __call__(self, path: str, payload: dict, source_token: str) -> tuple[int, Any]:
        response = self._client.post(
            path,
            content=canonical_json(payload),
            headers={
                "Authorization": "Bearer " + source_token,
                "Content-Type": "application/json",
            },
        )
        try:
            body: Any = response.json()
        except ValueError:
            body = {}
        return response.status_code, body

    def close(self) -> None:
        self._client.close()


def backoff_delay(attempts: int, rng: Callable[[], float] = random.random) -> float:
    """Jeda sebelum percobaan berikutnya: 1, 2, 4 ... 30 detik ditambah jitter 0-20%."""
    base = min(BACKOFF_MAX_SECONDS, BACKOFF_BASE_SECONDS * (2 ** max(0, attempts - 1)))
    return base * (1.0 + JITTER_MAX * rng())


class SenderLockError(RuntimeError):
    """Sender lain sudah memegang lock untuk database ini."""


class Sender:
    def __init__(
        self,
        settings: Settings,
        post: Post | None = None,
        *,
        clock: Callable[[], float] = time.time,
        rng: Callable[[], float] = random.random,
    ):
        if settings.role != "source":
            raise ValueError("Sender hanya untuk peran source")
        self.settings = settings
        self._post = post
        self._clock = clock
        self._rng = rng
        self._lock_file = None

    # ---- lock: satu sender per database ----
    def acquire_lock(self) -> None:
        if self._lock_file is not None:
            return
        path = Path(self.settings.sender_lock)
        path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(path, "a+")
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            handle.close()
            raise SenderLockError("sender lain sudah berjalan") from exc
        self._lock_file = handle

    def release_lock(self) -> None:
        if self._lock_file is not None:
            with contextlib.suppress(OSError):
                fcntl.flock(self._lock_file, fcntl.LOCK_UN)
            self._lock_file.close()
            self._lock_file = None

    def _transport(self) -> Post:
        if self._post is None:
            self._post = HttpPost(self.settings)
        return self._post

    # ---- pengiriman event ----
    def run_once(self, limit: int = BATCH_LIMIT) -> dict[str, int]:
        """Kirim event pending yang sudah jatuh tempo. Berhenti pada kegagalan sementara pertama
        agar urutan sequence terjaga dan Monitor yang mati tidak membuat tiap event menunggu timeout."""
        result = {"acked": 0, "retried": 0, "held": 0}
        now = self._clock()
        with connect(self.settings.db_path) as db:
            rows = db.execute(
                "SELECT event_id, payload_json, attempts FROM outbox "
                "WHERE state='pending' AND next_attempt <= ? ORDER BY sequence LIMIT ?",
                (now, limit),
            ).fetchall()
        for row in rows:
            outcome = self._deliver(row["event_id"], row["payload_json"], row["attempts"])
            result[outcome] += 1
            if outcome == "retried":
                break
        return result

    def _deliver(self, event_id: str, payload_json: str, attempts: int) -> str:
        event = json.loads(payload_json)
        try:
            status, body = self._transport()(EVENTS_PATH, event, self.settings.source_token)
        except (TimeoutError, OSError, httpx.TransportError) as exc:
            self._schedule_retry(event_id, attempts, "transport:" + type(exc).__name__)
            return "retried"
        if status == 200:
            try:
                validate_receipt(body, event)
            except ValueError:
                # Receipt tidak cocok: event belum selesai. Coba lagi; jangan di-ACK.
                self._schedule_retry(event_id, attempts, "receipt_mismatch")
                return "retried"
            self._ack(event_id, body["status"])
            return "acked"
        code = body.get("error") if isinstance(body, dict) and isinstance(body.get("error"), str) else ""
        reason = f"http_{status}" + (f":{code[:40]}" if code else "")
        if status == 429 or 500 <= status <= 599:
            self._schedule_retry(event_id, attempts, reason)
            return "retried"
        # 400/401/409/413/422 dan 4xx lain: permanen. Tahan, jangan hapus.
        self._hold(event_id, attempts, reason)
        return "held"

    def _ack(self, event_id: str, receipt_status: str) -> None:
        with connect(self.settings.db_path) as db:
            db.execute(
                "UPDATE outbox SET state='acked', receipt_status=?, acked_at=?, "
                "attempts=attempts+1, last_error=NULL WHERE event_id=? AND state='pending'",
                (receipt_status, utc_now(), event_id),
            )

    def _schedule_retry(self, event_id: str, attempts: int, reason: str) -> None:
        attempts += 1
        due = self._clock() + backoff_delay(attempts, self._rng)
        with connect(self.settings.db_path) as db:
            db.execute(
                "UPDATE outbox SET attempts=?, next_attempt=?, last_error=? "
                "WHERE event_id=? AND state='pending'",
                (attempts, due, reason, event_id),
            )

    def _hold(self, event_id: str, attempts: int, reason: str) -> None:
        with connect(self.settings.db_path) as db:
            db.execute(
                "UPDATE outbox SET state='held', attempts=?, last_error=? "
                "WHERE event_id=? AND state='pending'",
                (attempts + 1, reason, event_id),
            )

    # ---- status / heartbeat ----
    def build_status(self) -> dict[str, Any]:
        with connect(self.settings.db_path) as db:
            meta = {r["key"]: r["value"] for r in db.execute("SELECT key, value FROM meta")}
            counters = {r["key"]: r["value"] for r in db.execute("SELECT key, value FROM counters")}
            committed = int(meta["next_sequence"]) - 1
            first_unacked = db.execute(
                "SELECT MIN(sequence) FROM outbox WHERE state != 'acked'"
            ).fetchone()[0]
            counts = {
                r["state"]: r["n"]
                for r in db.execute("SELECT state, COUNT(*) AS n FROM outbox GROUP BY state")
            }
        acknowledged = committed if first_unacked is None else first_unacked - 1
        status = {
            "source_id": self.settings.source_id,
            "stream_id": meta["stream_id"],
            "committed_sequence": committed,
            "acknowledged_sequence": acknowledged,
            "pending_count": counts.get("pending", 0),
            "held_count": counts.get("held", 0),
            "rejected_count": counters.get("enqueue_rejected", 0),
            "offered_count": counters.get("offered", 0),
            "accepted_local_count": counters.get("accepted_local", 0),
            "source_time": utc_now(),
        }
        validate_source_status(status)
        return status

    def send_heartbeat(self) -> bool:
        """Kirim status; kegagalan jaringan tidak mengubah outbox dan dicoba lagi pada heartbeat berikut."""
        try:
            status, _body = self._transport()(STATUS_PATH, self.build_status(), self.settings.source_token)
        except (TimeoutError, OSError, httpx.TransportError):
            return False
        return status == 200

    # ---- loop ----
    def run_forever(self, stop: threading.Event) -> None:
        try:
            self.acquire_lock()
        except SenderLockError:
            log.error("sender tidak dijalankan: lock %s sudah dipegang proses lain", self.settings.sender_lock)
            return
        next_heartbeat = 0.0
        try:
            while not stop.is_set():
                try:
                    self.run_once()
                    if self._clock() >= next_heartbeat:
                        self.send_heartbeat()
                        next_heartbeat = self._clock() + HEARTBEAT_SECONDS
                except Exception as exc:  # satu siklus gagal tidak boleh mematikan login
                    log.warning("siklus sender gagal: %s", type(exc).__name__)
                stop.wait(TICK_SECONDS)
        finally:
            self.release_lock()


def sender_lifespan(sender: Sender):
    """Lifespan FastAPI: jalankan sender di thread latar belakang selama aplikasi hidup."""

    @contextlib.asynccontextmanager
    async def lifespan(_app):
        stop = threading.Event()
        thread = threading.Thread(
            target=sender.run_forever, args=(stop,), name="loglab-sender", daemon=True
        )
        thread.start()
        try:
            yield
        finally:
            stop.set()
            thread.join(timeout=5)

    return lifespan
