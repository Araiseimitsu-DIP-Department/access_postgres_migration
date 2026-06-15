"""材料入庫管理台帳兼ミルシート管理表DBをAccessからPostgreSQLへ忠実に移行する対象専用スクリプト。

このファイルは .docs/material_millsheet_manager 専用です。
Access側は読み取りのみ、PostgreSQL側は既存の移行先テーブルがある場合に停止します。
削除・TRUNCATE・既存行の更新は行いません。
"""

from __future__ import annotations

import argparse
import json
import logging
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import psycopg2
import pyodbc
from dotenv import dotenv_values
from psycopg2.extras import execute_values

from name_maps import COLUMN_NAME_MAP, TABLE_NAME_MAP


TARGET_DIR = Path(__file__).resolve().parent
META_FILE = "材料入庫管理台帳兼ミルシート管理表DB_meta.json"
RESULT_FILE = "migration_result_material_millsheet_manager_db.md"
MAPPING_FILE = "migration_mapping_material_millsheet_manager_db.md"
ERROR_LOG_FILE = "migration_error_material_millsheet_manager_db.log"
DEFAULT_SCHEMA = "public"
DEFAULT_BATCH_SIZE = 1000


@dataclass(frozen=True)
class ColumnMapping:
    access_name: str
    postgres_name: str
    access_type: str
    postgres_type: str
    nullable: bool
    note: str


@dataclass(frozen=True)
class TableMapping:
    access_name: str
    postgres_name: str
    table_type: str
    access_row_count: int
    columns: list[ColumnMapping]
    primary_key: list[str]
    indexes: list[dict[str, Any]]


@dataclass
class MigrationResult:
    table: TableMapping
    access_row_count: int | None = None
    postgres_row_count: int = 0
    inserted_row_count: int = 0
    status: str = "未実行"
    error: str = ""


def main() -> int:
    args = parse_args()
    setup_logging(TARGET_DIR / ERROR_LOG_FILE)

    try:
        env = load_env(TARGET_DIR / ".env")
        meta = load_meta(TARGET_DIR / META_FILE)
        access_db_path = resolve_access_db_path(env, meta)
        mappings = build_mappings(meta)
        validate_target_tables(mappings)
        write_mapping(TARGET_DIR / MAPPING_FILE, env, meta, mappings, [])

        if args.verify_only:
            results = verify_counts(env["DATABASE_URL"], access_db_path, mappings, args.schema)
        elif args.append_missing:
            results = append_missing_rows(env["DATABASE_URL"], access_db_path, mappings, args.schema, args.batch_size)
        else:
            results = migrate(env["DATABASE_URL"], access_db_path, mappings, args.schema, args.batch_size)

        write_mapping(TARGET_DIR / MAPPING_FILE, env, meta, mappings, results)
        write_result(TARGET_DIR / RESULT_FILE, access_db_path, results)
        return 0 if all(result.status == "成功" for result in results) else 1
    except Exception:
        logging.exception("移行処理が失敗しました")
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="材料入庫管理台帳兼ミルシート管理表DBをPostgreSQLへ移行")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="PostgreSQLスキーマ名")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="一括投入件数")
    parser.add_argument("--verify-only", action="store_true", help="投入せずAccess/PostgreSQL件数だけ再確認")
    parser.add_argument("--append-missing", action="store_true", help="PostgreSQLに存在しないAccess行だけを追加投入")
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
    missing = [key for key in ("DATABASE_URL", "ACCESS_DB_PATH") if not values.get(key)]
    if missing:
        raise ValueError(f".envの必須項目が不足しています: {', '.join(missing)}")
    return values


def load_meta(meta_path: Path) -> dict[str, Any]:
    if not meta_path.exists():
        raise FileNotFoundError(f"メタJSONが見つかりません: {meta_path}")
    return json.loads(meta_path.read_text(encoding="utf-8"))


def resolve_access_db_path(env: dict[str, str], meta: dict[str, Any]) -> Path:
    env_path = Path(env["ACCESS_DB_PATH"])
    if env_path.exists():
        return env_path

    meta_path = Path(meta.get("database_path", ""))
    if meta_path.exists():
        logging.warning("ACCESS_DB_PATHが存在しないため、メタJSONのAccess DBパスを使用します")
        return meta_path

    raise FileNotFoundError(f"Access DBが見つかりません: {env_path}")


