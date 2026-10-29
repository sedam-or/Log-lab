"""Create the local Python 3.13 development environment; no VM/service changes."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def python_version(executable: str) -> tuple[int, int]:
    result = subprocess.run([executable, '-c', 'import json,sys; print(json.dumps(list(sys.version_info[:2])))'],
                            check=True, text=True, capture_output=True)
    return tuple(json.loads(result.stdout))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', default='python3')
    args = parser.parse_args()
    try:
        executable = shutil.which(args.python)
        if not executable or python_version(executable) != (3, 13):
            raise ValueError('Gunakan Python 3.13. Di Debian 13: sudo apt install python3 python3-venv')
        venv = ROOT / '.venv'
        vpython = venv / 'bin/python'
        if venv.exists():
            if not vpython.is_file() or python_version(str(vpython)) != (3, 13):
                raise ValueError('.venv sudah ada tetapi bukan Python 3.13; periksa lalu simpan/rename sendiri sebelum mencoba lagi.')
        else:
            subprocess.run([executable, '-m', 'venv', str(venv)], check=True)
        subprocess.run([str(vpython), '-m', 'pip', 'install', '--disable-pip-version-check', '--require-hashes', '-r', str(ROOT/'requirements.lock')], check=True)
        subprocess.run([str(vpython), '-m', 'pip', 'install', '--disable-pip-version-check', '--no-deps', '--no-build-isolation', '-e', str(ROOT)], check=True)
        subprocess.run([str(vpython), '-m', 'pip', 'check'], check=True)
        subprocess.run([str(vpython), '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=ROOT, check=True)
        print('SIAP CODING: environment dan tes fondasi lulus. Aplikasi peran belum ditulis.')
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print('SETUP BELUM SELESAI: '+str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
