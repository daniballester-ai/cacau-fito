"""API-level tests for GET /history (see openspec/changes/add-prediction-history, tasks 3.1-3.3)."""
import os

import pytest
from fastapi.testclient import TestClient

from src.inference_service import history, main
from tests.conftest import authenticate

SAMPLE_IMAGES = [
    os.path.join(os.path.dirname(__file__), "..", "samples", "healthy_1.jpg"),
    os.path.join(os.path.dirname(__file__), "..", "samples", "cssvd_1.jpg"),
    os.path.join(os.path.dirname(__file__), "..", "samples", "anthracnose_1.jpg"),
]


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setattr(history, "IMAGES_DIR", str(tmp_path / "history" / "images"))
    monkeypatch.setattr(history, "DB_PATH", str(tmp_path / "history" / "history.db"))
    yield


@pytest.fixture
def client():
    client = TestClient(main.app)
    authenticate(client)
    return client


def _predict(client, image_path):
    with open(image_path, "rb") as f:
        response = client.post("/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
    assert response.status_code == 200
    return response.json()


def test_history_lists_predictions_newest_first(client):
    for image_path in SAMPLE_IMAGES:
        _predict(client, image_path)

    response = client.get("/history", params={"limit": 10, "offset": 0})
    assert response.status_code == 200
    body = response.json()

    assert body["total"] == 3
    assert len(body["items"]) == 3
    created_ats = [item["created_at"] for item in body["items"]]
    assert created_ats == sorted(created_ats, reverse=True)


def test_history_pagination_returns_only_requested_page_and_next_offset(client):
    for image_path in SAMPLE_IMAGES:
        _predict(client, image_path)

    first_page = client.get("/history", params={"limit": 2, "offset": 0}).json()
    assert len(first_page["items"]) == 2
    assert first_page["next_offset"] == 2

    second_page = client.get("/history", params={"limit": 2, "offset": 2}).json()
    assert len(second_page["items"]) == 1
    assert second_page["next_offset"] is None


def test_history_empty_returns_empty_list_not_error(client):
    response = client.get("/history")
    assert response.status_code == 200
    body = response.json()
    assert body == {"items": [], "total": 0, "next_offset": None}
