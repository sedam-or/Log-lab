# Repository Guidelines

## Project Structure

This repository is the shared LogLab workspace for Source VM A and Monitor VM B. Application code is in `src/loglab/`, tests in `tests/`, requirements in `docs/requirements/`, architecture in `docs/architecture/`, interface contracts in `docs/interface-contracts/` (source of truth: `config/contract.json`), safe templates in `config/`, helpers in `scripts/`, and guest provisioning in `deployment/<role>/`.

Start with `README.md`, then `docs/ATURAN-SINGKAT.md`, `docs/architecture/BASELINE.md` and the relevant task in `docs/tugas/`. Do not copy credentials, private paths, or raw evidence into Git.

## Source of truth order

When documents disagree: `config/contract.json` > `docs/requirements/srs/*` > `docs/tugas/*` > `CONTRIBUTING.md`. Fix the lower document or raise a contract change; do not silently diverge.

## Branches and environments

Exactly three branches: `dev` (default, development and testing), `staging` (two-VM integration test), `production` (final demo). Promotion is by PR `dev` -> `staging` -> `production` with merge commit, a green CI and at least one other member reviewing. See `CONTRIBUTING.md` and `docs/ENVIRONMENT.md`.

## Current Development Status

Python 3.13 exactly (`make dev-setup` enforces it). Monitor and Source application code, the Monitor deployment and tests exist. Check `docs/tugas/index.md` and `CHANGELOG.md` for the real status of each task. Commands such as `make setup-source` / `make setup-monitor` are reported as available only after their tests pass and they have been run on a VM. Never report planned behavior as verified.

## Implementation and Collaboration

Target Debian 13 amd64 guests. Source and Monitor use the same repository and an agreed compatible commit or release tag. Follow `CONTRIBUTING.md`. Shared schemas, locks, the root Makefile, and requirements need coordinated review. Preserve requirement IDs and distinguish proposed behavior from implemented and verified behavior.

## Style and Verification

Use clear Indonesian documentation. Python follows four-space indentation, `snake_case` functions/modules, and `PascalCase` classes. Tests use `unittest` and `test_*.py`. Run `make check-contract` and `make test` before promoting; document results honestly.

## Access and Evidence

SSH is recommended for command copy-paste from the host; the guest console is an alternative. Application traffic uses HTTPS between A and B. Never commit secrets, databases, VM images, or private operational logs. A VMware screenshot must be captured from the actual VMware display; label SSH output as terminal evidence.
