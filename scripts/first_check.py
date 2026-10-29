"""Small runnable example that verifies foundations without a live Monitor."""
from pathlib import Path
import argparse
import tempfile

from loglab.config import Settings
from loglab.db import connect, initialize_source, initialize_monitor
from loglab.events import validate_event
from loglab.testing import ReceiverStub, fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--role', required=True, choices=['source', 'monitor'])
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='loglab-first-check-') as tmp:
        settings = Settings.for_test(args.role, Path(tmp))
        (initialize_source if args.role=='source' else initialize_monitor)(settings.db_path)
        event = fixture('login-success'); validate_event(event)
        receiver = ReceiverStub(settings.source_token)
        code, first = receiver.post('/api/v1/events', event, settings.source_token)
        _, second = receiver.post('/api/v1/events', event, settings.source_token)
        if code != 200 or first['status'] != 'stored' or second['status'] != 'duplicate' or len(receiver.events) != 1:
            raise SystemExit('FAIL: receiver simulation did not match the shared fixture')
        with connect(settings.db_path) as db:
            if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise SystemExit('FAIL: temporary DB integrity')
    print(f'PASS fondasi {args.role}: Settings test, DB sementara, fixture dan receipt simulasi sesuai.')
    print('SIMULASI: belum menjalankan Source/Monitor asli, HTTPS, analisis atau dashboard.')


if __name__ == '__main__':
    main()
