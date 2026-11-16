"""Tes statis baseline container (Modul 7). Tidak menjalankan Docker; uji e2e ada di deployment/container/smoke-e2e.sh."""
import json
import re
import unittest

from loglab.contract import ROOT

CONTAINER = ROOT / "deployment" / "container"
CONTRACT = json.loads((ROOT / "config" / "contract.json").read_text(encoding="utf-8"))
DOCKERFILE = (CONTAINER / "Dockerfile").read_text(encoding="utf-8")
COMPOSE = (CONTAINER / "compose.yaml").read_text(encoding="utf-8")
MAKE_PRIVATE = (CONTAINER / "make-private.sh").read_text(encoding="utf-8")
SMOKE = (CONTAINER / "smoke-e2e.sh").read_text(encoding="utf-8")
MAKEFILE = (ROOT / "Makefile").read_text(encoding="utf-8")


class DockerfileTests(unittest.TestCase):
    def test_base_image_is_pinned_by_digest(self):
        self.assertRegex(DOCKERFILE, re.compile(r"^FROM python:3\.13-slim@sha256:[0-9a-f]{64}$", re.M))

    def test_dependencies_install_from_hashed_lock(self):
        self.assertIn("pip install --require-hashes --no-deps -r requirements.lock", DOCKERFILE)

    def test_runs_as_fixed_non_root_user(self):
        self.assertIn("USER 10001:10001", DOCKERFILE)
        self.assertIn("--uid 10001", DOCKERFILE)

    def test_contract_json_is_copied_for_env_validation(self):
        self.assertIn("COPY config/contract.json ./config/contract.json", DOCKERFILE)

    def test_no_secret_or_env_file_is_copied(self):
        self.assertNotRegex(DOCKERFILE, r"COPY\s+.*(\.env|private|tls|\.key|\.pem|sqlite)")


class ComposeTests(unittest.TestCase):
    def test_network_is_internal_and_publishes_no_ports(self):
        self.assertIn("internal: true", COMPOSE)
        self.assertNotRegex(COMPOSE, re.compile(r"^\s+ports:", re.M))

    def test_static_ips_match_contract_roles(self):
        self.assertIn(CONTRACT["roles"]["source"]["ip"], COMPOSE)
        self.assertIn(CONTRACT["roles"]["monitor"]["ip"], COMPOSE)
        self.assertIn("ipv4_address: " + CONTRACT["roles"]["source"]["ip"], COMPOSE)
        self.assertIn("ipv4_address: " + CONTRACT["roles"]["monitor"]["ip"], COMPOSE)

    def test_containers_hardened(self):
        self.assertIn("read_only: true", COMPOSE)
        self.assertIn("cap_drop:", COMPOSE)
        self.assertIn("no-new-privileges:true", COMPOSE)
        self.assertIn('user: "10001:10001"', COMPOSE)

    def test_env_files_come_from_private_dir_not_repo(self):
        self.assertIn("${LOGLAB_PRIVATE_DIR:-./private}/source.env", COMPOSE)
        self.assertIn("${LOGLAB_PRIVATE_DIR:-./private}/monitor.env", COMPOSE)


class PrivateFolderScriptTests(unittest.TestCase):
    def test_renders_from_contract_examples(self):
        self.assertIn("config/source.example.env", MAKE_PRIVATE)
        self.assertIn("config/monitor.example.env", MAKE_PRIVATE)

    def test_script_contains_no_literal_secret(self):
        self.assertIsNone(re.search(r"[0-9a-f]{64}", MAKE_PRIVATE))
        self.assertNotIn("scrypt$16384", MAKE_PRIVATE)

    def test_compose_dollar_escape_is_applied_to_hash(self):
        self.assertIn("'$$'", MAKE_PRIVATE)


class SmokeAndMakefileTests(unittest.TestCase):
    def test_smoke_checks_health_login_and_monitor_event(self):
        for needle in ("/health", "/api/v1/login", "monitor_events", "verify_password"):
            self.assertIn(needle, SMOKE)

    def test_makefile_exposes_container_targets(self):
        for target in ("container-private:", "container-build:", "container-up:", "container-e2e:", "container-down:"):
            self.assertIn(target, MAKEFILE)


if __name__ == "__main__":
    unittest.main()
