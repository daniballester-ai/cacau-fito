"""Unit tests for diagnosis feedback (see openspec/changes/add-diagnosis-feedback)."""
import pytest

from src.inference_service import history


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setattr(history, "IMAGES_DIR", str(tmp_path / "history" / "images"))
    monkeypatch.setattr(history, "DB_PATH", str(tmp_path / "history" / "history.db"))
    yield


def _make_prediction():
    history.record_prediction("healthy", 0.9, {"healthy": 0.9, "cssvd": 0.05, "anthracnose": 0.05}, user_id=1)
    items, _ = history.list_predictions(1, limit=1, offset=0)
    return items[0]["id"]


def test_record_and_read_back_feedback():
    pred_id = _make_prediction()
    history.record_feedback(pred_id, "healthy")
    assert history.get_feedback(pred_id) == "healthy"


def test_correcting_a_prediction_stores_the_corrected_label():
    pred_id = _make_prediction()
    history.record_feedback(pred_id, "cssvd")
    assert history.get_feedback(pred_id) == "cssvd"


def test_feedback_for_nonexistent_prediction_raises():
    with pytest.raises(history.PredictionNotFoundError):
        history.record_feedback(9999, "healthy")


def test_second_feedback_for_same_prediction_is_rejected():
    pred_id = _make_prediction()
    history.record_feedback(pred_id, "healthy")
    with pytest.raises(history.FeedbackAlreadyExistsError):
        history.record_feedback(pred_id, "cssvd")
    # original feedback unchanged
    assert history.get_feedback(pred_id) == "healthy"
