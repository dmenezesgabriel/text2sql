UV_EXCLUDE_NEWER ?= $(shell date -d '7 days ago' +%Y-%m-%dT00:00:00Z)

.DEFAULT_GOAL := all

.PHONY: check test mutate sync lock all

check:
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run ruff check src/
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run ruff format --check src/
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run deptry .
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run vulture src/
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run radon cc src/ -a
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run radon mi src/
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run semgrep --config=semgrep_rules/ src/
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run lint-imports --config .import_linter.cfg

test:
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run pytest -v

mutate:
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv run mutmut run

lock:
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv lock

sync: lock
	UV_EXCLUDE_NEWER=$(UV_EXCLUDE_NEWER) uv sync --all-extras

all: check test
