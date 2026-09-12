"""API-level tests for GET /history/export.csv (see openspec/changes/add-history-csv-export)."""
import csv
import io
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


def test_export_after_predictions_is_well_formed_csv(client):
    with open(SAMPLE_IMAGE, "rb") as f:
        response = client.post("/predict", files={"file": ("leaf.jpg", f, "image/jpeg")})
    assert response.status_code == 200

    export = client.get("/history/export.csv")
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("text/csv")

    reader = csv.DictReader(io.StringIO(export.text))
    rows = list(reader)
    assert len(rows) == 1
    assert set(["id", "created_at", "label", "prob_healthy", "prob_cssvd", "prob_anthracnose"]).issubset(reader.fieldnames)


def test_export_on_empty_history_returns_header_only(client):
    export = client.get("/history/export.csv")
    assert export.status_code == 200
    reader = csv.DictReader(io.StringIO(export.text))
    rows = list(reader)
    assert rows == []
    assert "label" in reader.fieldnames
