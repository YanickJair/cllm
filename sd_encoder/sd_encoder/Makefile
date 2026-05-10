.PHONY: venv dev dev-release build release clean check

VENV := .venv
PYTHON := $(VENV)/bin/python3
MATURIN := $(VENV)/bin/maturin
MATURIN_ENV := env -u VIRTUAL_ENV PYO3_PYTHON=$(abspath $(PYTHON))

venv:
	uv venv $(VENV)
	uv pip install --python $(PYTHON) maturin

dev: venv
	$(MATURIN_ENV) $(MATURIN) develop

dev-release: venv
	$(MATURIN_ENV) $(MATURIN) develop --release

build: venv
	$(MATURIN_ENV) $(MATURIN) build

release: venv
	$(MATURIN_ENV) $(MATURIN) build --release
