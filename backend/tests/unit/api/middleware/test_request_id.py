import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.middleware.request_id import REQUEST_ID_HEADER, RequestIDMiddleware


@pytest.fixture
def client():
    """Minimal app with only RequestIDMiddleware for isolated testing."""
    app = FastAPI()
    app.add_middleware(RequestIDMiddleware)

    @app.get("/ping")
    async def ping():
        return {}

    return TestClient(app)


def test_generates_request_id_when_absent(client):
    response = client.get("/ping")
    assert REQUEST_ID_HEADER in response.headers
    assert len(response.headers[REQUEST_ID_HEADER]) > 0


def test_preserves_existing_request_id(client):
    existing_id = "my-custom-id-abc"
    response = client.get("/ping", headers={REQUEST_ID_HEADER: existing_id})
    assert response.headers[REQUEST_ID_HEADER] == existing_id


def test_generated_id_is_unique(client):
    id_1 = client.get("/ping").headers[REQUEST_ID_HEADER]
    id_2 = client.get("/ping").headers[REQUEST_ID_HEADER]
    assert id_1 != id_2
