"""Unit tests for history.get_stats_timeseries() (see openspec/changes/add-stats-dashboard)."""
import sqlite3
import time

import pytest

from src.inference_service import history


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setattr(history, "IMAGES_DIR", str(tmp_path / "history" / "images"))
    monkeypatch.setattr(history, "DB_PATH", str(tmp_path / "history" / "history.db"))
    yield


def _set_created_at(prediction_id, timestamp):
    conn = sqlite3.connect(history.DB_PATH)
    conn.execute("UPDATE predictions SET created_at = ? WHERE id = ?", (timestamp, prediction_id))
    conn.commit()
    conn.close()


def test_timeseries_groups_by_day_and_class_across_multiple_days():
    now = time.time()
    one_day = 86400

    history.record_prediction("healthy", 0.9, {"healthy": 0.9}, user_id=1)
    _set_created_at(1, now - 2 * one_day)

    history.record_prediction("healthy", 0.9, {"healthy": 0.9}, user_id=1)
    _set_created_at(2, now - one_day)
    history.record_prediction("cssvd", 0.8, {"cssvd": 0.8}, user_id=1)
    _set_created_at(3, now - one_day)

    history.record_prediction("anthracnose", 0.7, {"anthracnose": 0.7}, user_id=1)
    _set_created_at(4, now)

    series = history.get_stats_timeseries(1)

    assert len(series) == 3
    assert series[0]["by_class"] == {"healthy": 1}
    assert series[1]["by_class"] == {"healthy": 1, "cssvd": 1}
    assert series[2]["by_class"] == {"anthracnose": 1}
    # ascending order
    assert series[0]["date"] <= series[1]["date"] <= series[2]["date"]


def test_timeseries_on_empty_history_returns_empty_list():
    assert history.get_stats_timeseries(1) == []
