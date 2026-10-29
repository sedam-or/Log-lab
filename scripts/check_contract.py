"""CLI entrypoint for the shared contract validator."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from loglab.contract import (
    ROOT, START, END, ContractError, load_contract, require, validate_contract,
    role_specs, render_env, render_tables, check_repo, parse_env, validate_env,
    validate_pair, check_ca_pair, main,
)
if __name__ == "__main__":
    raise SystemExit(main())
