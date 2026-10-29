"""Validate the public parameter contract and literal per-role env files.

Uses only the Python standard library. Never prints env values or secret inputs.
This is an offline configuration check, not a network/deployment acceptance test.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import ipaddress
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- CONTRACT-TABLES:START -->'
END = '<!-- CONTRACT-TABLES:END -->'


class ContractError(ValueError):
    pass


def load_contract(root: Path = ROOT) -> dict:
    try:
        c = json.loads((root / 'config/contract.json').read_text(encoding='utf-8'))
        validate_contract(c)
        return c
    except (OSError, KeyError, TypeError, json.JSONDecodeError, ValueError) as exc:
        if isinstance(exc, ContractError):
            raise
        raise ContractError('Contract structure is invalid or cannot be read.') from None


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def validate_contract(c: dict) -> None:
    require(bool(re.fullmatch(r'\d+\.\d+\.\d+', c['contract_version'])), 'Invalid contract version.')
    net = ipaddress.ip_network(c['network']['cidr'], strict=True)
    require(net.version == 4 and net.is_private, 'Integration network must be private IPv4.')
    require(c['network']['default_gateway'] is None, 'Host-only must not define an internet gateway.')
    require(c['network']['runtime_nat_enabled'] is False, 'Runtime NAT must be disabled.')
    require(set(c['roles']) == {'source', 'monitor'}, 'Exactly source and monitor roles are required.')
    host = ipaddress.ip_address(c['network']['host_ip'])
    addresses = [host]
    for port in [c['network']['https_port'], c['network']['ssh_port']]:
        require(type(port) is int and 1 <= port <= 65535, 'Invalid port.')
    require(c['network']['https_port'] != c['network']['ssh_port'], 'SSH and HTTPS ports must differ.')
    for role, spec in c['roles'].items():
        ip = ipaddress.ip_address(spec['ip'])
        addresses.append(ip)
        origin = f"https://{ip}:{c['network']['https_port']}"
        require(c['api'][role + '_origin'] == origin, f'{role}: origin does not match IP/port.')
        require(spec['service'] == 'loglab-' + role + '.service', f'{role}: unexpected service name.')
        require(spec['hostname'] == 'loglab-' + role, f'{role}: unexpected hostname.')
        require(spec['entrypoint'] == 'loglab.' + role + '_main:app', f'{role}: unexpected entrypoint.')
        require(spec['env_file'] == c['paths']['private_config'] + '/' + role + '.env', f'{role}: wrong env path.')
        require(spec['db_file'] == c['paths']['data'] + '/' + role + '.sqlite3', f'{role}: wrong DB path.')
        require(spec['setup_script'] == 'deployment/' + role + '/setup.sh', f'{role}: wrong setup path.')
        require(spec['config_example'] == 'config/' + role + '.example.env', f'{role}: wrong template path.')
        for field in ['env_file', 'db_file']:
            require(Path(spec[field]).is_absolute(), f'{role}: {field} must be absolute.')
    require(len(set(addresses)) == len(addresses), 'Host and guest IPs must be distinct.')
    require(all(ip in net and ip not in {net.network_address, net.broadcast_address} for ip in addresses), 'Host/guest IP is outside usable subnet.')
    expected_inbound = {
        'source': [{'from': c['network']['host_ip'], 'ports': [c['network']['ssh_port'], c['network']['https_port']]}],
        'monitor': [{'from': c['network']['host_ip'], 'ports': [c['network']['ssh_port'], c['network']['https_port']]},
                    {'from': c['roles']['source']['ip'], 'ports': [c['network']['https_port']]}],
    }
    require(c['network']['inbound_tcp'] == expected_inbound, 'Inbound TCP rules conflict with host/source isolation.')
    require(c['roles']['source']['db_file'] != c['roles']['monitor']['db_file'], 'Role DB filenames must differ.')
    require(c['paths']['project'] == '/home/' + c['platform']['guest_user'] + '/LogLab', 'Project path must match guest user.')
    require(c['paths']['venv'] == c['paths']['project'] + '/.venv', 'Venv must be inside the project.')
    require(c['roles']['monitor']['model_checksum_file'] == c['roles']['monitor']['model_file'] + '.sha256', 'Model checksum sidecar path differs.')
    for path in c['paths'].values():
        require(Path(path).is_absolute(), 'Shared paths must be absolute.')
    for key, spec in c['env'].items():
        require(bool(re.fullmatch(r'LOGLAB_[A-Z0-9_]+', key)), 'Invalid env key in contract.')
        require(set(spec['roles']) <= set(c['roles']) and bool(spec['roles']), f'{key}: invalid role scope.')
        require(bool(re.fullmatch(r'[a-z][a-z0-9_]*', spec['python_name'])), f'{key}: invalid Python name.')
        if spec['kind'] == 'fixed':
            require(set(spec['values']) == set(spec['roles']), f'{key}: missing fixed values.')
            require(all(isinstance(v, str) and '\n' not in v for v in spec['values'].values()), f'{key}: fixed values must be one-line strings.')
        else:
            require(spec['kind'] in {'hex64', 'scrypt'}, f'{key}: invalid secret type.')
    for role in c['roles']:
        expected = {
            'LOGLAB_CONTRACT_VERSION': c['contract_version'],
            'LOGLAB_ROLE': role,
            'LOGLAB_PORT': str(c['network']['https_port']),
            'LOGLAB_BIND_HOST': c['roles'][role]['ip'],
            'LOGLAB_SOURCE_ID': c['identity']['source_id'],
            'LOGLAB_DB_PATH': c['roles'][role]['db_file'],
            'LOGLAB_CA_BUNDLE': c['paths']['ca'],
            'LOGLAB_TLS_CERT': c['paths']['cert'],
            'LOGLAB_TLS_KEY': c['paths']['key'],
        }
        if role == 'source':
            expected['LOGLAB_MONITOR_URL'] = c['api']['monitor_origin']
        else:
            expected['LOGLAB_MODEL_PATH'] = c['roles']['monitor']['model_file']
            expected['LOGLAB_OPERATOR_USERNAME'] = c['roles']['monitor']['operator_username']
        for key, value in expected.items():
            require(c['env'][key]['values'][role] == value, f'{role}: {key} conflicts with contract.')


def role_specs(c: dict, role: str) -> dict:
    require(role in c['roles'], 'Unknown role.')
    return {key: spec for key, spec in c['env'].items() if role in spec['roles']}


def render_env(c: dict, role: str) -> str:
    lines = [f'# Contract {c["contract_version"]}; {role}; generated, no real secrets.',
             '# Copy to the private env path, fill placeholders, then validate.',
             '# Literal KEY=value. Do not execute this file with shell source.']
    for key, spec in role_specs(c, role).items():
        value = spec['values'][role] if spec['kind'] == 'fixed' else spec['example']
        lines.append(f'{key}={value}')
    return '\n'.join(lines) + '\n'


def render_tables(c: dict) -> str:
    lines = [START, '', f'Versi kontrak: **{c["contract_version"]}**. Profil: **{c["profile"]}**.', '',
             '| Parameter | Nilai yang disepakati |', '| --- | --- |',
             f'| Jaringan host-only | `{c["network"]["cidr"]}`, `{c["network"]["vmnet"]}` |',
             f'| Alamat adapter host | `{c["network"]["host_ip"]}`; bukan default gateway |',
             f'| HTTPS / SSH | `{c["network"]["https_port"]}` / `{c["network"]["ssh_port"]}` |',
             f'| Folder clone / virtualenv | `{c["paths"]["project"]}` / `{c["paths"]["venv"]}` |',
             f'| User guest / service | `{c["platform"]["guest_user"]}` / `{c["platform"]["service_user"]}` |', '',
             '| Peran | IP dan hostname | Service dan entrypoint | Env privat dan DB |', '| --- | --- | --- | --- |']
    for role, spec in c['roles'].items():
        lines.append(f'| {spec["member"]} / {role} | `{spec["ip"]}`; `{spec["hostname"]}` | `{spec["service"]}`; `{spec["entrypoint"]}` | `{spec["env_file"]}`; `{spec["db_file"]}` |')
    lines += ['', '| Variabel wajib | Source | Monitor | Nama pada Settings Python | Arti |', '| --- | --- | --- | --- | --- |']
    for key, spec in c['env'].items():
        cells = []
        for role in ['source', 'monitor']:
            cells.append('Tidak dipakai' if role not in spec['roles'] else (f'`{spec["values"][role]}`' if spec['kind'] == 'fixed' else f'Rahasia: `{spec["kind"]}`'))
        lines.append(f'| `{key}` | {cells[0]} | {cells[1]} | `{spec["python_name"]}` | {spec["description"]} |')
    lines += ['', '| Endpoint | Method | Alamat |', '| --- | --- | --- |']
    for name, role in [('source_login_form', 'source'), ('source_login_form_submit', 'source'), ('source_login_submit', 'source'),
                       ('monitor_events', 'monitor'), ('monitor_status', 'monitor'), ('dashboard', 'monitor')]:
        spec = c['api'][name]
        lines.append(f'| `{name}` | `{spec["method"]}` | `{c["api"][role + "_origin"]}{spec["path"]}` |')
    for role in c['roles']:
        lines.append(f'| `{role}_health` | `GET` | `{c["api"][role + "_origin"]}{c["api"]["health"]["path"]}` |')
    lines += ['', '| Aturan masuk TCP baru | Yang diizinkan |', '| --- | --- |']
    for role, rules in c['network']['inbound_tcp'].items():
        allowed = '; '.join(f'{rule["from"]}: {rule["ports"]}' for rule in rules)
        lines.append(f'| `{role}` | `{allowed}` |')
    lines += ['', END]
    return '\n'.join(lines)


def check_repo(c: dict, root: Path = ROOT, sync: bool = False) -> None:
    for role, spec in c['roles'].items():
        p = root / spec['config_example']
        text = render_env(c, role)
        if sync:
            p.write_text(text, encoding='utf-8')
        require(p.exists() and p.read_text(encoding='utf-8') == text, f'{role}: example differs; review contract and run --sync.')
    p = root / 'docs/interface-contracts/index.md'
    text = p.read_text(encoding='utf-8')
    require(text.count(START) == 1 and text.count(END) == 1 and text.index(START) < text.index(END), 'Contract doc needs one generated table region.')
    expected = render_tables(c)
    if sync:
        text = text[:text.index(START)] + expected + text[text.index(END) + len(END):]
        p.write_text(text, encoding='utf-8')
    current = text[text.index(START):text.index(END) + len(END)]
    require(current == expected, 'Contract documentation differs; review and run --sync.')


def parse_env(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError):
        raise ContractError('Cannot read supplied env file.') from None
    values = {}
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        key, sep, value = line.partition('=')
        require(bool(sep) and bool(re.fullmatch(r'LOGLAB_[A-Z0-9_]+', key)), f'Env line {number}: use literal LOGLAB_NAME=value.')
        require(key not in values, f'Env line {number}: duplicate key.')
        values[key] = value
    return values


def validate_env(c: dict, role: str, values: dict[str, str]) -> None:
    specs = role_specs(c, role)
    require(not (set(values) - set(specs)), f'{role}: unknown or wrong-role variable present.')
    require(not (set(specs) - set(values)), f'{role}: missing required variable.')
    for key, spec in specs.items():
        value = values[key]
        if spec['kind'] == 'fixed':
            require(value == spec['values'][role], f'{role}: {key} differs from contract.')
        elif spec['kind'] == 'hex64':
            require(bool(re.fullmatch(r'[0-9a-f]{64}', value)) and value != '0' * 64, f'{role}: {key} must contain a provisioned lowercase hex secret.')
        else:
            pattern = r'scrypt\$16384\$8\$1\$[0-9a-f]{32}\$[0-9a-f]{64}'
            require(bool(re.fullmatch(pattern, value)), f'{role}: {key} must contain the agreed scrypt hash.')


def validate_pair(c: dict, source: dict, monitor: dict) -> None:
    validate_env(c, 'source', source)
    validate_env(c, 'monitor', monitor)
    require(hmac.compare_digest(source['LOGLAB_SOURCE_TOKEN'], monitor['LOGLAB_SOURCE_TOKEN']), 'Source token differs between A and B.')


def check_ca_pair(source: Path, monitor: Path) -> None:
    try:
        a, b = source.read_bytes(), monitor.read_bytes()
    except OSError:
        raise ContractError('Cannot read supplied CA files.') from None
    require(b'-----BEGIN CERTIFICATE-----' in a and b'-----BEGIN CERTIFICATE-----' in b, 'Expected public CA PEM files.')
    require(hmac.compare_digest(hashlib.sha256(a).digest(), hashlib.sha256(b).digest()), 'CA file hashes differ between A and B.')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sync', action='store_true', help='Regenerate safe examples and documentation tables only.')
    parser.add_argument('--role', choices=['source', 'monitor'])
    parser.add_argument('--env', type=Path)
    parser.add_argument('--source-env', type=Path)
    parser.add_argument('--monitor-env', type=Path)
    parser.add_argument('--source-ca', type=Path)
    parser.add_argument('--monitor-ca', type=Path)
    args = parser.parse_args(argv)
    pair = args.source_env is not None or args.monitor_env is not None
    if bool(args.role) != bool(args.env) or (pair and (not args.source_env or not args.monitor_env)):
        parser.error('Use --role with --env, or both --source-env and --monitor-env.')
    if args.role and pair or args.sync and (args.role or pair):
        parser.error('Choose exactly one mode: repository, --sync, one env, or env pair.')
    if bool(args.source_ca) != bool(args.monitor_ca) or (args.source_ca and not pair):
        parser.error('CA comparison requires an env pair and both --source-ca/--monitor-ca.')
    try:
        c = load_contract()
        check_repo(c, sync=args.sync)
        if args.role:
            validate_env(c, args.role, parse_env(args.env))
            print(f'PASS: {args.role} env matches contract {c["contract_version"]}; no values printed.')
        elif pair:
            validate_pair(c, parse_env(args.source_env), parse_env(args.monitor_env))
            if args.source_ca:
                check_ca_pair(args.source_ca, args.monitor_ca)
            print('PASS: env pair matches contract; source token matches; no values printed.')
            print('CA copy hashes compared.' if args.source_ca else 'CA file contents were not compared; provide both CA flags to check copies.')
        else:
            print(f'PASS: contract {c["contract_version"]}, role templates and documentation tables agree.')
        print('Scope: offline configuration only; service, TLS trust/SAN and event delivery still require VM tests.')
        return 0
    except (ContractError, OSError) as exc:
        # ContractError messages are constructed from safe labels, never raw env lines/values.
        print('FAIL: ' + (str(exc) if isinstance(exc, ContractError) else 'Required repository file cannot be read.'), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