def build_mappings(meta: dict[str, Any]) -> list[TableMapping]:
    mappings = []
    for table in meta["tables"]:
        access_table_name = table["name"]
        if access_table_name not in TABLE_NAME_MAP:
            raise ValueError(f"未定義のテーブル名があります。推測せず停止します: {access_table_name}")

        columns = [
            ColumnMapping(
                access_name=column["name"],
                postgres_name=resolve_column_name(column["name"]),
                access_type=column["access_type"],
                postgres_type=to_postgres_type(column),
                nullable=bool(column["nullable"]),
                note=build_column_note(column),
            )
            for column in table["columns"]
        ]
        postgres_names = [column.postgres_name for column in columns]
        if len(postgres_names) != len(set(postgres_names)):
            duplicates = sorted({name for name in postgres_names if postgres_names.count(name) > 1})
            raise ValueError(f"PostgreSQL列名が重複しています: {access_table_name} -> {duplicates}")

        mappings.append(
            TableMapping(
                access_name=access_table_name,
                postgres_name=TABLE_NAME_MAP[access_table_name],
                table_type=table.get("table_type") or "TABLE",
                access_row_count=int(table["row_count"] or 0),
                columns=columns,
                primary_key=table.get("primary_key", []),
                indexes=table.get("indexes", []),
            )
        )
    return mappings


def validate_target_tables(mappings: list[TableMapping]) -> None:
    actual = {mapping.access_name for mapping in mappings}
    expected = set(TABLE_NAME_MAP)
    if actual != expected:
        raise ValueError(f"移行対象テーブルが定義と一致しません。不足={sorted(expected - actual)} 想定外={sorted(actual - expected)}")


def resolve_column_name(access_column_name: str) -> str:
    if access_column_name not in COLUMN_NAME_MAP:
        raise ValueError(f"未定義のカラム名があります。推測せず停止します: {access_column_name}")
    return COLUMN_NAME_MAP[access_column_name]


def to_postgres_type(column: dict[str, Any]) -> str:
    access_type = column["access_type"]
    size = column.get("column_size")
    if access_type in {"VARCHAR", "WVARCHAR"}:
        return f"VARCHAR({size})" if size else "TEXT"
    if access_type == "COUNTER":
        return "BIGINT"
    if access_type in {"INTEGER", "SMALLINT"}:
        return "INTEGER"
    if access_type in {"DOUBLE", "REAL", "FLOAT"}:
        return "DOUBLE PRECISION"
    if access_type in {"NUMERIC", "DECIMAL", "CURRENCY"}:
        return "NUMERIC"
    if access_type in {"DATETIME", "DATE"}:
        return "TIMESTAMP"
    if access_type == "BIT":
        return "BOOLEAN"
    return column.get("postgres_type_hint") or "TEXT"


def build_column_note(column: dict[str, Any]) -> str:
    notes = []
    if column["access_type"] == "COUNTER":
        notes.append("AccessのCOUNTER。値を忠実に移行するためBIGINTで保持")
    if column["access_type"] == "BIT":
        notes.append("AccessのYes/Noをbooleanへ変換")
    if column["name"] == "金額" and column["access_type"] == "INTEGER":
        notes.append("変更前履歴テーブルではINTEGER型のためNUMERICではなくINTEGERで保持")
    return " / ".join(notes)


def migrate(
    database_url: str,
    access_db_path: Path,
    mappings: list[TableMapping],
    schema: str,
    batch_size: int,
) -> list[MigrationResult]:
    results = [MigrationResult(table=mapping) for mapping in mappings]
    access_connection = connect_access(access_db_path)
    postgres_connection = psycopg2.connect(database_url)
    try:
        postgres_connection.autocommit = False
        ensure_no_existing_tables(postgres_connection, schema, mappings)
        create_schema_and_tables(postgres_connection, schema, mappings)
        for result in results:
            migrate_table(access_connection, postgres_connection, schema, result, batch_size)
        postgres_connection.commit()
    except Exception:
        postgres_connection.rollback()
        raise
    finally:
        access_connection.close()
        postgres_connection.close()
    return results


def verify_counts(
    database_url: str,
    access_db_path: Path,
    mappings: list[TableMapping],
    schema: str,
) -> list[MigrationResult]:
    results = [MigrationResult(table=mapping) for mapping in mappings]
    access_connection = connect_access(access_db_path)
    postgres_connection = psycopg2.connect(database_url)
    try:
        with postgres_connection.cursor() as postgres_cursor:
            for result in results:
                result.access_row_count = count_access_rows(access_connection, result.table.access_name)
                result.postgres_row_count = count_postgres_rows(postgres_cursor, schema, result.table.postgres_name)
                result.inserted_row_count = result.postgres_row_count
                result.status = "成功" if result.access_row_count == result.postgres_row_count else "件数差異"
                logging.info(
                    "件数確認: %s Access=%s PostgreSQL=%s",
                    result.table.access_name,
                    result.access_row_count,
                    result.postgres_row_count,
                )
    finally:
        access_connection.close()
        postgres_connection.close()
    return results


