.PHONY: venv dev dev-release build release build-local test-local-build bench profile-load clean check

VENV := .venv
PYTHON := $(VENV)/bin/python3
MATURIN := $(VENV)/bin/maturin
MATURIN_ENV := env -u VIRTUAL_ENV PYO3_PYTHON=$(abspath $(PYTHON))
DIST_DIR := dist

venv:
	uv venv --allow-existing $(VENV)
	uv pip install --python $(PYTHON) maturin

dev: venv
	$(MATURIN_ENV) $(MATURIN) develop

dev-release: venv
	$(MATURIN_ENV) $(MATURIN) develop --release

build: venv
	$(MATURIN_ENV) $(MATURIN) build

release: venv
	$(MATURIN_ENV) $(MATURIN) build --release

build-local: venv
	$(MATURIN_ENV) $(MATURIN) build --release --out $(DIST_DIR)

test-local-build:
	scripts/test_local_build.sh

bench:
	cargo bench --bench load

profile-load:
	cargo run --release --example load_profile
