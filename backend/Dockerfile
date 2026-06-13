FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv venv /app/.venv && \
    uv sync --no-dev --frozen --no-editable --python /app/.venv/bin/python

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ src/

ENV PATH="/app/.venv/bin:$PATH"

# Pre-install DuckDB extensions so startup doesn't block on download
RUN python -c "import duckdb; c = duckdb.connect(); c.execute('INSTALL httpfs'); c.close()"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
