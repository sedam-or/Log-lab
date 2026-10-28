# Repository Guidelines

## Project Structure

This repository is the shared LogLab workspace for Source VM A and Monitor VM B. Follow the course layout: application code in `src/`, tests in `tests/`, requirements in `docs/requirements/`, architecture in `docs/architecture/`, interface contracts in `docs/interface-contracts/`, safe templates in `config/`, development helpers in `scripts/`, and guest provisioning in `deployment/`.

Start with `README.md`, then read `docs/architecture/BASELINE.md` and the relevant task in `docs/TASKS.md`. Preserve the workspace's existing documents outside this repository. Do not copy their credentials, private paths, or raw evidence into Git.

## Current Development Status

Only documentation and directory guidance are currently published. Application code, dependency locks, setup targets, and tests are pending. Commands such as `make setup-source` describe planned interfaces until their implementation is verified. Never report them as available or tested prematurely.

## Implementation and Collaboration

Target Debian 13 amd64 guests; record the exact ISO and checksum before installation. Windows 11 is the final VMware integration host. Source and Monitor use the same repository and an agreed compatible commit or release tag.

Follow `CONTRIBUTING.md`. Members change their assigned role files on short-lived branches. Shared schemas, locks, root Makefile, and requirements need coordinated review. Preserve requirement IDs and distinguish proposed behavior from implemented and verified behavior.

## Style and Verification

Use clear Indonesian documentation and connected explanations. Python follows four-space indentation, `snake_case` functions/modules, and `PascalCase` classes. Planned tests use `unittest` and `test_*.py` names. Verify changes with checks appropriate to the files actually changed; document results honestly.

## Access and Evidence

SSH is recommended for convenient command copy-paste from the host. Guest console is an alternative. Application traffic uses HTTPS between A and B. Never commit secrets, databases, VM images, or private operational logs. A VMware screenshot must be captured from the actual VMware display; label SSH output as terminal evidence.
