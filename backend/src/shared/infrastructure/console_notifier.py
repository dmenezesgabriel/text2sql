from __future__ import annotations


class ConsoleNotifier:
    def notify(self, message: str) -> None:
        print(f"[NOTIFICATION] {message}")
