"""API-level tests for POST /predict/{id}/feedback (see openspec/changes/add-diagnosis-feedback)."""
import os

import pytest
from fastapi.testclient import TestClient

from src.inference_service import history, main
from tests.conftest import authenticate

SAMPLE_IMAGE = os.path.join(os.path.dirname(__file__), "..", "samples", "healthy_1.jpg")


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


def _predict(client):
    with open(SAMPLE_IMAGE, "rb") as f:
        response = client.post("/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
    assert response.status_code == 200
    history_response = client.get("/history", params={"limit": 1, "offset": 0})
    return history_response.json()["items"][0]["id"]


def test_submit_feedback_for_real_prediction_succeeds(client):
    pred_id = _predict(client)
    response = client.post(f"/predict/{pred_id}/feedback", json={"label": "healthy"})
    assert response.status_code == 200
    assert response.json() == {"prediction_id": pred_id, "label": "healthy"}


def test_feedback_for_nonexistent_prediction_returns_404(client):
    response = client.post("/predict/999999/feedback", json={"label": "healthy"})
    assert response.status_code == 404


def test_second_feedback_for_same_prediction_returns_409(client):
    pred_id = _predict(client)
    first = client.post(f"/predict/{pred_id}/feedback", json={"label": "healthy"})
    assert first.status_code == 200

    second = client.post(f"/predict/{pred_id}/feedback", json={"label": "cssvd"})
    assert second.status_code == 409
    assert history.get_feedback(pred_id) == "healthy"
