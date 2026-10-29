from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any

EVENT_FIELDS = (
    "schema_version", "source_id", "event_id", "stream_id", "sequence", "occurred_at",
    "event_type", "account_token", "client_token", "reason_code",
)
ALL_EVENT_FIELDS = frozenset((*EVENT_FIELDS, "event_digest"))
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("timestamp must be RFC 3339 UTC with Z suffix")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value):
        raise ValueError("timestamp must use RFC 3339 UTC")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("timestamp offset is not UTC")
    return parsed


def canonical_json(value: dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_event(*, source_id: str, stream_id: str, sequence: int, occurred_at: str,
                event_type: str, account_token: str, client_token: str,
                reason_code: str, event_id: str | None = None) -> dict[str, Any]:
    event = {
        "schema_version": 1,
        "source_id": source_id,
        "event_id": event_id or str(uuid.uuid4()),
        "stream_id": stream_id,
        "sequence": sequence,
        "occurred_at": occurred_at,
        "event_type": event_type,
        "account_token": account_token,
        "client_token": client_token,
        "reason_code": reason_code,
    }
    validate_event(event, require_digest=False)
    event["event_digest"] = hashlib.sha256(canonical_json(event)).hexdigest()
    return event


def validate_event(event: Any, *, require_digest: bool = True) -> None:
    if not isinstance(event, dict):
        raise ValueError("event must be an object")
    required = ALL_EVENT_FIELDS if require_digest else frozenset(EVENT_FIELDS)
    if frozenset(event) != required:
        raise ValueError("event fields do not match schema v1")
    if type(event.get("schema_version")) is not int or event["schema_version"] != 1:
        raise ValueError("unsupported schema_version")
    for name, limit in (("source_id", 64), ("event_id", 36), ("stream_id", 36)):
        value = event.get(name)
        if not isinstance(value, str) or not value or len(value) > limit or not value.isascii():
            raise ValueError(f"invalid {name}")
    try:
        if str(uuid.UUID(event["event_id"])) != event["event_id"]:
            raise ValueError("event_id must be canonical lowercase UUID")
        if str(uuid.UUID(event["stream_id"])) != event["stream_id"]:
            raise ValueError("stream_id must be canonical lowercase UUID")
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError("invalid event UUID") from exc
    sequence = event.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise ValueError("sequence must be a positive integer")
    parse_utc(event.get("occurred_at"))
    if not isinstance(event.get("event_type"), str) or event.get("event_type") not in {"login.success", "login.failure"}:
        raise ValueError("invalid event_type")
    expected_reason = "SUCCESS" if event.get("event_type") == "login.success" else "INVALID_CREDENTIALS"
    if event.get("reason_code") != expected_reason:
        raise ValueError("reason_code does not match event_type")
    for name in ("account_token", "client_token"):
        value = event.get(name)
        if not isinstance(value, str) or not HEX64.fullmatch(value):
            raise ValueError(f"invalid {name}")
    if require_digest:
        digest = event.get("event_digest")
        if not isinstance(digest, str) or not HEX64.fullmatch(digest):
            raise ValueError("invalid event_digest")
        core = {key: event[key] for key in EVENT_FIELDS}
        if not hashlib.sha256(canonical_json(core)).hexdigest() == digest:
            raise ValueError("event_digest mismatch")


def event_json(event: dict[str, Any]) -> str:
    validate_event(event)
    return canonical_json(event).decode("utf-8")


STATUS_FIELDS = frozenset({
    'source_id', 'stream_id', 'committed_sequence', 'acknowledged_sequence',
    'pending_count', 'held_count', 'rejected_count', 'offered_count',
    'accepted_local_count', 'source_time',
})


def validate_source_status(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != STATUS_FIELDS:
        raise ValueError('source status fields do not match contract')
    if not isinstance(value['source_id'], str) or not value['source_id'] or len(value['source_id']) > 64 or not value['source_id'].isascii():
        raise ValueError('invalid source_id')
    stream = value['stream_id']
    try:
        if not isinstance(stream, str) or str(uuid.UUID(stream)) != stream:
            raise ValueError('invalid stream_id')
    except (TypeError, AttributeError, ValueError):
        raise ValueError('invalid stream_id') from None
    for name in ('committed_sequence', 'acknowledged_sequence', 'pending_count',
                 'held_count', 'rejected_count', 'offered_count', 'accepted_local_count'):
        if type(value[name]) is not int or not 0 <= value[name] <= (1 << 63)-1:
            raise ValueError('invalid counter or watermark')
    if value['acknowledged_sequence'] > value['committed_sequence']:
        raise ValueError('ACK watermark exceeds committed sequence')
    parse_utc(value['source_time'])


def build_receipt(event: dict, status: str = 'stored') -> dict:
    validate_event(event)
    if status not in {'stored', 'duplicate'}:
        raise ValueError('invalid receipt status')
    return {'status': status, 'source_id': event['source_id'],
            'event_id': event['event_id'], 'event_digest': event['event_digest']}


def validate_receipt(receipt: Any, event: dict) -> None:
    validate_event(event)
    if not isinstance(receipt, dict) or set(receipt) != {'status', 'source_id', 'event_id', 'event_digest'}:
        raise ValueError('receipt fields do not match contract')
    if not isinstance(receipt['status'], str) or receipt['status'] not in {'stored', 'duplicate'}:
        raise ValueError('invalid receipt status')
    for name in ('source_id', 'event_id', 'event_digest'):
        if receipt[name] != event[name]:
            raise ValueError('receipt does not match event')
