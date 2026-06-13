from __future__ import annotations

from typing import Protocol

from src.datasets.domain.entities import Dataset, Datasets
from src.shared.domain.base import EntityId


class IDatasetRepository(Protocol):
    def save(self, dataset: Dataset) -> None: ...

    def load(self, dataset_id: EntityId) -> Dataset | None: ...

    def delete(self, dataset_id: EntityId) -> None: ...

    def find_all(self) -> Datasets: ...
