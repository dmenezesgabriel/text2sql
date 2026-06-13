from __future__ import annotations

from src.shared.infrastructure.console_notifier import ConsoleNotifier


class TestConsoleNotifier:
    def test_notify_prints_message(self, capsys) -> None:
        notifier = ConsoleNotifier()
        notifier.notify("hello world")
        captured = capsys.readouterr()
        assert "hello world" in captured.out
        assert "[NOTIFICATION]" in captured.out

    def test_instantiate(self) -> None:
        notifier = ConsoleNotifier()
        assert notifier is not None
