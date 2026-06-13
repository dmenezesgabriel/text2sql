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


class TestSetupLogging:
    def test_configures_json_formatter_on_root_logger(self) -> None:
        setup_logging(level="DEBUG")
        root = logging.getLogger()
        assert any(isinstance(h.formatter, _JsonFormatter) for h in root.handlers)

    def test_sets_requested_level(self) -> None:
        setup_logging(level="WARNING")
        assert logging.getLogger().level == logging.WARNING
