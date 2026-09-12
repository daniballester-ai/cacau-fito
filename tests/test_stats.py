"""Unit tests for history.get_stats() (see specs/001-prediction-stats)."""
import pytest

from src.inference_service import history

USER_ID = 1


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setattr(history, "IMAGES_DIR", str(tmp_path / "history" / "images"))
    monkeypatch.setattr(history, "DB_PATH", str(tmp_path / "history" / "history.db"))
    yield


def test_get_stats_counts_across_multiple_classes():
    history.record_prediction("healthy", 0.9, {"healthy": 0.9}, user_id=USER_ID)
    history.record_prediction("healthy", 0.85, {"healthy": 0.85}, user_id=USER_ID)
    history.record_prediction("cssvd", 0.7, {"cssvd": 0.7}, user_id=USER_ID)
    history.record_prediction("anthracnose", 0.8, {"anthracnose": 0.8}, user_id=USER_ID)

    total, by_class = history.get_stats(USER_ID)

    assert total == 4
    assert by_class == {"healthy": 2, "cssvd": 1, "anthracnose": 1}


def test_get_stats_reflects_skewed_distribution_accurately():
    for _ in range(5):
        history.record_prediction("healthy", 0.9, {"healthy": 0.9}, user_id=USER_ID)
    history.record_prediction("cssvd", 0.6, {"cssvd": 0.6}, user_id=USER_ID)

    total, by_class = history.get_stats(USER_ID)

    assert total == 6
    assert by_class["healthy"] == 5
    assert by_class["cssvd"] == 1
    assert by_class.get("anthracnose", 0) == 0


def test_get_stats_on_empty_history_returns_zero():
    total, by_class = history.get_stats(USER_ID)

    assert total == 0
    assert by_class == {}


def test_get_stats_scoped_to_user():
    history.record_prediction("healthy", 0.9, {"healthy": 0.9}, user_id=1)
    history.record_prediction("cssvd", 0.7, {"cssvd": 0.7}, user_id=2)

    total, by_class = history.get_stats(1)

    assert total == 1
    assert by_class == {"healthy": 1}
