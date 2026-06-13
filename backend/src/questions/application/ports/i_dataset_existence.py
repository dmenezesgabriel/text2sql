from __future__ import annotations

from typing import Protocol

from src.shared.domain.base import EntityId


class IDatasetExistence(Protocol):
    def exists(self, dataset_id: EntityId) -> bool: ...
