"""Tes statis deployment Source (kontrak). Tidak menjalankan systemd atau firewall nyata."""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from loglab.contract import ROOT

DEPLOY = ROOT / "deployment" / "source"
CONTRACT = json.loads((ROOT / "config" / "contract.json").read_text(encoding="utf-8"))
SOURCE = CONTRACT["roles"]["source"]
NETWORK = CONTRACT["network"]
SERVICE = (DEPLOY / "loglab-source.service").read_text()
NFT = (DEPLOY / "source.nft").read_text()
SETUP = (DEPLOY / "setup.sh").read_text()


def exec_start():
    return re.search(r"^ExecStart=(.*)$", SERVICE, re.M).group(1)


class ServiceUnitTests(unittest.TestCase):
    def test_unit_uses_contract_values(self):
        self.assertIn("User=loglab-svc", SERVICE)
        self.assertIn("EnvironmentFile=" + SOURCE["env_file"], SERVICE)
        self.assertIn("WorkingDirectory=" + CONTRACT["paths"]["project"], SERVICE)
        self.assertTrue(exec_start().startswith(CONTRACT["paths"]["venv"] + "/bin/python -m uvicorn " + SOURCE["entrypoint"] + " "))
        self.assertIn("ReadWritePaths=" + CONTRACT["paths"]["data"], SERVICE)
        self.assertEqual(SOURCE["service"], "loglab-source.service")
        self.assertIn("Restart=always", SERVICE)

    def test_bind_port_and_tls_come_from_env_not_hardcoded(self):
        for variable in ("LOGLAB_BIND_HOST", "LOGLAB_PORT", "LOGLAB_TLS_KEY", "LOGLAB_TLS_CERT"):
            self.assertIn("${%s}" % variable, exec_start())
        self.assertNotIn(SOURCE["ip"], exec_start())

    def test_single_worker_and_runtime_dir_for_sender_lock(self):
        self.assertNotIn("--workers", exec_start())  # sender di dalam proses: satu worker
        self.assertIn("RuntimeDirectory=loglab", SERVICE)
        example = (ROOT / "config" / "source.example.env").read_text()
        lock = re.search(r"^LOGLAB_SENDER_LOCK=(.*)$", example, re.M).group(1)
        self.assertEqual(Path(lock).parent.as_posix(), "/run/loglab")

    def test_unit_is_hardened_and_does_not_log_requests(self):
        for directive in ("NoNewPrivileges=true", "ProtectSystem=strict", "PrivateTmp=true", "ProtectHome=read-only"):
            self.assertIn(directive, SERVICE)
        self.assertIn("--no-access-log", exec_start())


class FirewallTests(unittest.TestCase):
    def rules(self):
        return [l.strip() for l in NFT.splitlines() if "accept" in l and not l.strip().startswith("#")]

    def test_every_contract_inbound_rule_is_present(self):
        for rule in NETWORK["inbound_tcp"]["source"]:
            ports = rule["ports"]
            wanted = "tcp dport { %s }" % ", ".join(map(str, ports))
            self.assertTrue(any("ip saddr %s %s accept" % (rule["from"], wanted) in r for r in self.rules()), rule)

    def test_default_deny_and_no_other_hosts(self):
        chains = dict(re.findall(r"chain (\w+) \{\s*type filter hook \w+ priority filter; policy (\w+);", NFT))
        self.assertEqual((chains["input"], chains["forward"]), ("drop", "drop"))
        code = "\n".join(l for l in NFT.splitlines() if not l.strip().startswith("#"))
        for ip in set(re.findall(r"\b172\.16\.202\.\d+\b", code)):
            self.assertEqual(ip, NETWORK["host_ip"])  # Monitor tidak boleh masuk ke Source
        for rule in self.rules():
            if "tcp dport" in rule:
                self.assertIn("ip saddr", rule)
        self.assertNotIn("0.0.0.0/0", NFT)

    def test_syntax_accepted_by_nft_when_available(self):
        if shutil.which("nft") is None:
            self.skipTest("nft tidak tersedia")
        result = subprocess.run(["nft", "-c", "-f", str(DEPLOY / "source.nft")], capture_output=True, text=True)
        if "Operation not permitted" in result.stderr:
            self.skipTest("nft -c butuh hak akses netlink di lingkungan ini")
        self.assertEqual(result.returncode, 0, result.stderr)


class SetupScriptTests(unittest.TestCase):
    def test_syntax_is_valid(self):
        if shutil.which("bash") is None:
            self.skipTest("bash tidak tersedia")
        result = subprocess.run(["bash", "-n", str(DEPLOY / "setup.sh")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_paths_and_ip_match_contract(self):
        self.assertIn('CONF_DIR="%s"' % CONTRACT["paths"]["private_config"], SETUP)
        self.assertIn('ENV_FILE="${CONF_DIR}/%s"' % Path(SOURCE["env_file"]).name, SETUP)
        self.assertIn('ACCOUNTS_FILE="${CONF_DIR}/%s"' % Path(SOURCE["test_accounts_file"]).name, SETUP)
        self.assertIn('DB_FILE="${DATA_DIR}/%s"' % Path(SOURCE["db_file"]).name, SETUP)
        self.assertIn('SOURCE_IP="%s"' % SOURCE["ip"], SETUP)
        self.assertIn('WANTED_HOSTNAME="%s"' % SOURCE["hostname"], SETUP)
        self.assertIn('SOURCE_PORT="%d"' % NETWORK["https_port"], SETUP)

    def test_permissions_follow_the_contract(self):
        self.assertRegex(SETUP, r"install -d -o root -g \"\$SERVICE_USER\" -m 0750 \"\$CONF_DIR\"")
        self.assertRegex(SETUP, r"install -d -o \"\$SERVICE_USER\" -g \"\$SERVICE_USER\" -m 0700 \"\$DATA_DIR\"")
        self.assertIn('chmod 0600 "$ENV_FILE"', SETUP)
        self.assertIn('chmod 0600 "$ACCOUNTS_FILE"', SETUP)
        self.assertIn('chmod 0640 "${CONF_DIR}/tls.key"', SETUP)
        self.assertNotIn("777", SETUP)
        self.assertNotIn("chmod -R", SETUP)

    def test_validates_env_and_seeds_before_starting_and_never_overwrites_secrets(self):
        order = [SETUP.index(name + "\n    ") for name in ("validate_env", "check_tls", "seed_accounts", "install_units", "start_service", "health_check")
                 if (name + "\n    ") in SETUP]
        self.assertEqual(order, sorted(order))
        self.assertIn('scripts/check_contract.py" --role source --env', SETUP)
        self.assertIn('if [ -e "$ENV_FILE" ]; then', SETUP)

    def test_seed_goes_through_stdin_as_service_user_without_printing_passwords(self):
        self.assertIn('--accounts-file - < "$ACCOUNTS_FILE"', SETUP)
        self.assertIn('runuser -u "$SERVICE_USER"', SETUP)
        self.assertNotIn("cat \"$ACCOUNTS_FILE\"", SETUP)

    def test_setup_checks_service_account_access_tls_and_ssh_isolation(self):
        self.assertIn("import loglab.source_main", SETUP)
        self.assertIn(".ssh", SETUP)
        self.assertIn("openssl verify -CAfile", SETUP)
        self.assertIn("IP Address:${SOURCE_IP}", SETUP)
        self.assertIn("nft -c -f", SETUP)
        self.assertIn('/health"', SETUP)

    def test_setup_is_executable_like_monitor_setup(self):
        self.assertTrue((DEPLOY / "setup.sh").stat().st_mode & 0o111)


if __name__ == "__main__":
    unittest.main()
