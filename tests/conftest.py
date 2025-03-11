import pytest
from fastapi.testclient import TestClient
from app.main import app
from http import HTTPStatus
import httpx


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_raw_dataclient():
    # Use a context manager to read and close the file
    with open("tests/assets/current_period_mock.json") as f:
        content = f.read()

    # Mock the client and add the fixture to the response
    return httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(HTTPStatus.OK, content=content)
        )
    )


@pytest.fixture
def test_raw_dataclient_500():
    # From https://www.b-list.org/weblog/2023/dec/08/mock-python-httpx/
    # Mock the client and add the fixture to the response
    return httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                json={"error": "Internal Server Error"},
            )
        )
    )


@pytest.fixture
def test_raw_dataclient_invalid_json():
    # From https://www.b-list.org/weblog/2023/dec/08/mock-python-httpx/
    # Mock the client and add the fixture to the response
    return httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(HTTPStatus.OK, json={"invalid": "json"})
        )
    )