def append_missing_rows(
    database_url: str,
    access_db_path: Path,
    mappings: list[TableMapping],
    schema: str,
    batch_size: int,
) -> list[MigrationResult]:
    results = [MigrationResult(table=mapping) for mapping in mappings]
    access_connection = connect_access(access_db_path)
    postgres_connection = psycopg2.connect(database_url)
    try:
        postgres_connection.autocommit = False
        for result in results:
            append_missing_rows_for_table(access_connection, postgres_connection, schema, result, batch_size)
        postgres_connection.commit()
    except Exception:
        postgres_connection.rollback()
        raise
    finally:
        access_connection.close()
        postgres_connection.close()
    return results


def append_missing_rows_for_table(
    access_connection: pyodbc.Connection,
    postgres_connection: psycopg2.extensions.connection,
    schema: str,
    result: MigrationResult,
    batch_size: int,
) -> None:
    mapping = result.table
    access_columns = [column.access_name for column in mapping.columns]
    postgres_columns = [column.postgres_name for column in mapping.columns]
    insert_sql = build_insert_sql(schema, mapping.postgres_name, postgres_columns)

    with postgres_connection.cursor() as postgres_cursor:
        result.access_row_count = count_access_rows(access_connection, mapping.access_name)
        result.postgres_row_count = count_postgres_rows(postgres_cursor, schema, mapping.postgres_name)
        if result.access_row_count <= result.postgres_row_count:
            result.status = "成功" if result.access_row_count == result.postgres_row_count else "件数差異"
            logging.info(
                "不足行なし: %s Access=%s PostgreSQL=%s",
                mapping.access_name,
                result.access_row_count,
                result.postgres_row_count,
            )
            return

        postgres_rows = load_postgres_rows(postgres_cursor, schema, mapping.postgres_name, postgres_columns)
        postgres_row_counter = Counter(postgres_rows)
        missing_rows = find_missing_access_rows(access_connection, mapping.access_name, access_columns, postgres_row_counter)
        if missing_rows:
            for index in range(0, len(missing_rows), batch_size):
                execute_values(postgres_cursor, insert_sql, missing_rows[index : index + batch_size], page_size=batch_size)
            result.inserted_row_count = len(missing_rows)

        result.postgres_row_count = count_postgres_rows(postgres_cursor, schema, mapping.postgres_name)
        result.status = "成功" if result.access_row_count == result.postgres_row_count else "件数差異"
        logging.info(
            "不足行追記: %s Access=%s PostgreSQL=%s appended=%s",
            mapping.access_name,
            result.access_row_count,
            result.postgres_row_count,
            result.inserted_row_count,
        )


def connect_access(access_db_path: Path) -> pyodbc.Connection:
    connection_string = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};" f"DBQ={access_db_path};ReadOnly=1;"
    return pyodbc.connect(connection_string, autocommit=True)


