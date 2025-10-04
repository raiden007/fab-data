# files-3/Makefile
.ONESHELL:

# Detect a system Python to create the venv
PY_CMD := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || command -v py 2>/dev/null)
ifeq ($(PY_CMD),)
$(error No Python interpreter found. Install Python 3 and re-run make)
endif

VENV := .venv

# Venv python path per-OS
VPY := $(VENV)/bin/python
ifeq ($(OS),Windows_NT)
	VPY := $(VENV)/Scripts/python.exe
endif
VPIP := $(VPY) -m pip

.PHONY: whichpy venv install run test lint format clean freeze ci shell

whichpy:
	@echo "System Python: $(PY_CMD)"; $(PY_CMD) --version || true
	@echo "Venv Python:   $(VPY) (created after 'make venv')"

venv:
	@echo ">>> Creating virtual env at $(VENV) using: $(PY_CMD)"
	@$(PY_CMD) -m venv $(VENV)

install: venv
	@echo ">>> Installing requirements via venv python"
	@$(VPIP) install --upgrade pip
	@$(VPIP) install -r requirements.txt
	@echo ">>> Done."

run: install
	@echo ">>> Starting Flask app"
	@$(VPY) app.py

test: install
	@echo ">>> Running tests"
	@$(VPY) -m pytest -q

lint: install
	@echo ">>> Linting (ruff) & style check (black/isort)"
	@$(VPY) -m ruff check .
	@$(VPY) -m black --check .
	@$(VPY) -m isort --check-only .

format: install
	@echo ">>> Auto-fixing with ruff/black/isort"
	@$(VPY) -m ruff check . --fix
	@$(VPY) -m black .
	@$(VPY) -m isort .

freeze: install
	@echo ">>> Writing requirements-lock.txt"
	@$(VPIP) freeze > requirements-lock.txt

ci: test

clean:
	@echo ">>> Cleaning caches"
	@rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache *.egg-info
	@echo ">>> Remove venv with: rm -rf $(VENV)"

shell: venv
ifeq ($(OS),Windows_NT)
	@echo "Open PowerShell and run: .\\$(VENV)\\Scripts\\Activate.ps1"
else
	@echo ">>> Spawning shell with venv activated. Exit with Ctrl-D."
	@bash -c '. $(VENV)/bin/activate; exec $$SHELL'
endif
