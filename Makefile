PYTHON ?= python3
VENV_PYTHON := .venv/bin/python
ROLE ?= source

LOGLAB_BUNDLE_OUT ?= $(HOME)/loglab-bundle

.PHONY: help check-contract test-contract dev-setup test first-check lab-bundle setup-source setup-monitor container-private container-build container-up container-check container-e2e container-down
help:
	@echo "dev-setup     : siapkan .venv Python 3.13, install lock, jalankan tes fondasi"
	@echo "first-check ROLE=source|monitor : contoh fondasi, bukan aplikasi asli"
	@echo "test          : semua tes yang sudah tersedia"
	@echo "check-contract / test-contract : pemeriksaan aturan konfigurasi"
	@echo "lab-bundle    : (host) buat bundle env/TLS/akun di LOGLAB_BUNDLE_OUT (default ~/loglab-bundle), di luar Git"
	@echo "setup-source  : (VM A) sudo make setup-source LOGLAB_BUNDLE=/folder/bundle [LOGLAB_SKIP_FIREWALL=1]"
	@echo "setup-monitor : (VM B) sudo make setup-monitor LOGLAB_BUNDLE=/folder/bundle [LOGLAB_SKIP_FIREWALL=1]"
	@echo "container-private : (lab) buat folder privat uji di LOGLAB_PRIVATE_DIR (default ~/loglab-private, di luar Git)"
	@echo "container-build / container-up / container-check / container-down : Modul 7, dua service container"
	@echo "container-e2e : build, start, health, login, dan cek event di Monitor"

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

lab-bundle:
	$(PYTHON) scripts/make_lab_bundle.py --out "$(LOGLAB_BUNDLE_OUT)"

setup-source:
	bash deployment/source/setup.sh

setup-monitor:
	bash deployment/monitor/setup.sh

LOGLAB_PRIVATE_DIR ?= $(HOME)/loglab-private
COMPOSE := docker compose -f deployment/container/compose.yaml

container-private:
	bash deployment/container/make-private.sh "$(LOGLAB_PRIVATE_DIR)"

container-build:
	LOGLAB_PRIVATE_DIR="$(LOGLAB_PRIVATE_DIR)" $(COMPOSE) build

container-up:
	LOGLAB_PRIVATE_DIR="$(LOGLAB_PRIVATE_DIR)" $(COMPOSE) up -d

container-check:
	LOGLAB_PRIVATE_DIR="$(LOGLAB_PRIVATE_DIR)" $(COMPOSE) ps

container-e2e:
	LOGLAB_PRIVATE_DIR="$(LOGLAB_PRIVATE_DIR)" bash deployment/container/smoke-e2e.sh

container-down:
	LOGLAB_PRIVATE_DIR="$(LOGLAB_PRIVATE_DIR)" $(COMPOSE) down