def ensure_no_existing_tables(
    connection: psycopg2.extensions.connection,
    schema: str,
    mappings: list[TableMapping],
) -> None:
    table_names = [mapping.postgres_name for mapping in mappings]
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_name = ANY(%s)
            """,
            (schema, table_names),
        )
        existing_tables = [row[0] for row in cursor.fetchall()]
    if existing_tables:
        raise RuntimeError(f"移行先テーブルが既に存在するため停止しました: {', '.join(existing_tables)}")


def create_schema_and_tables(
    connection: psycopg2.extensions.connection,
    schema: str,
    mappings: list[TableMapping],
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {quote_identifier(schema)}")
        for mapping in mappings:
            column_sql = ",\n    ".join(build_column_sql(column) for column in mapping.columns)
            table_name = qualified_name(schema, mapping.postgres_name)
            cursor.execute(f"CREATE TABLE {table_name} (\n    {column_sql}\n)")
            cursor.execute(f"COMMENT ON TABLE {table_name} IS %s", (f"元Accessテーブル: {mapping.access_name}",))
            for column in mapping.columns:
                cursor.execute(
                    f"COMMENT ON COLUMN {table_name}.{quote_identifier(column.postgres_name)} IS %s",
                    (f"元Accessカラム: {column.access_name}",),
                )


def build_column_sql(column: ColumnMapping) -> str:
    nullable_sql = "" if column.nullable else " NOT NULL"
    return f"{quote_identifier(column.postgres_name)} {column.postgres_type}{nullable_sql}"


def migrate_table(
    access_connection: pyodbc.Connection,
    postgres_connection: psycopg2.extensions.connection,
    schema: str,
    result: MigrationResult,
    batch_size: int,
) -> None:
    mapping = result.table
    access_columns = [column.access_name for column in mapping.columns]
    postgres_columns = [column.postgres_name for column in mapping.columns]
    select_sql = build_access_select_sql(mapping.access_name, access_columns)
    insert_sql = build_insert_sql(schema, mapping.postgres_name, postgres_columns)

    logging.info("移行開始: %s -> %s", mapping.access_name, mapping.postgres_name)
    try:
        result.access_row_count = count_access_rows(access_connection, mapping.access_name)
        access_cursor = access_connection.cursor()
        access_cursor.execute(select_sql)
        with postgres_connection.cursor() as postgres_cursor:
            while True:
                rows = access_cursor.fetchmany(batch_size)
                if not rows:
                    break
                values = [tuple(normalize_value(value, column) for value, column in zip(row, mapping.columns)) for row in rows]
                execute_values(postgres_cursor, insert_sql, values, page_size=batch_size)
                result.inserted_row_count += len(values)
            result.postgres_row_count = count_postgres_rows(postgres_cursor, schema, mapping.postgres_name)
        result.status = "成功" if result.postgres_row_count == result.access_row_count else "件数差異"
        logging.info("移行完了: %s Access=%s PostgreSQL=%s", mapping.access_name, result.access_row_count, result.postgres_row_count)
    except Exception as error:
        result.status = "失敗"
        result.error = str(error)
        logging.exception("テーブル移行失敗: %s", mapping.access_name)
        raise


def load_postgres_rows(
    cursor: psycopg2.extensions.cursor,
    schema: str,
    table_name: str,
    column_names: list[str],
) -> list[tuple[Any, ...]]:
    columns = ", ".join(quote_identifier(column) for column in column_names)
    cursor.execute(f"SELECT {columns} FROM {qualified_name(schema, table_name)}")
    return [tuple(row) for row in cursor.fetchall()]


def find_missing_access_rows(
    connection: pyodbc.Connection,
    table_name: str,
    column_names: list[str],
    postgres_row_counter: Counter[tuple[Any, ...]],
) -> list[tuple[Any, ...]]:
    cursor = connection.cursor()
    cursor.execute(build_access_select_sql(table_name, column_names))
    missing_rows: list[tuple[Any, ...]] = []
    while True:
        rows = cursor.fetchmany(DEFAULT_BATCH_SIZE)
        if not rows:
            break
        for row in rows:
            normalized_row = tuple(row)
            if postgres_row_counter[normalized_row] > 0:
                postgres_row_counter[normalized_row] -= 1
            else:
                missing_rows.append(normalized_row)
    return missing_rows


def build_access_select_sql(table_name: str, column_names: list[str]) -> str:
    columns = ", ".join(f"[{column}]" for column in column_names)
    return f"SELECT {columns} FROM [{table_name}]"


def build_insert_sql(schema: str, table_name: str, column_names: list[str]) -> str:
    columns = ", ".join(quote_identifier(column) for column in column_names)
    return f"INSERT INTO {qualified_name(schema, table_name)} ({columns}) VALUES %s"


def count_access_rows(connection: pyodbc.Connection, table_name: str) -> int:
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
    return int(cursor.fetchone()[0])


def count_postgres_rows(cursor: psycopg2.extensions.cursor, schema: str, table_name: str) -> int:
    cursor.execute(f"SELECT COUNT(*) FROM {qualified_name(schema, table_name)}")
    return int(cursor.fetchone()[0])


def normalize_value(value: Any, column: ColumnMapping) -> Any:
    if value is None:
        return None
    if column.access_type == "BIT":
        return bool(int(value))
    if isinstance(value, str) and value == "" and column.access_type in {"VARCHAR", "WVARCHAR"}:
        return None
    if isinstance(value, (datetime, date)):
        return value
    return value


def write_mapping(
    path: Path,
    env: dict[str, str],
    meta: dict[str, Any],
    mappings: list[TableMapping],
    results: list[MigrationResult],
) -> None:
    result_by_table = {result.table.access_name: result for result in results}
    lines = [
        "# Access → PostgreSQL 移行対応表（material_millsheet_manager）",
        "",
        "## 1. 移行概要",
        "",
        f"- 対象Access DB：`{meta.get('database_path', '')}`",
        f"- 移行先PostgreSQL DB：`{extract_database_name(env['DATABASE_URL'])}`",
        "- 接続情報：`.env` の `DATABASE_URL` / `ACCESS_DB_PATH` を参照",
        f"- 移行日：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- 方針：材料入庫管理台帳兼ミルシート管理表DB.accdb の全11テーブル・全カラムを英語スネークケースへ変換し忠実に移行",
        "",
        "## 2. 移行対象テーブル一覧",
        "",
        "| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |",
        "|---:|---|---|---|---:|---:|---|",
    ]
    for index, mapping in enumerate(mappings, start=1):
        result = result_by_table.get(mapping.access_name)
        access_count = result.access_row_count if result and result.access_row_count is not None else mapping.access_row_count
        postgres_count = result.postgres_row_count if result else ""
        note = result.status if result else "移行前"
        lines.append(f"| {index} | `{mapping.access_name}` | `{mapping.postgres_name}` | {mapping.table_type} | {access_count} | {postgres_count} | {note} |")

    lines.extend(["", "## 3. テーブル別カラム対応表", ""])
    for mapping in mappings:
        lines.extend(
            [
                f"### `{mapping.access_name}` → `{mapping.postgres_name}`",
                "",
                "| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |",
                "|---:|---|---|---|---|---|---|",
            ]
        )
        for index, column in enumerate(mapping.columns, start=1):
            nullable = "可" if column.nullable else "不可"
            lines.append(f"| {index} | `{column.access_name}` | {column.access_type} | `{column.postgres_name}` | {column.postgres_type} | {nullable} | {column.note} |")
        lines.append("")

    lines.extend(
        [
            "## 4. 型変換ルール",
            "",
            "| Access型 | PostgreSQL型 | 備考 |",
            "|---|---|---|",
            "| VARCHAR | varchar(n) | Accessのサイズを維持 |",
            "| COUNTER | bigint | 採番値を忠実に移行 |",
            "| INTEGER | integer | 整数 |",
            "| DOUBLE | double precision | 浮動小数 |",
            "| DATETIME | timestamp | 日付/時刻 |",
            "| BIT | boolean | Yes/No |",
            "| CURRENCY | numeric | 金額 |",
            "",
            "## 5. 注意事項",
            "",
        ]
    )
    lines.extend(build_caution_lines(meta, mappings))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def build_caution_lines(meta: dict[str, Any], mappings: list[TableMapping]) -> list[str]:
    lines = [
        "- 本移行は `材料入庫管理台帳兼ミルシート管理表DB.accdb` の11テーブルを対象としています。",
        "- AccessのFKメタデータはODBCで取得できなかったため、外部キー制約は作成していません。",
        "- `t_材料納入履歴 変更前` はスキーマ変更前のバックアップテーブルです。金額列はINTEGER型です。",
        "- `t_材料納入Tmp` は一時登録用テーブルです（0件でも構造を再現）。",
        "- `t_旧検査データ` は旧形式の検査データです。現行は `t_検査データ` を使用しています。",
        "- `購入ID` は材料納入履歴のIDを参照する論理FKですが、制約は未設定です。",
    ]
    zero_tables = [mapping.access_name for mapping in mappings if mapping.access_row_count == 0]
    if zero_tables:
        lines.append(f"- 0件テーブルも構造再現のため作成しています: {', '.join(f'`{name}`' for name in zero_tables)}")
    return lines


def write_result(path: Path, access_db_path: Path, results: list[MigrationResult]) -> None:
    lines = [
        "# Access → PostgreSQL 移行結果（material_millsheet_manager）",
        "",
        f"- 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Access DB: {access_db_path}",
        "",
        "| Accessテーブル名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 投入済み件数 | 状態 | エラー |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for result in results:
        access_count = result.access_row_count if result.access_row_count is not None else result.table.access_row_count
        lines.append(
            f"| {result.table.access_name} | {result.table.postgres_name} | {access_count} | {result.postgres_row_count} | {result.inserted_row_count} | {result.status} | {result.error} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def qualified_name(schema: str, table_name: str) -> str:
    return f"{quote_identifier(schema)}.{quote_identifier(table_name)}"


def extract_database_name(database_url: str) -> str:
    parsed = urlparse(database_url)
    return parsed.path.lstrip("/") or "要確認"


if __name__ == "__main__":
    raise SystemExit(main())
