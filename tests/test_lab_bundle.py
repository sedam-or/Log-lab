"""Tes make_lab_bundle.py dan pemasangan bundle oleh setup.sh (tanpa root, tanpa VM)."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from loglab.contract import ROOT, ContractError, check_ca_pair, load_contract, parse_env, validate_pair

SCRIPT = ROOT / "scripts" / "make_lab_bundle.py"
CONTRACT = load_contract()


@unittest.skipIf(shutil.which("openssl") is None, "openssl tidak tersedia")
class BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "bundle"
        cls.run_result = subprocess.run([sys.executable, "-I", str(SCRIPT), "--out", str(cls.out)],
                                        capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_creates_expected_files_with_private_permissions(self):
        self.assertEqual(self.run_result.returncode, 0, self.run_result.stderr)
        names = sorted(str(p.relative_to(self.out)) for p in self.out.rglob("*") if p.is_file())
        self.assertEqual(names, sorted([
            "KREDENSIAL-PRIVAT.txt", "ca.crt", "monitor/monitor.env", "monitor/tls.crt", "monitor/tls.key",
            "source/source.env", "source/test-accounts.json", "source/tls.crt", "source/tls.key"]))
        self.assertNotIn("ca.key", "".join(names))
        for path in self.out.rglob("*"):
            self.assertEqual(path.stat().st_mode & 0o077, 0, path)

    def test_envs_match_contract_and_share_one_token(self):
        source, monitor = parse_env(self.out / "source" / "source.env"), parse_env(self.out / "monitor" / "monitor.env")
        validate_pair(CONTRACT, source, monitor)
        self.assertNotEqual(source["LOGLAB_SOURCE_TOKEN"], source["LOGLAB_PSEUDONYM_KEY"])
        self.assertNotIn("LOGLAB_PSEUDONYM_KEY", monitor)  # kunci pseudonim hanya di Source

    def test_certificates_chain_to_ca_with_each_role_ip(self):
        for role in ("source", "monitor"):
            crt = self.out / role / "tls.crt"
            verify = subprocess.run(["openssl", "verify", "-CAfile", str(self.out / "ca.crt"), str(crt)],
                                    capture_output=True, text=True)
            self.assertEqual(verify.returncode, 0, verify.stderr)
            san = subprocess.run(["openssl", "x509", "-in", str(crt), "-noout", "-ext", "subjectAltName"],
                                 capture_output=True, text=True).stdout
            self.assertIn("IP Address:" + CONTRACT["roles"][role]["ip"], san)
        check_ca_pair(self.out / "ca.crt", self.out / "ca.crt")

    def test_demo_accounts_and_credentials_file(self):
        accounts = json.loads((self.out / "source" / "test-accounts.json").read_text())
        self.assertEqual(sorted(accounts), sorted(CONTRACT["roles"]["source"]["demo_usernames"]))
        self.assertTrue(all(len(p) >= 12 for p in accounts.values()))
        creds = (self.out / "KREDENSIAL-PRIVAT.txt").read_text()
        for password in accounts.values():
            self.assertIn(password, creds)
            self.assertNotIn(password, (self.out / "monitor" / "monitor.env").read_text())
            self.assertNotIn(password, self.run_result.stdout + self.run_result.stderr)

    def test_refuses_non_empty_folder_and_repo_paths(self):
        again = subprocess.run([sys.executable, "-I", str(SCRIPT), "--out", str(self.out)], capture_output=True, text=True)
        self.assertNotEqual(again.returncode, 0)
        inside = subprocess.run([sys.executable, "-I", str(SCRIPT), "--out", str(ROOT / "bundle-uji-jangan-dibuat")],
                                capture_output=True, text=True)
        self.assertEqual(inside.returncode, 2)
        self.assertFalse((ROOT / "bundle-uji-jangan-dibuat").exists())

    def test_passes_the_setup_validators(self):
        for role, name in (("source", "source.env"), ("monitor", "monitor.env")):
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_contract.py"), "--role", role,
                                     "--env", str(self.out / role / name)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class SetupBundleTests(unittest.TestCase):
    def test_both_setup_scripts_install_bundle_without_overwriting(self):
        for role, files in (("source", ("source.env", "tls.crt", "tls.key", "test-accounts.json")),
                            ("monitor", ("monitor.env", "tls.crt", "tls.key"))):
            text = (ROOT / "deployment" / role / "setup.sh").read_text()
            self.assertIn("LOGLAB_BUNDLE", text)
            self.assertIn('if [ -e "$target" ]; then', text)
            for name in files:
                self.assertIn("/%s/%s:" % (role, name), text)
            self.assertLess(text.index("    install_bundle\n"), text.index("    ensure_env\n"))
            self.assertNotIn("ca.key", text.split("install_bundle() {")[1].split("grant_project_access")[0])

    def test_makefile_targets_and_gitignore(self):
        makefile = (ROOT / "Makefile").read_text()
        for target in ("lab-bundle:", "setup-source:", "setup-monitor:"):
            self.assertIn(target, makefile)
        ignore = (ROOT / ".gitignore").read_text()
        for pattern in ("loglab-bundle/", "test-accounts.json", "KREDENSIAL-PRIVAT.txt"):
            self.assertIn(pattern, ignore)
        self.assertEqual(CONTRACT["roles"]["source"]["setup_target"], "setup-source")


if __name__ == "__main__":
    unittest.main()
