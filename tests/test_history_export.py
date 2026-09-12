"""Unit tests for history.list_all_predictions() (see openspec/changes/add-history-csv-export)."""
import pytest

from src.inference_service import history


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setattr(history, "IMAGES_DIR", str(tmp_path / "history" / "images"))
    monkeypatch.setattr(history, "DB_PATH", str(tmp_path / "history" / "history.db"))
    yield


def test_list_all_predictions_returns_every_entry_newest_first():
    history.record_prediction("healthy", 0.9, {"healthy": 0.9}, user_id=1)
    history.record_prediction("cssvd", 0.8, {"cssvd": 0.8}, user_id=1)
    history.record_prediction("anthracnose", 0.7, {"anthracnose": 0.7}, user_id=1)

    rows = history.list_all_predictions(1)

    assert len(rows) == 3
    assert [r["label"] for r in rows] == ["anthracnose", "cssvd", "healthy"]


def test_list_all_predictions_on_empty_history_returns_empty_list():
    assert history.list_all_predictions(1) == []
