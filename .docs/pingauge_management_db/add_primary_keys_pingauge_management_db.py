"""ピンゲージ管理DBのPostgreSQLテーブルにPRIMARY KEY制約を追加する。

このファイルは .docs/pingauge_management_db 専用です。
既存データの重複・NULLを確認したうえで、未設定のPRIMARY KEYのみ追加します。
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

import psycopg2
from dotenv import dotenv_values

TARGET_DIR = Path(__file__).resolve().parent
ERROR_LOG_FILE = "add_primary_keys_pingauge_management_db.log"
DEFAULT_SCHEMA = "public"

PRIMARY_KEY_SPECS: list[tuple[str, list[str], str]] = [
    ("pin_gauge_lending", ["id"], "pin_gauge_lending_pkey"),
    ("staff_master", ["staff_id"], "staff_master_pkey"),
    # case_no に NULL が 310 件あるため、全行で一意な size を主キーとする
    ("pin_gauge_master", ["size"], "pin_gauge_master_pkey"),
]


@dataclass(frozen=True)
class PrimaryKeySpec:
    table_name: str
    columns: list[str]
    constraint_name: str


def main() -> int:
    args = parse_args()
    setup_logging(TARGET_DIR / ERROR_LOG_FILE)

    try:
        env = load_env(TARGET_DIR / ".env")
        specs = [PrimaryKeySpec(*spec) for spec in PRIMARY_KEY_SPECS]
        apply_primary_keys(env["DATABASE_URL"], args.schema, specs, dry_run=args.dry_run)
        return 0
    except Exception:
        logging.exception("PRIMARY KEY追加処理が失敗しました")
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ピンゲージ管理DBのPRIMARY KEYを追加")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="PostgreSQLスキーマ名")
    parser.add_argument("--dry-run", action="store_true", help="検証のみ行い、ALTER TABLEは実行しない")
    return parser.parse_args()


def setup_logging(error_log_path: Path) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(error_log_path, mode="w", encoding="utf-8-sig"),
            logging.StreamHandler(),
        ],
    )


def load_env(env_path: Path) -> dict[str, str]:
    values = {key: value for key, value in dotenv_values(env_path).items() if value is not None}
    if not values.get("DATABASE_URL"):
        raise ValueError(".envの必須項目が不足しています: DATABASE_URL")
    return values


def apply_primary_keys(
    database_url: str,
    schema: str,
    specs: list[PrimaryKeySpec],
    *,
    dry_run: bool,
) -> None:
    connection = psycopg2.connect(database_url)
    try:
        connection.autocommit = False
        with connection.cursor() as cursor:
            for spec in specs:
                apply_primary_key(cursor, schema, spec, dry_run=dry_run)
        if dry_run:
            connection.rollback()
            logging.info("dry-runのため変更はコミットしませんでした")
        else:
            connection.commit()
            logging.info("PRIMARY KEY追加をコミットしました")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def apply_primary_key(
    cursor: psycopg2.extensions.cursor,
    schema: str,
    spec: PrimaryKeySpec,
    *,
    dry_run: bool,
) -> None:
    if has_primary_key(cursor, schema, spec.table_name):
        logging.info("スキップ: %s には既にPRIMARY KEYがあります", spec.table_name)
        return

    verify_primary_key_candidate(cursor, schema, spec)
    alter_sql = build_add_primary_key_sql(schema, spec)
    logging.info("実行予定SQL: %s", alter_sql)
    if dry_run:
        logging.info("dry-run: %s へのPRIMARY KEY追加をスキップしました", spec.table_name)
        return

    cursor.execute(alter_sql)
    logging.info("完了: %s に PRIMARY KEY (%s) を追加しました", spec.table_name, ", ".join(spec.columns))


def has_primary_key(cursor: psycopg2.extensions.cursor, schema: str, table_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.table_constraints
        WHERE table_schema = %s
          AND table_name = %s
          AND constraint_type = 'PRIMARY KEY'
        """,
        (schema, table_name),
    )
    return int(cursor.fetchone()[0]) > 0


def verify_primary_key_candidate(
    cursor: psycopg2.extensions.cursor,
    schema: str,
    spec: PrimaryKeySpec,
) -> None:
    table_name = qualified_name(schema, spec.table_name)
    column_exprs = [f"{quote_identifier(column)} IS NULL" for column in spec.columns]
    null_condition = " OR ".join(column_exprs)
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {null_condition}")
    null_count = int(cursor.fetchone()[0])
    if null_count > 0:
        raise ValueError(f"{spec.table_name} のPRIMARY KEY候補にNULLがあります: {null_count}件")

    if len(spec.columns) == 1:
        column_name = quote_identifier(spec.columns[0])
        cursor.execute(
            f"""
            SELECT COUNT(*) - COUNT(DISTINCT {column_name})
            FROM {table_name}
            """
        )
    else:
        distinct_expr = ", ".join(quote_identifier(column) for column in spec.columns)
        cursor.execute(
            f"""
            SELECT COUNT(*) - COUNT(DISTINCT ({distinct_expr}))
            FROM {table_name}
            """
        )

    duplicate_count = int(cursor.fetchone()[0])
    if duplicate_count > 0:
        raise ValueError(f"{spec.table_name} のPRIMARY KEY候補に重複があります: {duplicate_count}件")

    logging.info("検証OK: %s (%s)", spec.table_name, ", ".join(spec.columns))


def build_add_primary_key_sql(schema: str, spec: PrimaryKeySpec) -> str:
    table_name = qualified_name(schema, spec.table_name)
    columns = ", ".join(quote_identifier(column) for column in spec.columns)
    constraint_name = quote_identifier(spec.constraint_name)
    return f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} PRIMARY KEY ({columns})"


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def qualified_name(schema: str, table_name: str) -> str:
    return f"{quote_identifier(schema)}.{quote_identifier(table_name)}"


if __name__ == "__main__":
    raise SystemExit(main())
