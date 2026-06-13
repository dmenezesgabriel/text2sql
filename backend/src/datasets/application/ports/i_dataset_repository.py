from __future__ import annotations

from typing import Protocol

from src.shared.domain.base import EntityId
from src.datasets.domain.entities import Dataset, Datasets


class IDatasetRepository(Protocol):
    async def save(self, dataset: Dataset) -> None: ...

    async def load(self, dataset_id: EntityId) -> Dataset | None: ...

    async def delete(self, dataset_id: EntityId) -> None: ...

    async def find_all(self) -> Datasets: ...
