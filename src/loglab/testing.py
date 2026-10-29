"""In-memory receiver simulation for sender unit tests, not the Monitor app."""
from __future__ import annotations

from copy import deepcopy
import hmac
import json
from pathlib import Path

from .contract import ROOT, load_contract
from .events import validate_event, validate_source_status, utc_now, parse_utc


def fixture(name: str) -> dict:
    allowed = {'login-success', 'login-failure', 'stored-receipt', 'source-status'}
    if name not in allowed:
        raise ValueError('unknown shared fixture')
    return json.loads((ROOT / 'tests/fixtures' / (name + '.json')).read_text(encoding='utf-8'))


class ReceiverStub:
    """A transport double: pass post into sender tests instead of making HTTPS.

    It simulates only event auth/schema/identity/receipt. TLS, persistence,
    limits and concurrency still need tests of Arhasya's real receiver.
    """
    def __init__(self, source_token: str):
        self.source_token = source_token
        self.events: dict[tuple[str, str], dict] = {}
        self.sequences: dict[tuple[str, str, int], str] = {}
        self.available = True
        self.statuses = {}

    def post(self, path: str, payload: dict, source_token: str) -> tuple[int, dict]:
        if not self.available:
            raise TimeoutError('simulated receiver unavailable')
        if path not in {'/api/v1/events', '/api/v1/source-status'}:
            return 404, {'error': 'not_found'}
        if not hmac.compare_digest(source_token, self.source_token):
            return 401, {'error': 'unauthorized'}
        if path == '/api/v1/source-status':
            try:
                validate_source_status(payload)
            except ValueError:
                return 422, {'error': 'invalid_source_status'}
            if payload['source_id'] != load_contract()['identity']['source_id']:
                return 401, {'error': 'unknown_source'}
            self.statuses[(payload['source_id'], payload['stream_id'])] = deepcopy(payload)
            received = utc_now()
            offset = int((parse_utc(received) - parse_utc(payload['source_time'])).total_seconds()*1000)
            return 200, {'status': 'accepted', 'source_id': payload['source_id'],
                         'received_at': received, 'clock_offset_ms': offset}
        try:
            validate_event(payload)
        except ValueError:
            return 422, {'error': 'invalid_event'}
        if payload['source_id'] != load_contract()['identity']['source_id']:
            return 401, {'error': 'unknown_source'}
        identity = payload['source_id'], payload['event_id']
        sequence = payload['source_id'], payload['stream_id'], payload['sequence']
        previous = self.events.get(identity)
        if previous is not None:
            if previous['event_digest'] != payload['event_digest']:
                return 409, {'error': 'event_conflict'}
            status = 'duplicate'
        elif sequence in self.sequences:
            return 409, {'error': 'sequence_conflict'}
        else:
            self.events[identity] = deepcopy(payload)
            self.sequences[sequence] = payload['event_id']
            status = 'stored'
        return 200, {'status': status, 'source_id': payload['source_id'],
                     'event_id': payload['event_id'], 'event_digest': payload['event_digest']}
