.DEFAULT_GOAL := help
PY ?= python3

VENV     := .venv
PIP      := $(VENV)/bin/pip
PYTHON   := $(VENV)/bin/python
MKDOCS   := $(VENV)/bin/mkdocs
PYTEST   := $(VENV)/bin/pytest

.PHONY: help install docs-install test docs serve docs-strict clean

help:
	@echo "Targets:"
	@echo "  install        Create $(VENV) and install runtime deps (requirements.txt)"
	@echo "  docs-install   Install MkDocs Material into $(VENV) for the docs site"
	@echo "  test           Run pytest"
	@echo "  docs           Build the MkDocs site into ./site"
	@echo "  docs-strict    Build with --strict (fails on warnings; CI mode)"
	@echo "  serve          Serve the docs locally at http://127.0.0.1:8000"
	@echo "  clean          Remove build artefacts and caches"

$(VENV)/bin/activate:
	$(PY) -m venv $(VENV)
	$(PIP) install -U pip

install: $(VENV)/bin/activate
	$(PIP) install -r requirements.txt

docs-install: $(VENV)/bin/activate
	$(PIP) install "mkdocs>=1.6" "mkdocs-material>=9.5" "mkdocs-material-extensions>=1.3" "pymdown-extensions>=10.7"

test: install
	$(PYTEST)

docs: docs-install
	$(MKDOCS) build

docs-strict: docs-install
	$(MKDOCS) build --strict

serve: docs-install
	$(MKDOCS) serve

clean:
	rm -rf site .pytest_cache .ruff_cache .mypy_cache build dist *.egg-info
	find . -name __pycache__ -type d -exec rm -rf {} +
