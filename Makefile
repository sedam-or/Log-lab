PYTHON ?= python3
VENV_PYTHON := .venv/bin/python
ROLE ?= source

.PHONY: help check-contract test-contract dev-setup test first-check
help:
	@echo "dev-setup     : siapkan .venv Python 3.13, install lock, jalankan tes fondasi"
	@echo "first-check ROLE=source|monitor : contoh fondasi, bukan aplikasi asli"
	@echo "test          : semua tes yang sudah tersedia"
	@echo "check-contract / test-contract : pemeriksaan aturan konfigurasi"
	@echo "setup-source / setup-monitor belum diimplementasikan; tugas anggota"

check-contract:
	$(PYTHON) scripts/check_contract.py

test-contract:
	$(PYTHON) -m unittest discover -s tests -p test_contract.py -v

dev-setup:
	$(PYTHON) scripts/dev_setup.py --python "$(PYTHON)"

test:
	$(VENV_PYTHON) -m unittest discover -s tests -v

first-check:
	$(VENV_PYTHON) scripts/first_check.py --role "$(ROLE)"
