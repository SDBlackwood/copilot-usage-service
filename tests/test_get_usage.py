import pytest 
from fastapi.testclient import TestClient

def test_get_usage(client):
    response = client.get("/usage")
    assert response.status_code == 200
    assert response.json() == {"usage": [
        {
            "message_id": 123,
            "timestamp": "2021-01-01T00:00:00Z",
            "report_name": "Report 1",
            "credits_used": 100
        },
        {
            "message_id": 124,
            "timestamp": "2021-01-01T00:00:00Z",
            "report_name": "Report 2",
            "credits_used": 200
        }
    ]}
