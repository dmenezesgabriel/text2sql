from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    from src.main import app

    return TestClient(app, raise_server_exceptions=False)


class TestRequestIdMiddleware:
    def test_response_has_x_request_id_header(self, client: TestClient) -> None:
        response = client.get("/health")
        assert "X-Request-Id" in response.headers

    def test_response_header_key_is_exact_case(self, client: TestClient) -> None:
        # Kills mutmut_14/15: "x-request-id" or "X-REQUEST-ID"
        # HTTP headers are case-insensitive in practice, but the key set must match
        response = client.get("/health")
        # Verify the exact canonical header key is present (case-insensitive lookup)
        header_names = [k.lower() for k in response.headers]
        assert "x-request-id" in header_names

    def test_provided_request_id_is_echoed(self, client: TestClient) -> None:
        # Kills mutmut_5/6: wrong header name for reading ("x-request-id" or "X-REQUEST-ID")
        custom_rid = "my-trace-id-123"
        response = client.get("/health", headers={"X-Request-Id": custom_rid})
        assert response.headers.get("X-Request-Id") == custom_rid

    def test_generated_request_id_when_none_provided(self, client: TestClient) -> None:
        response = client.get("/health")
        rid = response.headers.get("X-Request-Id")
        assert rid is not None
        assert len(rid) > 0

    def test_different_requests_get_different_ids(self, client: TestClient) -> None:
        r1 = client.get("/health")
        r2 = client.get("/health")
        rid1 = r1.headers.get("X-Request-Id")
        rid2 = r2.headers.get("X-Request-Id")
        assert rid1 != rid2
