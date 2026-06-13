from __future__ import annotations

from src.datasets.domain.value_objects import FileFormat, StorageUri
from src.datasets.infrastructure.s3_ingester import S3Ingester


class TestS3Ingester:
    def test_instantiate(self) -> None:
        ingester = S3Ingester()
        assert ingester is not None

    async def test_ingest_yields_placeholder_column(self) -> None:
        ingester = S3Ingester()
        columns = []
        async for col in ingester.ingest(
            uri=StorageUri("s3://bucket/data.parquet"),
            file_format=FileFormat.PARQUET,
        ):
            columns.append(col)
        assert len(columns) == 1
        assert columns[0]._name == "placeholder"
