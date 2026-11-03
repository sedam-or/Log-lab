"""Kontrak 1.1.0 vs kode: rute implemented harus ada, planned tidak boleh diklaim ada."""
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

from loglab.config import Settings
from loglab.contract import ROOT, load_contract
from loglab.events import build_event, canonical_json
from loglab.monitor_app import create_app as create_monitor
from loglab.source_app import create_app as create_source

C = load_contract()
API = C["api"]
SOURCE_ENDPOINTS = ("source_login_form", "source_login_form_submit", "source_login_submit")
from loglab.contract import MONITOR_UI_ENDPOINTS
MONITOR_ENDPOINTS = ("monitor_events", "monitor_status", "dashboard", *MONITOR_UI_ENDPOINTS)


def routes(app):
    found = set()
    for route in app.routes:
        for method in getattr(route, "methods", None) or ():
            if method != "HEAD":
                found.add((method, route.path))
    return found


class RouteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        token = "1a" * 32
        cls.source = routes(create_source(Settings.for_test("source", base, source_token=token)))
        cls.monitor = routes(create_monitor(Settings.for_test("monitor", base, source_token=token)))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def check(self, names, found):
        for name in names:
            spec = API[name]
            present = (spec["method"], spec["path"]) in found
            if spec["status"] == "implemented":
                self.assertTrue(present, f"{name} bertanda implemented tetapi rute tidak ada")
            else:
                self.assertFalse(present, f"{name} bertanda planned tetapi rute sudah ada; ubah status")

    def test_source_routes_match_contract(self):
        self.check(SOURCE_ENDPOINTS, self.source)
        self.assertIn(("GET", API["health"]["path"]), self.source)
        self.assertNotIn(("GET", "/healthz"), self.source)

    def test_monitor_routes_match_contract(self):
        self.check(MONITOR_ENDPOINTS, self.monitor)
        self.assertIn(("GET", API["health"]["path"]), self.monitor)

    def test_every_monitor_route_is_declared_in_the_contract(self):
        declared = {(API[n]["method"], API[n]["path"]) for n in MONITOR_ENDPOINTS}
        declared |= {("GET", API["health"]["path"])}
        docs = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}
        extra = {r for r in self.monitor if r[1] not in docs} - declared
        self.assertEqual(extra, set(), "rute Monitor belum ada di kontrak")


class ErrorAndRetryContractTests(unittest.TestCase):
    def test_every_error_code_in_the_apps_is_in_the_contract(self):
        declared = set(API["errors"])
        for name in ("monitor_app.py", "source_app.py"):
            text = (ROOT / "src" / "loglab" / name).read_text()
            used = set(re.findall(r'_error\(\d+, "([a-z_]+)"\)', text)) | set(re.findall(r'\{"error": "([a-z_]+)"\}', text))
            self.assertLessEqual(used - {"event_conflict", "sequence_conflict", "event_id_conflict"}, declared, name)

    def test_sender_constants_follow_contract(self):
        from loglab import sender
        retry = API["sender_retry"]
        self.assertEqual(sender.PERMANENT_STATUSES, frozenset(retry["hold_http"]))
        self.assertEqual(sender.REQUEST_TIMEOUT_SECONDS, retry["timeout_seconds"])
        self.assertEqual(sender.HEARTBEAT_SECONDS, retry["heartbeat_seconds"])
        self.assertEqual(sender.JITTER_MAX, retry["jitter_max_fraction"])
        self.assertEqual([sender.backoff_delay(n, rng=lambda: 0.0) for n in range(1, 7)], retry["backoff_seconds"])

    def test_source_status_fields_are_all_mapped(self):
        from loglab.events import STATUS_FIELDS as SOURCE_STATUS_FIELDS
        mapped = set(API["source_status_counters"])
        self.assertEqual(mapped, {"offered_count", "accepted_local_count", "rejected_count", "held_count",
                                  "pending_count", "acknowledged_sequence"})
        self.assertTrue(mapped <= set(SOURCE_STATUS_FIELDS))


class DigestVectorTests(unittest.TestCase):
    def test_vector_matches_code_and_independent_computation(self):
        vector = API["digest_test_vector"]
        built = build_event(**{k: v for k, v in vector["event"].items() if k != "schema_version"})
        self.assertEqual(built["event_digest"], vector["event_digest"])
        independent = hashlib.sha256(json.dumps(vector["event"], sort_keys=True, separators=(",", ":"),
                                                ensure_ascii=True).encode()).hexdigest()
        self.assertEqual(independent, vector["event_digest"])
        self.assertEqual(hashlib.sha256(canonical_json(vector["event"])).hexdigest(), vector["event_digest"])


class PermissionContractTests(unittest.TestCase):
    def test_setup_scripts_apply_the_contract_modes(self):
        perms = C["permissions"]
        for role in ("source", "monitor"):
            text = (ROOT / "deployment" / role / "setup.sh").read_text()
            self.assertIn("chmod %s \"$ENV_FILE\"" % perms["env_file"]["mode"], text)
            self.assertIn("chmod %s \"${CONF_DIR}/tls.key\"" % perms["tls_key"]["mode"], text)
            self.assertIn("chmod %s \"${CONF_DIR}/tls.crt\" \"${CONF_DIR}/ca.crt\"" % perms["tls_crt"]["mode"], text)
        source = (ROOT / "deployment" / "source" / "setup.sh").read_text()
        self.assertIn("chmod %s \"$ACCOUNTS_FILE\"" % perms["test_accounts_file"]["mode"], source)
        unit = (ROOT / "deployment" / "source" / "loglab-source.service").read_text()
        self.assertIn("RuntimeDirectoryMode=%s" % perms["run_dir"]["mode"], unit)

    def test_versioning_rules_and_history_are_present(self):
        self.assertEqual(set(C["changes"]["versioning"]) >= {"major", "minor", "patch"}, True)
        self.assertEqual(C["changes"]["history"][0]["version"], C["contract_version"])


if __name__ == "__main__":
    unittest.main()
