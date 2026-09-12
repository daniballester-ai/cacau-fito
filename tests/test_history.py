"""Unit tests for src/inference_service/history.py (see openspec/changes/add-prediction-history)."""
import os

import pytest

from src.inference_service import history

USER_ID = 1


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    """Point the module at a throwaway directory per test."""
    monkeypatch.setattr(history, "HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setattr(history, "IMAGES_DIR", str(tmp_path / "history" / "images"))
    monkeypatch.setattr(history, "DB_PATH", str(tmp_path / "history" / "history.db"))
    yield


def test_record_and_read_back():
    history.record_prediction(
        "healthy", 0.93, {"healthy": 0.93, "cssvd": 0.04, "anthracnose": 0.03}, b"fake-image-bytes", user_id=USER_ID
    )

    items, total = history.list_predictions(USER_ID, limit=20, offset=0)

    assert total == 1
    assert len(items) == 1
    assert items[0]["label"] == "healthy"
    assert items[0]["confidence"] == pytest.approx(0.93)
    assert items[0]["probabilities"]["cssvd"] == pytest.approx(0.04)


def test_retention_evicts_oldest_and_its_image_file():
    for i in range(history.RETENTION_LIMIT + 1):
        history.record_prediction("healthy", 0.9, {"healthy": 0.9}, f"image-{i}".encode(), user_id=USER_ID)

    items, total = history.list_predictions(USER_ID, limit=1000, offset=0)

    assert total == history.RETENTION_LIMIT
    assert len(items) == history.RETENTION_LIMIT
    # the very first inserted entry should have been evicted
    assert all(item["id"] != 1 for item in items)
    # image directory should also only contain RETENTION_LIMIT files
    image_files = os.listdir(history.IMAGES_DIR)
    assert len(image_files) == history.RETENTION_LIMIT


def test_image_file_written_and_path_matches_stored_reference():
    history.record_prediction("cssvd", 0.7, {"cssvd": 0.7}, b"some-bytes", user_id=USER_ID)

    conn = history._connect()
    try:
        (image_path,) = conn.execute("SELECT image_path FROM predictions").fetchone()
    finally:
        conn.close()

    assert image_path is not None
    assert os.path.exists(image_path)
    with open(image_path, "rb") as f:
        assert f.read() == b"some-bytes"


def test_ordering_is_newest_first():
    history.record_prediction("healthy", 0.9, {"healthy": 0.9}, user_id=USER_ID)
    history.record_prediction("cssvd", 0.8, {"cssvd": 0.8}, user_id=USER_ID)
    history.record_prediction("anthracnose", 0.7, {"anthracnose": 0.7}, user_id=USER_ID)

    items, _ = history.list_predictions(USER_ID, limit=10, offset=0)

    assert [item["label"] for item in items] == ["anthracnose", "cssvd", "healthy"]


def test_pagination_returns_only_requested_page():
    for i in range(5):
        history.record_prediction("healthy", 0.9, {"healthy": 0.9}, user_id=USER_ID)

    page, total = history.list_predictions(USER_ID, limit=2, offset=0)
    assert total == 5
    assert len(page) == 2

    next_page, _ = history.list_predictions(USER_ID, limit=2, offset=2)
    assert len(next_page) == 2
    assert {item["id"] for item in page}.isdisjoint({item["id"] for item in next_page})


def test_empty_history_returns_empty_list_not_error():
    items, total = history.list_predictions(USER_ID, limit=20, offset=0)
    assert items == []
    assert total == 0


def test_users_only_see_their_own_history():
    history.record_prediction("healthy", 0.9, {"healthy": 0.9}, user_id=1)
    history.record_prediction("cssvd", 0.8, {"cssvd": 0.8}, user_id=2)

    items_user1, total_user1 = history.list_predictions(1, limit=20, offset=0)
    items_user2, total_user2 = history.list_predictions(2, limit=20, offset=0)

    assert total_user1 == 1
    assert items_user1[0]["label"] == "healthy"
    assert total_user2 == 1
    assert items_user2[0]["label"] == "cssvd"
