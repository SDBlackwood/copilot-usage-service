import pytest
from fastapi.testclient import TestClient
from app.datatypes import UsageResponse
import httpx
from app.settings import Settings
from app.main import app, egress_client


def test_get_usage(client, test_raw_dataclient):
    # Mock the egress client to return a fixture
    # As described here https://fastapi.tiangolo.com/advanced/testing-dependencies/#use-the-appdependency_overrides-attribute
    app.dependency_overrides[egress_client] = lambda: test_raw_dataclient

    try:
        response = client.get("/usage")
        assert response.status_code == 200
    finally:
        # Clean up the override after the test
        app.dependency_overrides.clear()


def test_returns_500_if_upstrea_fails(client, test_raw_dataclient_500):
    app.dependency_overrides[egress_client] = lambda: test_raw_dataclient_500

    try:
        response = client.get("/usage")
        assert response.status_code == 500
        # Check that the error message contains the expected text
        error_detail = response.json()["detail"]
        assert "Failed to fetch billing period data:" in error_detail
        assert "500 Internal Server Error" in error_detail
    finally:
        # Clean up the override after the test
        app.dependency_overrides.clear()


def test_returns_500_if_upstream_data_is_invalid(
    client, test_raw_dataclient_invalid_json
):
    app.dependency_overrides[egress_client] = lambda: test_raw_dataclient_invalid_json

    try:
        response = client.get("/usage")
        assert response.status_code == 500
        # Check that the error message contains the expected text
        error_detail = response.json()["detail"]
        assert "Failed to parse billing period data:" in error_detail
    finally:
        # Clean up the override after the test
        app.dependency_overrides.clear()
