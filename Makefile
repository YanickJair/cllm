PY := python3
VENV := .venv
VENV_PY := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

.PHONY: help venv install-dev lint format typecheck test coverage build dist smoke-install \
        publish-testpypi publish-pypi clean

help:
	@echo "Makefile targets:"
	@echo "  make venv            -> create virtualenv and upgrade pip"
	@echo "  make install-dev     -> install dev dependencies (ruff, mypy, pytest, coverage, hatch, twine)"
	@echo "  make lint            -> run ruff checks"
	@echo "  make format          -> run ruff format"
	@echo "  make typecheck       -> run mypy"
	@echo "  make test            -> run pytest"
	@echo "  make coverage        -> run coverage and generate html report"
	@echo "  make build           -> build wheel + sdist with hatch"
	@echo "  make dist            -> list files in dist/"
	@echo "  make smoke-install   -> install built wheel into a fresh venv and sanity-check import"
	@echo "  make publish-testpypi-> upload artifacts to TestPyPI (requires TEST_PYPI_API_TOKEN)"
	@echo "  make publish-pypi    -> upload artifacts to PyPI (requires PYPI_API_TOKEN)"
	@echo "  make clean           -> remove build artifacts and temp venvs"

# Create virtualenv and upgrade pip/setuptools/wheel
venv:
	@if [ ! -d "$(VENV)" ]; then $(PY) -m venv $(VENV); fi
	$(VENV_PY) -m pip install --upgrade pip setuptools wheel

# Install dev tools. If you keep a requirements-dev.txt, make it available and it will be used.
install-dev: venv
	@if [ -f requirements-dev.txt ]; then \
		$(VENV_PIP) install -r requirements-dev.txt; \
	else \
		$(VENV_PIP) install hatch ruff mypy pytest coverage twine; \
	fi

lint: venv
	$(VENV_PIP) install ruff >/dev/null 2>&1 || true
	$(VENV_PY) -m ruff check .

format: venv
	$(VENV_PIP) install ruff >/dev/null 2>&1 || true
	$(VENV_PY) -m ruff format .

typecheck: venv
	$(VENV_PIP) install mypy >/dev/null 2>&1 || true
	$(VENV_PY) -m mypy .

test: venv
	$(VENV_PIP) install pytest >/dev/null 2>&1 || true
	$(VENV_PY) -m pytest -q

coverage: venv
	$(VENV_PIP) install coverage pytest >/dev/null 2>&1 || true
	$(VENV_PY) -m coverage run -m pytest
	$(VENV_PY) -m coverage report -m
	$(VENV_PY) -m coverage html
	@echo "HTML report written to htmlcov/index.html (open in browser)"

# Build via hatch (wheel + sdist)
build: venv
	$(VENV_PIP) install hatch >/dev/null 2>&1 || true
	$(VENV_PY) -m hatchling.build

# List distribution artifacts
dist: build
	@ls -l dist || true


# Publish (twine) — requires env vars:
#   TEST_PYPI_API_TOKEN  for TestPyPI (use make publish-testpypi)
#   PYPI_API_TOKEN       for PyPI (use make publish-pypi)
publish-testpypi: dist
ifndef TEST_PYPI_API_TOKEN
	$(error TEST_PYPI_API_TOKEN is undefined — export it before running)
endif
	. $(VENV)/bin/activate; \
	twine upload --repository-url https://test.pypi.org/legacy/ -u __token__ -p "$$TEST_PYPI_API_TOKEN" dist/*

publish-pypi: dist
ifndef PYPI_API_TOKEN
	$(error PYPI_API_TOKEN is undefined — export it before running)
endif
	. $(VENV)/bin/activate; \
	twine upload -u __token__ -p "$$PYPI_API_TOKEN" dist/*

clean:
	@echo "Cleaning build artifacts and caches..."
	@rm -rf build dist *.egg-info .venv_test_install .venv htmlcov
	@find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf || true
