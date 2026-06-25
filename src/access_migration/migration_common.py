"""移行スクリプト共通: ログ形式・CLI・PostgreSQL 更新モード。"""

from __future__ import annotations

import argparse
import logging
import sys
from enum import Enum
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import psycopg2
from dotenv import dotenv_values
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

REFRESH_MODE_HELP = (
    "更新モード（いずれか1つ必須）: "
    "--drop-database=DB削除後に再作成, "
    "--drop-table=移行対象テーブルのみDROP後に再作成, "
    "--truncate=データのみ更新"
)


class RefreshMode(str, Enum):
    DROP_DATABASE = "drop-database"
    DROP_TABLE = "drop-table"
    TRUNCATE = "truncate"


def ensure_src_on_path(script_file: str | Path) -> Path:
    """`.docs/<target>/` 配下スクリプトから `src` を import 可能にする。"""

    migration_root = Path(script_file).resolve().parents[2]
    src = migration_root / "src"
    src_text = str(src)
    if src_text not in sys.path:
        sys.path.insert(0, src_text)
    return migration_root


def setup_migration_logging(error_log_path: Path, *, verbose: bool = False) -> None:
    """コンソールと対象フォルダ内エラーログへ同一形式で出力する。"""

    error_log_path.parent.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    root = logging.getLogger()
    root.handlers.clear()
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(error_log_path, mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def load_target_env(target_dir: Path, env_filename: str = ".env") -> dict[str, str]:
    """対象フォルダ内 `.env` を読み込む。"""

    env_path = target_dir / env_filename
    if not env_path.is_file():
        raise FileNotFoundError(f".envファイルが見つかりません: {env_path}")
    values = {key: value for key, value in dotenv_values(env_path).items() if value is not None}
    missing = [key for key in ("DATABASE_URL", "ACCESS_DB_PATH") if not values.get(key)]
    if missing:
        raise ValueError(f".envの必須項目が不足しています: {', '.join(missing)}")
    return values


def add_refresh_mode_arguments(parser: argparse.ArgumentParser, *, required: bool = True) -> None:
    """--drop-database / --drop-table / --truncate の排他グループを追加する。"""

    group = parser.add_mutually_exclusive_group(required=required)
    group.add_argument(
        "--drop-database",
        action="store_true",
        help="PostgreSQL データベースを DROP 後に再作成してから移行",
    )
    group.add_argument(
        "--drop-table",
        action="store_true",
        help="Access移行対象テーブルのみ DROP CASCADE 後に再作成してから移行（手動追加テーブルは保持）",
    )
    group.add_argument(
        "--truncate",
        action="store_true",
        help="移行対象テーブルを TRUNCATE してデータのみ更新",
    )


def resolve_refresh_mode(args: argparse.Namespace, *, default: RefreshMode | None = None) -> RefreshMode:
    """CLI 引数から RefreshMode を返す。"""

    if getattr(args, "drop_database", False):
        return RefreshMode.DROP_DATABASE
    if getattr(args, "drop_table", False):
        return RefreshMode.DROP_TABLE
    if getattr(args, "truncate", False):
        return RefreshMode.TRUNCATE
    if default is not None:
        return default
    raise ValueError(REFRESH_MODE_HELP)


def refresh_mode_to_cli_args(mode: RefreshMode) -> tuple[str, ...]:
    """subprocess へ渡す CLI 引数を返す。"""

    return (f"--{mode.value}",)


def mask_database_url(database_url: str) -> str:
    parsed = urlparse(database_url)
    if not parsed.hostname:
        return database_url
    user = parsed.username or ""
    host = parsed.hostname
    port = f":{parsed.port}" if parsed.port else ""
    db = parsed.path.lstrip("/")
    return f"postgresql://{user}:***@{host}{port}/{db}"


def extract_database_name(database_url: str) -> str:
    name = urlparse(database_url).path.lstrip("/")
    if not name:
        raise ValueError("DATABASE_URL にデータベース名が含まれていません")
    return name


def admin_database_url(database_url: str, admin_db: str = "postgres") -> str:
    parsed = urlparse(database_url)
    return parsed._replace(path=f"/{quote_plus(admin_db)}").geturl()


def drop_database(database_url: str) -> None:
    """対象 PostgreSQL データベースを DROP 後に再作成する。"""

    database_name = extract_database_name(database_url)
    admin_url = admin_database_url(database_url)
    logging.warning("DROP DATABASE を実行します: %s", database_name)
    connection = psycopg2.connect(admin_url)
    try:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
                """,
                (database_name,),
            )
            cursor.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
            cursor.execute(f'CREATE DATABASE "{database_name}"')
    finally:
        connection.close()
    logging.info("データベースを再作成しました: %s", database_name)


def drop_public_schema(database_url: str, schema: str = "public") -> None:
    """public スキーマを DROP CASCADE 後に再作成する。"""

    logging.warning('DROP SCHEMA "%s" CASCADE を実行します: %s', schema, mask_database_url(database_url))
    connection = psycopg2.connect(database_url)
    try:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
            cursor.execute(f'CREATE SCHEMA "{schema}"')
            cursor.execute(f'GRANT ALL ON SCHEMA "{schema}" TO postgres')
            cursor.execute(f'GRANT ALL ON SCHEMA "{schema}" TO public')
    finally:
        connection.close()


def drop_tables_cascade(connection: psycopg2.extensions.connection, schema: str, table_names: list[str]) -> None:
    """指定テーブルを DROP TABLE IF EXISTS ... CASCADE する。"""

    if not table_names:
        return
    with connection.cursor() as cursor:
        for table_name in table_names:
            cursor.execute(f'DROP TABLE IF EXISTS "{schema}"."{table_name}" CASCADE')
    logging.warning("DROP TABLE を実行しました: %s", ", ".join(table_names))


def table_exists(connection: psycopg2.extensions.connection, schema: str, table_name: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s
            """,
            (schema, table_name),
        )
        return cursor.fetchone() is not None


def ensure_tables_exist(connection: psycopg2.extensions.connection, schema: str, table_names: list[str]) -> None:
    missing = [name for name in table_names if not table_exists(connection, schema, name)]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"--truncate に必要なテーブルが存在しません: {joined}。"
            "先に --drop-table または --drop-database でスキーマを作成してください。"
        )


def truncate_tables(connection: psycopg2.extensions.connection, schema: str, table_names: list[str]) -> None:
    """指定テーブルを TRUNCATE RESTART IDENTITY CASCADE する。"""

    if not table_names:
        return
    ensure_tables_exist(connection, schema, table_names)
    qualified = ", ".join(f'"{schema}"."{name}"' for name in table_names)
    with connection.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {qualified} RESTART IDENTITY CASCADE")
    logging.warning("TRUNCATE を実行しました: %s", ", ".join(table_names))


def run_pre_migration_refresh(
    database_url: str,
    mode: RefreshMode,
    schema: str = "public",
    table_names: list[str] | None = None,
) -> None:
    """移行スクリプト main() から呼び出す DB レベルの refresh。"""

    if mode == RefreshMode.DROP_DATABASE:
        drop_database(database_url)
        return
    if mode == RefreshMode.DROP_TABLE:
        if not table_names:
            raise ValueError("--drop-table では移行対象テーブル名 (table_names) の指定が必要です")
        connection = psycopg2.connect(database_url)
        try:
            connection.autocommit = True
            drop_tables_cascade(connection, schema, table_names)
        finally:
            connection.close()
