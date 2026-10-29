import copy
import unittest

from loglab.events import build_event, canonical_json, validate_event


class EventContractTests(unittest.TestCase):
    def make_event(self):
        return build_event(source_id="login-lab-a", stream_id="12345678-1234-5678-1234-567812345678",
                           sequence=1, occurred_at="2026-10-11T00:00:00.000Z",
                           event_type="login.failure", account_token="a" * 64,
                           client_token="b" * 64, reason_code="INVALID_CREDENTIALS",
                           event_id="12345678-1234-5678-1234-567812345679")

    def test_canonical_json_and_digest_are_stable(self):
        event = self.make_event()
        validate_event(event)
        self.assertEqual(canonical_json(event), canonical_json(dict(reversed(list(event.items())))))

    def test_tampering_is_detected(self):
        event = self.make_event()
        event["sequence"] = 2
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_event(event)

    def test_schema_rejects_extra_fields_and_wrong_reason(self):
        event = self.make_event()
        event["password"] = "must not be present"
        with self.assertRaisesRegex(ValueError, "fields"):
            validate_event(event)
        event = self.make_event()
        event["reason_code"] = "SUCCESS"
        core = {k: v for k, v in event.items() if k != "event_digest"}
        from hashlib import sha256
        event["event_digest"] = sha256(canonical_json(core)).hexdigest()
        with self.assertRaisesRegex(ValueError, "does not match"):
            validate_event(event)


if __name__ == "__main__":
    unittest.main()
