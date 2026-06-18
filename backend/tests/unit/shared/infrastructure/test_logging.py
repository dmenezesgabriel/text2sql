from __future__ import annotations

import json
import logging
import sys

from src.shared.infrastructure.logging import REQUEST_ID, _JsonFormatter, setup_logging


class TestJsonFormatter:
    def _make_record(
        self,
        msg: str = "test message",
        level: int = logging.INFO,
        name: str = "test.logger",
        exc_info: object = None,
    ) -> logging.LogRecord:
        return logging.LogRecord(
            name=name,
            level=level,
            pathname="",
            lineno=0,
            msg=msg,
            args=(),
            exc_info=exc_info,
        )

    def test_format_includes_required_fields(self) -> None:
        record = self._make_record()
        output = json.loads(_JsonFormatter().format(record))
        assert output["level"] == "INFO"
        assert output["logger"] == "test.logger"
        assert output["msg"] == "test message"
        assert "ts" in output

    def test_format_includes_request_id_when_set(self) -> None:
        token = REQUEST_ID.set("req-abc-123")
        try:
            output = json.loads(_JsonFormatter().format(self._make_record()))
            assert output["request_id"] == "req-abc-123"
        finally:
            REQUEST_ID.reset(token)

    def test_format_omits_request_id_when_not_set(self) -> None:
        # Ensure no stale value from other tests
        token = REQUEST_ID.set("")
        try:
            output = json.loads(_JsonFormatter().format(self._make_record()))
            assert "request_id" not in output
        finally:
            REQUEST_ID.reset(token)

    def test_format_includes_exc_as_string_when_exc_info_set(self) -> None:
        try:
            raise ValueError("boom")
        except ValueError:
            exc_info = sys.exc_info()
        record = self._make_record(level=logging.ERROR, exc_info=exc_info)
        output = json.loads(_JsonFormatter().format(record))
        assert "exc" in output
        assert "ValueError" in str(output["exc"])

    def test_format_omits_exc_when_no_exception(self) -> None:
        output = json.loads(_JsonFormatter().format(self._make_record()))
        assert "exc" not in output

    def test_format_includes_extra_fields(self) -> None:
        record = self._make_record()
        record.conversation_id = "conv-xyz"  # type: ignore[attr-defined]
        output = json.loads(_JsonFormatter().format(record))
        assert output["conversation_id"] == "conv-xyz"

    def test_format_ts_field_is_parseable_datetime(self) -> None:
        from datetime import datetime

        record = self._make_record()
        output = json.loads(_JsonFormatter().format(record))
        assert isinstance(output["ts"], str)
        datetime.fromisoformat(output["ts"])  # raises if not valid

    def test_format_ts_is_utc_aware(self) -> None:
        # Kills mutmut_4: datetime.now(None) produces naive datetime, no timezone offset
        record = self._make_record()
        output = json.loads(_JsonFormatter().format(record))
        # UTC-aware ISO strings contain "+00:00" or "Z"
        assert "+" in output["ts"] or output["ts"].endswith("Z")

    def test_format_excludes_underscore_private_fields(self) -> None:
        record = self._make_record()
        record.__dict__["_private"] = "secret"
        output = json.loads(_JsonFormatter().format(record))
        assert "_private" not in output

    def test_format_includes_non_stdlib_extra_fields(self) -> None:
        record = self._make_record()
        record.__dict__["conversation_id"] = "abc-123"
        output = json.loads(_JsonFormatter().format(record))
        assert output.get("conversation_id") == "abc-123"


class TestSetupLogging:
    def test_configures_json_formatter_on_root_logger(self) -> None:
        setup_logging(level="DEBUG")
        root = logging.getLogger()
        assert any(isinstance(h.formatter, _JsonFormatter) for h in root.handlers)

    def test_sets_requested_level(self) -> None:
        setup_logging(level="WARNING")
        assert logging.getLogger().level == logging.WARNING

    def test_default_level_is_info(self) -> None:
        setup_logging()
        assert logging.getLogger().level == logging.INFO

    def test_force_true_replaces_existing_handlers(self) -> None:
        import io

        dummy_handler = logging.StreamHandler(io.StringIO())
        logging.root.addHandler(dummy_handler)
        setup_logging(level="DEBUG")
        # force=True means basicConfig replaces, so only one handler from setup_logging
        assert any(isinstance(h.formatter, _JsonFormatter) for h in logging.root.handlers)
        # The dummy handler should have been replaced
        assert dummy_handler not in logging.root.handlers

    def test_uvicorn_access_filter_installed(self) -> None:
        setup_logging()
        uvicorn_logger = logging.getLogger("uvicorn.access")
        from src.shared.infrastructure.logging import _HealthCheckFilter

        assert any(isinstance(f, _HealthCheckFilter) for f in uvicorn_logger.filters)

    def test_uvicorn_access_filter_installed_on_correct_logger(self) -> None:
        # Kills mutmut_13/14/15: filter goes to wrong logger (None/XX/uppercase)
        # Ensure uvicorn.access has the filter, while root does NOT have it from this call
        from src.shared.infrastructure.logging import _HealthCheckFilter

        uvicorn_logger = logging.getLogger("uvicorn.access")
        uvicorn_logger.filters.clear()
        setup_logging()
        assert any(isinstance(f, _HealthCheckFilter) for f in uvicorn_logger.filters)
        # Root logger should NOT have a _HealthCheckFilter (it would if mutmut_13 fired)
        root_logger = logging.getLogger()
        assert not any(isinstance(f, _HealthCheckFilter) for f in root_logger.filters)

    def test_uvicorn_access_filter_is_health_check_filter_instance(self) -> None:
        # Kills mutmut_12: addFilter(None) — None is not a _HealthCheckFilter
        from src.shared.infrastructure.logging import _HealthCheckFilter

        uvicorn_logger = logging.getLogger("uvicorn.access")
        uvicorn_logger.filters.clear()
        setup_logging()
        assert any(isinstance(f, _HealthCheckFilter) for f in uvicorn_logger.filters)
