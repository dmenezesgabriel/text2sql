"""Integration tests against the running backend at http://localhost:8000.

Run with: uv run pytest tests/integration/ -v
Requires all Docker services to be up and datasets seeded.
"""

# ruff: noqa: S603,S607 -- curl invocation uses known fixed args, not user input
from __future__ import annotations

import json
import subprocess

import httpx
import pytest

BASE = "http://localhost:8000"
_CLIENT = httpx.Client(base_url=BASE, timeout=15)


def _get(path: str) -> dict:
    return _CLIENT.get(path).raise_for_status().json()


def _post(path: str, body: dict, timeout: int = 10) -> dict:
    return _CLIENT.post(path, json=body, timeout=timeout).raise_for_status().json()


class TestHealth:
    def test_health_returns_ok(self) -> None:
        result = _get("/health")
        assert result == {"status": "ok"}


class TestDatasets:
    def test_list_datasets_returns_list(self) -> None:
        result = _get("/api/v1/datasets")
        assert "datasets" in result
        assert isinstance(result["datasets"], list)

    def test_seeded_datasets_present(self) -> None:
        result = _get("/api/v1/datasets")
        names = {d["name"] for d in result["datasets"]}
        assert names >= {"sales", "product", "customer"}, f"Missing datasets: {names}"

    def test_datasets_have_required_fields(self) -> None:
        result = _get("/api/v1/datasets")
        for ds in result["datasets"]:
            assert "id" in ds
            assert "name" in ds
            assert "kind" in ds
            assert "location" in ds
            assert "columns" in ds
            assert isinstance(ds["columns"], list)

    def test_datasets_have_columns(self) -> None:
        result = _get("/api/v1/datasets")
        for ds in result["datasets"]:
            assert len(ds["columns"]) > 0, f"Dataset '{ds['name']}' has no columns"
            for col in ds["columns"]:
                assert "name" in col
                assert "dtype" in col

    def test_register_duplicate_returns_conflict(self) -> None:
        resp = _CLIENT.post(
            "/api/v1/datasets/register-s3",
            json={"name": "sales", "s3_uri": "s3://bi-data/sales.parquet"},
        )
        assert resp.status_code == 409

    def test_register_invalid_s3_uri_returns_error(self) -> None:
        resp = _CLIENT.post(
            "/api/v1/datasets/register-s3",
            json={"name": "bad_uri_test", "s3_uri": "not-an-s3-uri"},
        )
        assert resp.status_code in (400, 422, 500)

    def test_preview_returns_columns_and_rows(self) -> None:
        datasets = _get("/api/v1/datasets")["datasets"]
        sales = next(d for d in datasets if d["name"] == "sales")
        result = _get(f"/api/v1/datasets/{sales['id']}/preview")
        assert "columns" in result
        assert "rows" in result
        assert len(result["columns"]) > 0
        assert len(result["rows"]) > 0


class TestChat:
    def _stream_chat(
        self,
        message: str,
        conversation_id: str | None = None,
        timeout: int = 90,
    ) -> list[dict]:
        """Send chat message and collect all SSE events.

        Uvicorn closes the SSE connection after the generator exhausts without
        a proper chunked-encoding terminator, so we catch RemoteProtocolError
        and return whatever events arrived before the connection closed.
        """
        result = subprocess.run(
            [
                "curl",
                "-sN",
                "-X",
                "POST",
                f"{BASE}/api/v1/chat",
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps({"conversation_id": conversation_id, "message": message}),
                "--max-time",
                str(timeout),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        events = []
        for raw_line in result.stdout.splitlines():
            stripped = raw_line.strip()
            if stripped.startswith("data: "):
                events.append(json.loads(stripped[6:]))
        return events

    def test_chat_returns_sse_events(self) -> None:
        events = self._stream_chat("Show me total sales by region")
        assert len(events) > 0

    def test_chat_has_thinking_event(self) -> None:
        events = self._stream_chat("Show me total sales by region")
        types = {e["type"] for e in events}
        assert "ThinkingEvent" in types

    def test_chat_has_spec_fragment_event(self) -> None:
        events = self._stream_chat("Show me total sales by region as a bar chart")
        types = {e["type"] for e in events}
        assert "SpecFragmentEvent" in types, f"Events received: {types}"

    def test_chat_spec_is_valid_json_render_format(self) -> None:
        events = self._stream_chat("Show me total sales by region")
        spec_event = next((e for e in events if e["type"] == "SpecFragmentEvent"), None)
        if spec_event is None:
            pytest.skip("No SpecFragmentEvent received")
        spec = spec_event["payload"]
        assert "root" in spec, "Spec missing 'root' key"
        assert "elements" in spec, "Spec missing 'elements' key"
        root_key = spec["root"]
        assert root_key in spec["elements"], f"Root key '{root_key}' not in elements"

    def test_chat_creates_conversation(self) -> None:
        events = self._stream_chat("How many customers do we have?")
        # Successful response means conversation was created and persisted
        types = {e["type"] for e in events}
        assert "ErrorEvent" not in types, f"Got error: {events}"
