"""Testes unitários para o script scripts/purge_legacy_predictions.py."""
import sqlite3
import time
from pathlib import Path

from scripts.purge_legacy_predictions import purge_legacy_records


def setup_test_db(tmp_path: Path):
    db_path = tmp_path / "test_history.db"
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    # Cria arquivos de imagem falsos
    img_legacy_1 = images_dir / "legacy_1.jpg"
    img_legacy_1.write_bytes(b"fake-image-legacy-1")
    img_legacy_2 = images_dir / "legacy_2.jpg"
    img_legacy_2.write_bytes(b"fake-image-legacy-2")
    img_user_1 = images_dir / "user_1.jpg"
    img_user_1.write_bytes(b"fake-image-user-1")

    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at REAL NOT NULL,
            label TEXT NOT NULL,
            confidence REAL NOT NULL,
            probabilities_json TEXT NOT NULL,
            image_path TEXT,
            user_id INTEGER
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE feedback (
            prediction_id INTEGER UNIQUE NOT NULL,
            corrected_label TEXT NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )

    # Inserção de dados de teste: 2 legados (user_id=None) e 1 com usuário ativo (user_id=42)
    conn.execute(
        "INSERT INTO predictions VALUES (1, ?, 'cssvd', 0.9, '{}', ?, NULL)",
        (time.time() - 100, str(img_legacy_1)),
    )
    conn.execute(
        "INSERT INTO predictions VALUES (2, ?, 'healthy', 0.85, '{}', ?, NULL)",
        (time.time() - 50, str(img_legacy_2)),
    )
    conn.execute(
        "INSERT INTO predictions VALUES (3, ?, 'anthracnose', 0.95, '{}', ?, 42)",
        (time.time(), str(img_user_1)),
    )

    # Feedback para predição 1 (legada) e predição 3 (autenticada)
    conn.execute("INSERT INTO feedback VALUES (1, 'healthy', ?)", (time.time(),))
    conn.execute("INSERT INTO feedback VALUES (3, 'cssvd', ?)", (time.time(),))
    conn.commit()
    conn.close()

    return db_path, img_legacy_1, img_legacy_2, img_user_1


def test_dry_run_does_not_delete(tmp_path):
    db_path, img_l1, img_l2, img_u1 = setup_test_db(tmp_path)

    exit_code = purge_legacy_records(db_path, dry_run=True)
    assert exit_code == 0

    # Garante que arquivos físicos ainda existem
    assert img_l1.exists()
    assert img_l2.exists()
    assert img_u1.exists()

    # Garante que as linhas no banco ainda existem
    conn = sqlite3.connect(str(db_path))
    total_preds = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    total_feedback = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
    conn.close()

    assert total_preds == 3
    assert total_feedback == 2


def test_purge_deletes_only_legacy_records(tmp_path):
    db_path, img_l1, img_l2, img_u1 = setup_test_db(tmp_path)

    exit_code = purge_legacy_records(db_path, dry_run=False)
    assert exit_code == 0

    # Imagens legadas devem ter sido deletadas
    assert not img_l1.exists()
    assert not img_l2.exists()

    # Imagem do usuário ativo DEVE continuar existindo intacta
    assert img_u1.exists()

    # No banco de dados: apenas o registro 3 deve sobrar
    conn = sqlite3.connect(str(db_path))
    remaining = conn.execute("SELECT id, user_id, label FROM predictions").fetchall()
    remaining_feedback = conn.execute("SELECT prediction_id FROM feedback").fetchall()
    conn.close()

    assert len(remaining) == 1
    assert remaining[0][0] == 3
    assert remaining[0][1] == 42
    assert remaining[0][2] == "anthracnose"

    # Feedback da predição legada (1) foi removido; da predição 3 permanece
    assert len(remaining_feedback) == 1
    assert remaining_feedback[0][0] == 3
