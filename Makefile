PYTHON ?= python3

.PHONY: help check-contract test-contract
help:
	@echo "check-contract : periksa kontrak, template dan tabel dokumentasi"
	@echo "test-contract  : jalankan tes pemeriksa kontrak"
	@echo "setup-source / setup-monitor belum diimplementasikan"

check-contract:
	$(PYTHON) scripts/check_contract.py

test-contract:
	$(PYTHON) -m unittest discover -s tests -p test_contract.py -v
