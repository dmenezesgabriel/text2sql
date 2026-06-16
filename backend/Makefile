UV_EXCLUDE_NEWER ?= $(shell date -d '7 days ago' +%Y-%m-%dT00:00:00Z)

.DEFAULT_GOAL := all

.PHONY: check test mutate sync lock all

check:
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run ruff check src/
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run ruff format --check src/
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run pyright src/
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run deptry .
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run vulture src/ vulture_whitelist.py --ignore-decorators "@router.*,@app.*"
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run radon cc src/ -a
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run radon mi src/
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run semgrep --config=semgrep_rules/ src/ tests/
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run lint-imports --config .import_linter.cfg
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run python scripts/check_test_coverage.py

test:
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run pytest --cov=src --cov-report=term-missing

mutate:
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run mutmut run

lock:
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv lock

sync: lock
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv sync --all-extras

all: check test
