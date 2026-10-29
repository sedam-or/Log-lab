"""Settings shared by both roles; production names/values follow contract.json."""
from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import secrets
from typing import Mapping

from .contract import load_contract, validate_env


@dataclass(frozen=True)
class Settings:
    role: str
    contract_version: str
    bind_host: str
    port: int
    db_path: Path
    source_id: str
    source_token: str = field(repr=False)
    ca_bundle: Path
    certfile: Path
    keyfile: Path
    monitor_url: str = ''
    pseudonym_key: bytes | None = field(default=None, repr=False)
    model_path: Path | None = None
    operator_username: str = ''
    operator_password_hash: str = field(default='', repr=False)
    sender_lock: Path | None = None
    test_mode: bool = False

    @classmethod
    def from_env(cls, role: str, environ: Mapping[str, str] | None = None) -> 'Settings':
        supplied = os.environ if environ is None else environ
        values = {k: v for k, v in supplied.items() if k.startswith('LOGLAB_')}
        c = load_contract()
        validate_env(c, role, values)
        return cls(
            role=role, contract_version=values['LOGLAB_CONTRACT_VERSION'],
            bind_host=values['LOGLAB_BIND_HOST'], port=int(values['LOGLAB_PORT']),
            db_path=Path(values['LOGLAB_DB_PATH']), source_id=values['LOGLAB_SOURCE_ID'],
            source_token=values['LOGLAB_SOURCE_TOKEN'], ca_bundle=Path(values['LOGLAB_CA_BUNDLE']),
            certfile=Path(values['LOGLAB_TLS_CERT']), keyfile=Path(values['LOGLAB_TLS_KEY']),
            monitor_url=values.get('LOGLAB_MONITOR_URL', ''),
            pseudonym_key=bytes.fromhex(values['LOGLAB_PSEUDONYM_KEY']) if role == 'source' else None,
            model_path=Path(values['LOGLAB_MODEL_PATH']) if role == 'monitor' else None,
            operator_username=values.get('LOGLAB_OPERATOR_USERNAME', ''),
            operator_password_hash=values.get('LOGLAB_OPERATOR_PASSWORD_HASH', ''),
            sender_lock=Path(values['LOGLAB_SENDER_LOCK']) if role == 'source' else None,
        )

    @classmethod
    def for_test(cls, role: str, directory: Path, *, source_token: str | None = None) -> 'Settings':
        """Explicit isolated test settings, never a production env template."""
        c = load_contract()
        if role not in c['roles']:
            raise ValueError('role must be source or monitor')
        directory = Path(directory) / role
        return cls(
            role=role, contract_version=c['contract_version'], bind_host='127.0.0.1', port=0,
            db_path=directory / (role + '.sqlite3'), source_id=c['identity']['source_id'],
            source_token=source_token or secrets.token_hex(32),
            ca_bundle=directory / 'test-ca.crt', certfile=directory / 'test.crt', keyfile=directory / 'test.key',
            monitor_url='https://monitor.test', pseudonym_key=secrets.token_bytes(32) if role == 'source' else None,
            model_path=directory / 'model.json' if role == 'monitor' else None,
            operator_username='operator', sender_lock=directory / 'sender.lock' if role == 'source' else None,
            test_mode=True,
        )
