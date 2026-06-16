from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime

REQUEST_ID: ContextVar[str] = ContextVar("request_id", default="")

# Standard LogRecord attributes to exclude from the extra fields payload.
_STDLIB_ATTRS = frozenset(
    {
        "args",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    },
)


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if rid := REQUEST_ID.get():
            payload["request_id"] = rid
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        for key, val in record.__dict__.items():
            if key not in _STDLIB_ATTRS and not key.startswith("_"):
                payload[key] = val
        return json.dumps(payload)


class _HealthCheckFilter(logging.Filter):
    """Drop uvicorn access-log entries for GET /health (Docker healthcheck noise)."""

    def filter(self, record: logging.LogRecord) -> bool:
        return "GET /health" not in record.getMessage()


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger to emit one JSON object per line to stdout."""
    handler = logging.StreamHandler()
    handler.setFormatter(_JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)
    logging.getLogger("uvicorn.access").addFilter(_HealthCheckFilter())
