"""API-level tests for GET /stats (see specs/001-prediction-stats)."""
import os

import pytest
from fastapi.testclient import TestClient

from src.inference_service import history, main
from tests.conftest import authenticate

SAMPLE_IMAGES = {
    "healthy": os.path.join(os.path.dirname(__file__), "..", "samples", "healthy_1.jpg"),
    "cssvd": os.path.join(os.path.dirname(__file__), "..", "samples", "cssvd_1.jpg"),
    "anthracnose": os.path.join(os.path.dirname(__file__), "..", "samples", "anthracnose_1.jpg"),
}


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


def test_stats_after_several_predictions_matches_contract_shape(client):
    for image_path in SAMPLE_IMAGES.values():
        _predict(client, image_path)

    response = client.get("/stats")
    assert response.status_code == 200
    body = response.json()

    assert set(body.keys()) == {"total", "by_class"}
    assert body["total"] == 3
    assert set(body["by_class"].keys()) == {"healthy", "cssvd", "anthracnose"}
    assert sum(body["by_class"].values()) == body["total"]


def test_stats_before_any_prediction_returns_all_zero(client):
    response = client.get("/stats")
    assert response.status_code == 200
    body = response.json()

    assert body["total"] == 0
    assert body["by_class"] == {"healthy": 0, "cssvd": 0, "anthracnose": 0}


def test_stats_returns_503_when_storage_fails(client, monkeypatch):
    def broken_get_stats(user_id):
        raise RuntimeError("simulated storage failure")

    monkeypatch.setattr(main.history, "get_stats", broken_get_stats)

    response = client.get("/stats")
    assert response.status_code == 503
    assert "detail" in response.json()
