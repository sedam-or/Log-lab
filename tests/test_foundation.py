from pathlib import Path
from copy import deepcopy
import json
import secrets
import sqlite3
import tempfile
import unittest

from loglab.config import Settings
from loglab.contract import ContractError, load_contract, role_specs
from loglab.db import connect, initialize_source, initialize_monitor
from loglab.events import build_event, build_receipt, validate_event, validate_receipt, validate_source_status
from loglab.testing import ReceiverStub, fixture


class FoundationTests(unittest.TestCase):
    def values(self, role):
        out = {}
        for k, rule in role_specs(load_contract(), role).items():
            out[k] = rule['values'][role] if rule['kind']=='fixed' else (
                secrets.token_hex(32) if rule['kind']=='hex64' else 'scrypt$16384$8$1$'+'ab'*16+'$'+'cd'*32)
        return out

    def test_settings_validate_role_scope_and_hide_secrets(self):
        for role in ['source','monitor']:
            values=self.values(role);s=Settings.from_env(role,values)
            self.assertEqual(s.role,role);self.assertEqual(s.port,8443)
            self.assertNotIn(values['LOGLAB_SOURCE_TOKEN'],repr(s))
            self.assertEqual(s.pseudonym_key is None,role=='monitor')
        with self.assertRaises(ContractError):Settings.from_env('monitor',self.values('source'))

    def test_test_settings_are_explicitly_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=Settings.for_test('source',Path(tmp))
            self.assertTrue(s.test_mode)
            self.assertTrue(s.db_path.is_relative_to(Path(tmp)))
            self.assertEqual(s.bind_host,'127.0.0.1')

    def test_shared_fixtures_and_receipt(self):
        for name in ['login-success','login-failure']:validate_event(fixture(name))
        validate_receipt(fixture('stored-receipt'),fixture('login-success'))
        validate_source_status(fixture('source-status'))
        bad=fixture('stored-receipt');bad['event_id']=fixture('login-failure')['event_id']
        with self.assertRaises(ValueError):validate_receipt(bad,fixture('login-success'))

    def test_receiver_duplicate_conflict_and_timeout(self):
        token=secrets.token_hex(32);r=ReceiverStub(token);event=fixture('login-success')
        self.assertEqual(r.post('/api/v1/events',event,token)[1]['status'],'stored')
        self.assertEqual(r.post('/api/v1/events',event,token)[1]['status'],'duplicate')
        self.assertEqual(len(r.events),1)
        changed={k:v for k,v in event.items() if k not in ['event_digest','schema_version']}
        changed['sequence']=3
        altered=build_event(**changed)
        self.assertEqual(r.post('/api/v1/events',altered,token)[0],409)
        self.assertEqual(r.events[(event['source_id'],event['event_id'])],event)
        self.assertEqual(r.post('/api/v1/events',event,'wrong-token')[0],401)
        r.available=False
        with self.assertRaises(TimeoutError):r.post('/api/v1/events',event,token)

    def test_receiver_status_does_not_create_login_event(self):
        token=secrets.token_hex(32);r=ReceiverStub(token);status=fixture('source-status')
        code,body=r.post('/api/v1/source-status',status,token)
        self.assertEqual(code,200);self.assertEqual(body['status'],'accepted')
        self.assertEqual(len(r.events),0);self.assertEqual(len(r.statuses),1)
        status['acknowledged_sequence']=100
        self.assertEqual(r.post('/api/v1/source-status',status,token)[0],422)

    def test_source_schema_preserves_stream_and_rolls_back_transaction(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'source.sqlite3';initialize_source(p)
            with connect(p) as db:stream=db.execute("SELECT value FROM meta WHERE key='stream_id'").fetchone()[0]
            initialize_source(p)
            with connect(p) as db:self.assertEqual(stream,db.execute("SELECT value FROM meta WHERE key='stream_id'").fetchone()[0])
            with self.assertRaises(RuntimeError):
                with connect(p) as db:
                    db.execute('BEGIN IMMEDIATE')
                    db.execute("UPDATE meta SET value='99' WHERE key='next_sequence'")
                    raise RuntimeError('simulated abort')
            with connect(p) as db:self.assertEqual(db.execute("SELECT value FROM meta WHERE key='next_sequence'").fetchone()[0],'1')

    def test_monitor_rejects_same_event_id_in_another_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'monitor.sqlite3';initialize_monitor(p)
            with connect(p) as db:
                status_columns = {row['name'] for row in db.execute('PRAGMA table_info(source_status)')}
            self.assertTrue(set(fixture('source-status')).issubset(status_columns))
            e=fixture('login-success')
            columns='source_id,stream_id,event_id,sequence,occurred_at,event_type,account_token,client_token,reason_code,event_digest,received_at,payload_json'
            values=[e[k] for k in columns.split(',')[:10]]+[e['occurred_at'],json.dumps(e)]
            with connect(p) as db:
                db.execute('INSERT INTO monitor_events('+columns+') VALUES('+','.join('?'*12)+')',values)
                values[1]='44444444-4444-4444-8444-444444444444'
                with self.assertRaises(sqlite3.IntegrityError):db.execute('INSERT INTO monitor_events('+columns+') VALUES('+','.join('?'*12)+')',values)

    def test_newer_database_version_is_not_downgraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'future.sqlite3'
            with connect(p) as db:db.execute('PRAGMA user_version=99')
            with self.assertRaises(sqlite3.DatabaseError):initialize_source(p)

    def test_event_types_and_source_status_counts_reject_invalid_types(self):
        for value in [True,1.0]:
            e=fixture('login-success');e['schema_version']=value
            with self.assertRaises(ValueError):validate_event(e)
        e=fixture('login-success');e['event_type']=[]
        with self.assertRaises(ValueError):validate_event(e)
        status=fixture('source-status');status['pending_count']=True
        with self.assertRaises(ValueError):validate_source_status(status)

    def test_locked_web_test_stack_imports_and_handles_asgi_request(self):
        from fastapi import FastAPI
        import asyncio
        import httpx
        import python_multipart
        app=FastAPI()
        @app.get('/foundation-probe')
        def probe():return {'foundation':'ok'}
        async def request():
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
                self.assertEqual((await client.get('/foundation-probe')).json(),{'foundation':'ok'})
        asyncio.run(request())
