from __future__ import annotations

from typing import Protocol


class ISummarizer(Protocol):
    async def summarize(self, text: str) -> str: ...
