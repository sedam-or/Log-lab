"""Compare a downloaded Debian ISO with the official hash recorded in contract."""
from pathlib import Path
import argparse
import hashlib
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from loglab.contract import load_contract


def check_iso(path: Path) -> bool:
    expected = load_contract()['platform']['iso']
    if path.name != expected['filename']:
        raise ValueError('Nama ISO berbeda dari acuan; jangan ganti nama image lain untuk memaksanya cocok.')
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest() == expected['sha256']


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    try:
        if not check_iso(parser.parse_args().iso):
            raise ValueError('SHA-256 ISO berbeda dari acuan resmi.')
        print('PASS: nama dan SHA-256 ISO sesuai acuan resmi.')
    except (OSError, ValueError) as exc:
        print('FAIL: '+str(exc), file=sys.stderr); raise SystemExit(1)
