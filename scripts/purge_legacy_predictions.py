#!/usr/bin/env python3
"""
CacauFito — Script de Manutenção e Purga Imediata de Dados Legados

Propósito:
    Remove imediatamente do banco de dados SQLite e do sistema de arquivos todas
    as predições registradas antes da introdução da autenticação multi-usuário (Fase 6),
    ou seja, tuplas onde `user_id IS NULL`.

Ações executadas:
    1. Identifica todas as predições órfãs (user_id IS NULL);
    2. Remove os arquivos físicos de imagem associados (.jpg em history/images/);
    3. Remove registros vinculados na tabela de feedback (se houver);
    4. Deleta as linhas na tabela predictions;
    5. Executa VACUUM no SQLite para desfragmentar e liberar espaço no arquivo .db.

Uso:
    python scripts/purge_legacy_predictions.py              # Executa a limpeza real
    python scripts/purge_legacy_predictions.py --dry-run    # Apenas simula sem deletar nada
    python scripts/purge_legacy_predictions.py --db-path /caminho/personalizado/history.db
"""
import argparse
import os
import sqlite3
import sys
from pathlib import Path

DEFAULT_HISTORY_DIR = Path(__file__).resolve().parent.parent / "history"
DEFAULT_DB_PATH = DEFAULT_HISTORY_DIR / "history.db"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Expurgo imediato de predições legadas (user_id IS NULL) no CacauFito."
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Caminho para o arquivo history.db (Padrão: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula a execução: lista o que seria excluído sem alterar o banco ou deletar arquivos.",
    )
    return parser.parse_args()


def purge_legacy_records(db_path: Path, dry_run: bool = False) -> int:
    if not db_path.exists():
        print(f"[INFO] Arquivo de banco de dados não encontrado em: {db_path}")
        print("[INFO] Nada a limpar. O sistema está limpo ou o banco ainda não foi inicializado.")
        return 0

    print(f"[*] Conectando ao banco de dados: {db_path}")
    conn = sqlite3.connect(str(db_path))

    try:
        # 1. Verifica se a tabela 'predictions' existe
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'")
        if not cursor.fetchone():
            print("[INFO] A tabela 'predictions' não existe no banco informado. Nada a fazer.")
            return 0

        # 2. Verifica se a coluna 'user_id' existe na tabela
        cursor.execute("PRAGMA table_info(predictions)")
        columns = [row[1] for row in cursor.fetchall()]
        if "user_id" not in columns:
            print("[ALERTA] A coluna 'user_id' não existe na tabela predictions.")
            print("[ALERTA] Execute a API ao menos uma vez para que a migração _ensure_user_id_column() ocorra.")
            return 0

        # 3. Busca predições órfãs (user_id IS NULL)
        cursor.execute(
            "SELECT id, image_path, label, created_at FROM predictions WHERE user_id IS NULL ORDER BY id ASC"
        )
        orphan_predictions = cursor.fetchall()
        total_orphans = len(orphan_predictions)

        if total_orphans == 0:
            print("[SUCESSO] Nenhuma predição legada (user_id IS NULL) foi encontrada. O banco já está saneado!")
            return 0

        orphan_ids = [row[0] for row in orphan_predictions]
        image_paths = [row[1] for row in orphan_predictions if row[1]]

        # 4. Verifica feedbacks vinculados a essas predições
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
        has_feedback_table = bool(cursor.fetchone())
        feedback_count = 0
        if has_feedback_table:
            placeholders = ",".join("?" for _ in orphan_ids)
            cursor.execute(
                f"SELECT COUNT(*) FROM feedback WHERE prediction_id IN ({placeholders})",
                orphan_ids,
            )
            feedback_count = cursor.fetchone()[0]

        print("--------------------------------------------------")
        print(f"  Predições legadas encontradas : {total_orphans}")
        print(f"  Imagens em disco associadas   : {len(image_paths)}")
        print(f"  Registros de feedback órfãos  : {feedback_count}")
        print("--------------------------------------------------")

        if dry_run:
            print("\n[MODO DRY-RUN] Nenhuma alteração foi realizada.")
            print(f"[DRY-RUN] Seriam deletadas {total_orphans} linhas de 'predictions'.")
            print(f"[DRY-RUN] Seriam deletadas {feedback_count} linhas de 'feedback'.")
            print(f"[DRY-RUN] Seriam removidos {len(image_paths)} arquivos físicos de imagem.")
            return 0

        # 5. Remoção física dos arquivos de imagem do disco
        deleted_files = 0
        bytes_freed = 0
        for img_path_str in image_paths:
            img_file = Path(img_path_str)
            if img_file.exists():
                try:
                    file_size = img_file.stat().st_size
                    img_file.unlink()
                    deleted_files += 1
                    bytes_freed += file_size
                except OSError as e:
                    print(f"[AVISO] Falha ao remover arquivo {img_file}: {e}")

        # 6. Remoção relacional no SQLite dentro de transação
        placeholders = ",".join("?" for _ in orphan_ids)
        if has_feedback_table and feedback_count > 0:
            cursor.execute(
                f"DELETE FROM feedback WHERE prediction_id IN ({placeholders})",
                orphan_ids,
            )
            print(f"[+] Removidos {cursor.rowcount} registros da tabela 'feedback'.")

        cursor.execute("DELETE FROM predictions WHERE user_id IS NULL")
        deleted_rows = cursor.rowcount
        conn.commit()
        print(f"[+] Removidos {deleted_rows} registros da tabela 'predictions'.")

        # 7. Executa VACUUM para recuperar espaço em disco do arquivo SQLite
        print("[*] Executando VACUUM no banco SQLite para desfragmentação...")
        conn.execute("VACUUM")
        conn.close()

        mb_freed = bytes_freed / (1024 * 1024)
        print("\n==================================================")
        print("  LIMPEZA CONCLUÍDA COM SUCESSO!")
        print(f"  Total de predições deletadas : {deleted_rows}")
        print(f"  Arquivos de imagem apagados  : {deleted_files}")
        print(f"  Espaço em disco liberado     : {mb_freed:.2f} MB")
        print("==================================================")
        return 0

    except Exception as exc:
        print(f"[ERRO CRÍTICO] Falha durante o processo de purga: {exc}", file=sys.stderr)
        conn.rollback()
        conn.close()
        return 1


if __name__ == "__main__":
    args = parse_args()
    exit_code = purge_legacy_records(args.db_path, dry_run=args.dry_run)
    sys.exit(exit_code)
