"""Contract checks use synthetic secrets only; never a deployed credential."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'scripts/check_contract.py'
spec = importlib.util.spec_from_file_location('check_contract', MODULE)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.c = contract.load_contract()

    def values(self, role):
        values = {}
        for key, rule in contract.role_specs(self.c, role).items():
            if rule['kind'] == 'fixed':
                values[key] = rule['values'][role]
            elif rule['kind'] == 'hex64':
                values[key] = '1a' * 32 if key == 'LOGLAB_SOURCE_TOKEN' else '2b' * 32
            else:
                values[key] = 'scrypt$16384$8$1$' + '3c' * 16 + '$' + '4d' * 32
        return values

    def test_repo_examples_and_tables_are_synchronized(self):
        contract.check_repo(self.c)

    def test_runtime_pair_with_matching_synthetic_token_passes(self):
        contract.validate_pair(self.c, self.values('source'), self.values('monitor'))

    def test_template_is_not_accepted_as_runtime_config(self):
        for role in ['source', 'monitor']:
            values = {k: (v['values'][role] if v['kind'] == 'fixed' else v['example'])
                      for k, v in contract.role_specs(self.c, role).items()}
            with self.assertRaises(contract.ContractError):
                contract.validate_env(self.c, role, values)

    def test_wrong_bind_ip_is_rejected(self):
        for wrong in ['0.0.0.0', '172.16.202.22', '127.0.0.1']:
            values = self.values('source')
            values['LOGLAB_BIND_HOST'] = wrong
            with self.assertRaises(contract.ContractError):
                contract.validate_env(self.c, 'source', values)

    def test_monitor_url_protocol_path_and_trailing_slash_are_rejected(self):
        for wrong in ['http://172.16.202.22:8443', 'https://172.16.202.22:8443/api', 'https://172.16.202.22:8443/']:
            values = self.values('source')
            values['LOGLAB_MONITOR_URL'] = wrong
            with self.assertRaises(contract.ContractError):
                contract.validate_env(self.c, 'source', values)

    def test_unknown_alias_missing_key_and_wrong_role_key_are_rejected(self):
        variants = []
        values = self.values('source'); values['MONITOR_URL'] = 'example'; variants.append(('source', values))
        values = self.values('source'); del values['LOGLAB_SOURCE_ID']; variants.append(('source', values))
        values = self.values('monitor'); values['LOGLAB_PSEUDONYM_KEY'] = '2b' * 32; variants.append(('monitor', values))
        for role, values in variants:
            with self.assertRaises(contract.ContractError):
                contract.validate_env(self.c, role, values)

    def test_source_identity_and_contract_version_cannot_drift(self):
        for key, wrong in [('LOGLAB_SOURCE_ID', 'other-source'), ('LOGLAB_CONTRACT_VERSION', '0.0.0')]:
            values = self.values('source'); values[key] = wrong
            with self.assertRaises(contract.ContractError):
                contract.validate_env(self.c, 'source', values)

    def test_pair_rejects_different_validly_formed_tokens(self):
        a, b = self.values('source'), self.values('monitor')
        b['LOGLAB_SOURCE_TOKEN'] = '5e' * 32
        with self.assertRaisesRegex(contract.ContractError, 'differs'):
            contract.validate_pair(self.c, a, b)

    def test_malformed_secret_and_raw_operator_password_are_rejected(self):
        for role, key, wrong in [('source', 'LOGLAB_PSEUDONYM_KEY', '0' * 64),
                                  ('source', 'LOGLAB_SOURCE_TOKEN', 'AB' * 32),
                                  ('monitor', 'LOGLAB_OPERATOR_PASSWORD_HASH', 'synthetic-raw-password')]:
            values = self.values(role); values[key] = wrong
            with self.assertRaises(contract.ContractError):
                contract.validate_env(self.c, role, values)

    def test_literal_hash_with_dollars_survives_env_parsing(self):
        values = self.values('monitor')
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'monitor.env'
            p.write_text('\n'.join(k + '=' + v for k, v in values.items()))
            self.assertEqual(contract.parse_env(p), values)

    def test_duplicate_key_shell_syntax_and_whitespace_fail_without_echo(self):
        sentinel = 'synthetic-private-value-never-echo'
        for text in ['LOGLAB_ROLE=source\nLOGLAB_ROLE=' + sentinel,
                     'export LOGLAB_ROLE=' + sentinel, 'LOGLAB_ROLE =' + sentinel]:
            with tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / 'source.env'; p.write_text(text)
                with self.assertRaises(contract.ContractError) as caught:
                    contract.parse_env(p)
                self.assertNotIn(sentinel, str(caught.exception))

    def test_manifest_rejects_overlap_out_of_subnet_and_default_gateway(self):
        variants = []
        c = deepcopy(self.c); c['roles']['source']['ip'] = c['network']['host_ip']; variants.append(c)
        c = deepcopy(self.c); c['roles']['monitor']['ip'] = '192.168.9.22'; variants.append(c)
        c = deepcopy(self.c); c['network']['default_gateway'] = '172.16.202.1'; variants.append(c)
        for c in variants:
            with self.assertRaises(contract.ContractError):
                contract.validate_contract(c)

    def test_firewall_must_not_allow_source_ssh_to_monitor(self):
        c = deepcopy(self.c)
        c['network']['inbound_tcp']['monitor'][1]['ports'].append(22)
        with self.assertRaises(contract.ContractError):
            contract.validate_contract(c)

    def test_unreadable_encoding_does_not_echo_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'bad.env'
            p.write_bytes(b'LOGLAB_SOURCE_TOKEN=\xffsynthetic-private')
            with self.assertRaises(contract.ContractError) as caught:
                contract.parse_env(p)
            self.assertNotIn('synthetic-private', str(caught.exception))

    def test_wrong_launch_metadata_and_private_paths_are_rejected(self):
        for key, wrong in [('entrypoint', 'loglab.monitor_main:app'),
                           ('env_file', '/tmp/source.env'), ('db_file', '/tmp/source.sqlite3'),
                           ('setup_script', 'deploy/source/setup.sh')]:
            c = deepcopy(self.c); c['roles']['source'][key] = wrong
            with self.assertRaises(contract.ContractError):
                contract.validate_contract(c)

    def test_project_and_checksum_sidecar_cannot_drift(self):
        c = deepcopy(self.c); c['paths']['venv'] = '/opt/old/.venv'
        with self.assertRaises(contract.ContractError):
            contract.validate_contract(c)
        c = deepcopy(self.c); c['roles']['monitor']['model_checksum_file'] = '/var/lib/loglab/unrelated.sha256'
        with self.assertRaises(contract.ContractError):
            contract.validate_contract(c)

    def test_manifest_env_and_origin_must_agree(self):
        c = deepcopy(self.c); c['env']['LOGLAB_PORT']['values']['source'] = '8081'
        with self.assertRaises(contract.ContractError):
            contract.validate_contract(c)

    def test_modified_template_and_documentation_are_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'config').mkdir()
            d = root / 'docs/interface-contracts'; d.mkdir(parents=True)
            p = d / 'index.md'; p.write_text(contract.START + '\n' + contract.END)
            contract.check_repo(self.c, root=root, sync=True)
            template = root / self.c['roles']['source']['config_example']
            template.write_text(template.read_text().replace('8443', '8081'))
            with self.assertRaises(contract.ContractError):
                contract.check_repo(self.c, root=root)
            contract.check_repo(self.c, root=root, sync=True)
            human = root / 'config/contract.md'
            human.write_text(human.read_text().replace('172.16.202.21', '172.16.202.99'))
            with self.assertRaises(contract.ContractError):
                contract.check_repo(self.c, root=root)
            contract.check_repo(self.c, root=root, sync=True)
            p.write_text(p.read_text().replace('`8443`', '`8081`'))
            with self.assertRaises(contract.ContractError):
                contract.check_repo(self.c, root=root)

    def test_ca_copy_check_detects_different_file_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / 'a.crt', Path(tmp) / 'b.crt'
            fake = b'-----BEGIN CERTIFICATE-----\nSYNTHETIC\n'
            a.write_bytes(fake); b.write_bytes(fake)
            contract.check_ca_pair(a, b)
            b.write_bytes(fake + b'DIFFERENT')
            with self.assertRaises(contract.ContractError):
                contract.check_ca_pair(a, b)

    def test_cli_failure_does_not_print_secret_value(self):
        values = self.values('source')
        sentinel = 'synthetic-private-token-should-not-appear'
        values['LOGLAB_SOURCE_TOKEN'] = sentinel
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'private.env'; p.write_text('\n'.join(k+'='+v for k,v in values.items()))
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = contract.main(['--role', 'source', '--env', str(p)])
            self.assertEqual(code, 1)
            self.assertNotIn(sentinel, out.getvalue() + err.getvalue())


if __name__ == '__main__':
    unittest.main()
