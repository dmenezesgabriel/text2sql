from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.main import RequestIdMiddleware
from src.shared.infrastructure.logging import REQUEST_ID

_UUID_LEN = 36


def _make_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)

    @app.get("/echo")
    def echo() -> dict[str, str]:
        return {"request_id": REQUEST_ID.get()}

    return app


class TestRequestIdMiddleware:
    def setup_method(self) -> None:
        self.client = TestClient(_make_app())

    def test_propagates_incoming_header(self) -> None:
        resp = self.client.get("/echo", headers={"X-Request-Id": "my-request-id"})
        assert resp.json()["request_id"] == "my-request-id"
        assert resp.headers["X-Request-Id"] == "my-request-id"

    def test_generates_uuid_when_header_absent(self) -> None:
        resp = self.client.get("/echo")
        rid = resp.headers["X-Request-Id"]
        assert len(rid) == _UUID_LEN
        assert resp.json()["request_id"] == rid

    def test_different_requests_get_different_ids(self) -> None:
        rid1 = self.client.get("/echo").headers["X-Request-Id"]
        rid2 = self.client.get("/echo").headers["X-Request-Id"]
        assert rid1 != rid2
