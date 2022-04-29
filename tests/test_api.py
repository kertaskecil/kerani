from starlette.testclient import TestClient
from starlette import status
from kerani.api import app


def test_ping_check():
    client = TestClient(app)
    resp = client.get("/ping")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"status": "ok"}


def test_publish_events():
    events1 = {
        "identifier": {
            "topic": "test-kerani-topic",
            "group": "test-kerani-group",
        },
        "properties": {
            "name": "category::event",
            "app_name": "simple-app",
            "platform": "web-desktop",
            "type": "impression",
        },
    }
    events2 = {
        "identifier": {
            "topic": "test-kerani-topic",
            "group": "test-kerani-group",
        },
        "properties": {
            "name": "category::event",
            "app_name": "simple-app",
            "platform": "web-desktop",
            "type": "click",
        },
    }
    payload = {
        "events": [
            events1,
            events2,
        ]
    }
    with TestClient(app) as client:
        resp = client.post("/api/v1/events", json=payload)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": "published"}


def test_publish_event_when_key_not_found():
    payload = {"others": "value"}
    with TestClient(app) as client:
        resp = client.post("/api/v1/events", json=payload)
        expected_resp = {"status": "error", "detail": "events not found"}
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json() == expected_resp


def test_publish_event_when_payload_not_valid_json():
    with TestClient(app) as client:
        resp = client.post("/api/v1/events")
        expected_resp = {"status": "error", "detail": "Unable to parse body"}
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.json() == expected_resp
