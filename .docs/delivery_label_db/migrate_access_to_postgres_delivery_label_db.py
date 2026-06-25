"""現品票DBをAccessからPostgreSQLへ忠実に移行する対象専用スクリプト。

このファイルは .docs/delivery_label_db 専用です。
接続設定は同フォルダ内の `.env` を使用します。
Access側は読み取りのみ。移行時は更新モードを指定してください:
  --drop-database  DB削除後に再作成
  --drop-table     テーブル削除後に再作成
  --truncate       データのみ更新（TRUNCATE）
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

import sys

_MIGRATION_ROOT = Path(__file__).resolve().parents[2]
_SRC = _MIGRATION_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from access_migration import migration_common
from access_migration import serial_columns as serial_columns_support
from access_migration.migration_common import RefreshMode

import pyodbc
import psycopg2
from dotenv import dotenv_values
from psycopg2.extras import execute_values


TARGET_DIR = Path(__file__).resolve().parent
META_FILE = "現品票DB_meta.json"
RESULT_FILE = "migration_result_delivery_label_db.md"
MAPPING_FILE = "migration_mapping_delivery_label_db.md"
ERROR_LOG_FILE = "migration_error_delivery_label_db.log"
DEFAULT_SCHEMA = "public"
DEFAULT_BATCH_SIZE = 1000

SKIP_ACCESS_TABLES: frozenset[str] = frozenset(
    {
        "t_QR履歴(backup_260521)",
        "t_QR履歴Tmp",
    }
)

TABLE_PRIMARY_KEY_OVERRIDE: dict[str, list[str]] = {
    "delivery_label_defect_details": ["production_lot_id"],
    "delivery_label_history": ["production_lot_id"],
}

TABLE_NAME_MAP = {
    "t_ExcelQR履歴": "excel_qr_history",
    "t_Excel現品票履歴": "excel_delivery_label_history",
    "t_ID番号": "id_number",
    "t_QR履歴": "qr_history",
    "t_エラーログ": "error_logs",
    "t_ロット完了理由": "lot_completion_reasons",
    "t_作業履歴": "work_history",
    "t_修正ログ": "correction_logs",
    "t_分割ロット": "split_lots",
    "t_工程マスタ": "process_master",
    "t_数量差異": "quantity_differences",
    "t_現品票不具合内容": "delivery_label_defect_details",
    "t_現品票履歴": "delivery_label_history",
}

COLUMN_NAME_MAP = {
    "ID": "id",
    "P番号": "p_number",
    "E番号": "e_number",
    "日付時刻": "date_time",
    "QRコード": "qr_code",
    "生産ロットID": "production_lot_id",
    "日付": "date_value",
    "工程": "process",
    "位置": "position",
    "数量": "quantity",
    "工程名": "process_name",
    "工程コード": "process_code",
    "更新フラグ": "update_flag",
    "TNo": "t_no",
    "号機": "machine_no",
    "品番": "product_code",
    "品名": "product_name",
    "客先": "customer",
    "材質": "material",
    "材料ロットNO": "material_lot_no",
    "備考": "remarks",
    "指示日": "instruction_date",
    "完了フラグ": "completion_flag",
    "エラー内容": "error_detail",
    "理由コード": "reason_code",
    "理由": "reason",
    "ロット数数値検査": "lot_count_numeric_inspection",
    "ロット数外観検査": "lot_count_appearance_inspection",
    "ロット数梱包": "lot_count_packaging",
    "ロット数洗浄": "lot_count_washing",
    "ロット数二次作業": "lot_count_secondary_work",
    "個数数値検査": "quantity_numeric_inspection",
    "個数外観検査": "quantity_appearance_inspection",
    "個数梱包": "quantity_packaging",
    "個数洗浄": "quantity_washing",
    "個数二次作業": "quantity_secondary_work",
    "金額数値検査": "amount_numeric_inspection",
    "金額外観検査": "amount_appearance_inspection",
    "金額梱包": "amount_packaging",
    "金額洗浄": "amount_washing",
    "金額二次作業": "amount_secondary_work",
    "稼働日数": "operating_days",
    "項目": "item",
    "内容": "content",
    "元ロットID": "source_lot_id",
    "新ロットID": "new_lot_id",
    "元数量": "source_quantity",
    "区分": "category",
    "作成日": "created_date",
    "計量日": "weighing_date",
    "出荷日": "shipping_date",
    "出荷数": "shipped_quantity",
    "計量数": "weighed_quantity",
    "差異": "difference",
    "不具合内容": "defect_detail",
    "処置内容": "action_detail",
    "処置済": "action_completed",
    "機械担当者": "machine_operator",
    "営業担当者": "sales_representative",
    "現在工程名": "current_process_name",
    "現在工程コード": "current_process_code",
    "工程2": "process_2",
    "工程3": "process_3",
    "工程4": "process_4",
    "工程5": "process_5",
    "工程6": "process_6",
    "工程7": "process_7",
    "工程8": "process_8",
    "工程9": "process_9",
    "現在工程番号": "current_process_number",
    "表面処理工程番号": "surface_treatment_process_number",
    "品番ID": "product_code_id",
    "印刷日": "printed_date",
    "完了日": "completed_date",
    "発行フラグ": "issue_flag",
    "不適合品フラグ": "nonconforming_product_flag",
    "不適合品数量": "nonconforming_product_quantity",
    "処理済フラグ": "processed_flag",
    "工程2備考": "process_2_remarks",
    "工程3備考": "process_3_remarks",
    "工程4備考": "process_4_remarks",
    "工程5備考": "process_5_remarks",
    "工程6備考": "process_6_remarks",
    "工程7備考": "process_7_remarks",
    "工程8備考": "process_8_remarks",
    "工程9備考": "process_9_remarks",
    "材料識別": "material_identification",
}

IMPORTANT_COLUMN_NAMES = {
    "id",
    "date_time",
    "qr_code",
    "production_lot_id",
    "date_value",
    "process",
    "position",
    "quantity",
    "process_code",
    "process_name",
    "product_code",
    "product_name",
    "customer",
    "instruction_date",
    "current_process_name",
    "current_process_code",
}


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
        elif args.delete_extra:
            results = delete_extra_rows(env["DATABASE_URL"], access_db_path, mappings, args.schema, args.batch_size)
        elif args.append_missing:
            results = append_missing_rows(env["DATABASE_URL"], access_db_path, mappings, args.schema, args.batch_size)
        else:
            refresh_mode = migration_common.resolve_refresh_mode(args)
            migration_common.run_pre_migration_refresh(env["DATABASE_URL"], refresh_mode, args.schema)
            results = migrate(
                env["DATABASE_URL"],
                access_db_path,
                mappings,
                args.schema,
                args.batch_size,
                refresh_mode,
            )

        write_mapping(TARGET_DIR / MAPPING_FILE, env, meta, mappings, results)
        write_result(TARGET_DIR / RESULT_FILE, access_db_path, results)
        return 0 if all(result.status == "成功" for result in results) else 1
    except Exception:
        logging.exception("移行処理が失敗しました")
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="現品票DBをPostgreSQLへ移行")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="PostgreSQLスキーマ名")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="一括投入件数")
    parser.add_argument("--verify-only", action="store_true", help="投入せずAccess/PostgreSQL件数だけ再確認")
    parser.add_argument(
        "--append-missing",
        action="store_true",
        help="PostgreSQLに存在しないAccess行だけを追加投入",
    )
    parser.add_argument("--delete-extra", action="store_true", help="Accessに存在しないPostgreSQL行だけを削除")
    migration_common.add_refresh_mode_arguments(parser, required=False)
    return parser.parse_args()


def setup_logging(error_log_path: Path) -> None:
    migration_common.setup_migration_logging(error_log_path)


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
        if access_table_name in SKIP_ACCESS_TABLES:
            logging.info("移行対象外のためスキップ: %s", access_table_name)
            continue
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
        postgres_name = TABLE_NAME_MAP[access_table_name]
        primary_key = TABLE_PRIMARY_KEY_OVERRIDE.get(postgres_name, table.get("primary_key", []))
        if primary_key:
            pk_columns = set(primary_key)
            columns = [
                ColumnMapping(
                    access_name=column.access_name,
                    postgres_name=column.postgres_name,
                    access_type=column.access_type,
                    postgres_type=column.postgres_type,
                    nullable=False if column.postgres_name in pk_columns else column.nullable,
                    note=(
                        f"{column.note} / PRIMARY KEY"
                        if column.postgres_name in pk_columns and column.note
                        else ("PRIMARY KEY" if column.postgres_name in pk_columns else column.note)
                    ),
                )
                for column in columns
            ]
        mappings.append(
            TableMapping(
                access_name=access_table_name,
                postgres_name=postgres_name,
                table_type=table["table_type"],
                access_row_count=int(table["row_count"] or 0),
                columns=columns,
                primary_key=primary_key,
                indexes=table.get("indexes", []),
            )
        )
    return mappings


def validate_target_tables(mappings: list[TableMapping]) -> None:
    actual = {mapping.access_name for mapping in mappings}
    expected = set(TABLE_NAME_MAP)
    if actual != expected:
        raise ValueError(f"移行対象テーブルが現品票DBの定義と一致しません。不足={sorted(expected - actual)} 想定外={sorted(actual - expected)}")


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
        return serial_columns_support.counter_postgres_type()
    if access_type == "INTEGER":
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
        notes.append(serial_columns_support.counter_column_note())
    if column["access_type"] == "BIT":
        notes.append("AccessのYes/Noをbooleanへ変換")
    return " / ".join(notes)


def migrate(
    database_url: str,
    access_db_path: Path,
    mappings: list[TableMapping],
    schema: str,
    batch_size: int,
    refresh_mode: RefreshMode,
) -> list[MigrationResult]:
    results = [MigrationResult(table=mapping) for mapping in mappings]
    table_names = [mapping.postgres_name for mapping in mappings]
    access_connection = connect_access(access_db_path)
    postgres_connection = psycopg2.connect(database_url)
    try:
        postgres_connection.autocommit = False
        if refresh_mode == RefreshMode.TRUNCATE:
            migration_common.truncate_tables(postgres_connection, schema, table_names)
        else:
            create_schema_and_tables(postgres_connection, schema, mappings)
        for result in results:
            migrate_table(access_connection, postgres_connection, schema, result, batch_size)
            sync_counter_sequences(postgres_connection.cursor(), schema, result.table)
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
        sync_counter_sequences(postgres_cursor, schema, mapping)
        result.status = "成功" if result.access_row_count == result.postgres_row_count else "件数差異"
        logging.info(
            "不足行追記: %s Access=%s PostgreSQL=%s appended=%s",
            mapping.access_name,
            result.access_row_count,
            result.postgres_row_count,
            result.inserted_row_count,
        )


def load_postgres_rows(
    cursor: psycopg2.extensions.cursor,
    schema: str,
    table_name: str,
    column_names: list[str],
) -> list[tuple[Any, ...]]:
    columns = ", ".join(quote_identifier(column) for column in column_names)
    cursor.execute(f"SELECT {columns} FROM {qualified_name(schema, table_name)}")
    return [tuple(normalize_value(value) for value in row) for row in cursor.fetchall()]


def delete_extra_rows(
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
            delete_extra_rows_for_table(access_connection, postgres_connection, schema, result, batch_size)
        postgres_connection.commit()
    except Exception:
        postgres_connection.rollback()
        raise
    finally:
        access_connection.close()
        postgres_connection.close()
    return results


def delete_extra_rows_for_table(
    access_connection: pyodbc.Connection,
    postgres_connection: psycopg2.extensions.connection,
    schema: str,
    result: MigrationResult,
    batch_size: int,
) -> None:
    mapping = result.table
    access_columns = [column.access_name for column in mapping.columns]
    postgres_columns = [column.postgres_name for column in mapping.columns]

    with postgres_connection.cursor() as postgres_cursor:
        result.access_row_count = count_access_rows(access_connection, mapping.access_name)
        result.postgres_row_count = count_postgres_rows(postgres_cursor, schema, mapping.postgres_name)
        if result.postgres_row_count <= result.access_row_count:
            result.status = "成功" if result.access_row_count == result.postgres_row_count else "件数差異"
            logging.info(
                "余剰行なし: %s Access=%s PostgreSQL=%s",
                mapping.access_name,
                result.access_row_count,
                result.postgres_row_count,
            )
            return

        access_rows = load_access_rows(access_connection, mapping.access_name, access_columns)
        access_row_counter = Counter(access_rows)
        extra_ctids = find_extra_postgres_ctids(postgres_cursor, schema, mapping.postgres_name, postgres_columns, access_row_counter)
        for index in range(0, len(extra_ctids), batch_size):
            delete_postgres_ctids(postgres_cursor, schema, mapping.postgres_name, extra_ctids[index : index + batch_size])
        result.inserted_row_count = -len(extra_ctids)
        result.postgres_row_count = count_postgres_rows(postgres_cursor, schema, mapping.postgres_name)
        result.status = "成功" if result.access_row_count == result.postgres_row_count else "件数差異"
        logging.info(
            "余剰行削除: %s Access=%s PostgreSQL=%s deleted=%s",
            mapping.access_name,
            result.access_row_count,
            result.postgres_row_count,
            len(extra_ctids),
        )


def load_access_rows(
    connection: pyodbc.Connection,
    table_name: str,
    column_names: list[str],
) -> list[tuple[Any, ...]]:
    cursor = connection.cursor()
    cursor.execute(build_access_select_sql(table_name, column_names))
    rows: list[tuple[Any, ...]] = []
    while True:
        batch = cursor.fetchmany(DEFAULT_BATCH_SIZE)
        if not batch:
            break
        rows.extend(tuple(normalize_value(value) for value in row) for row in batch)
    return rows


def find_extra_postgres_ctids(
    cursor: psycopg2.extensions.cursor,
    schema: str,
    table_name: str,
    column_names: list[str],
    access_row_counter: Counter[tuple[Any, ...]],
) -> list[str]:
    columns = ", ".join(quote_identifier(column) for column in column_names)
    cursor.execute(f"SELECT ctid::text, {columns} FROM {qualified_name(schema, table_name)}")
    extra_ctids: list[str] = []
    for row in cursor.fetchall():
        ctid = row[0]
        normalized_row = tuple(normalize_value(value) for value in row[1:])
        if access_row_counter[normalized_row] > 0:
            access_row_counter[normalized_row] -= 1
        else:
            extra_ctids.append(ctid)
    return extra_ctids


def delete_postgres_ctids(
    cursor: psycopg2.extensions.cursor,
    schema: str,
    table_name: str,
    ctids: list[str],
) -> None:
    if not ctids:
        return
    cursor.execute(f"DELETE FROM {qualified_name(schema, table_name)} WHERE ctid = ANY(%s::tid[])", (ctids,))


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
            normalized_row = tuple(normalize_value(value) for value in row)
            if postgres_row_counter[normalized_row] > 0:
                postgres_row_counter[normalized_row] -= 1
            else:
                missing_rows.append(normalized_row)
    return missing_rows


def connect_access(access_db_path: Path) -> pyodbc.Connection:
    connection_string = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};" f"DBQ={access_db_path};"
    return pyodbc.connect(connection_string, autocommit=True)


def create_schema_and_tables(
    connection: psycopg2.extensions.connection,
    schema: str,
    mappings: list[TableMapping],
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {quote_identifier(schema)}")
        for mapping in mappings:
            column_sql_parts = [
                build_column_sql(column, mapping.primary_key) for column in mapping.columns
            ]
            if mapping.primary_key and not any(
                serial_columns_support.is_counter_column(column) for column in mapping.columns
            ):
                pk_columns = ", ".join(quote_identifier(name) for name in mapping.primary_key)
                column_sql_parts.append(f"PRIMARY KEY ({pk_columns})")
            column_sql = ",\n    ".join(column_sql_parts)
            table_name = qualified_name(schema, mapping.postgres_name)
            cursor.execute(f"CREATE TABLE {table_name} (\n    {column_sql}\n)")
            cursor.execute(f"COMMENT ON TABLE {table_name} IS %s", (f"元Accessテーブル: {mapping.access_name}",))
            for column in mapping.columns:
                cursor.execute(
                    f"COMMENT ON COLUMN {table_name}.{quote_identifier(column.postgres_name)} IS %s",
                    (f"元Accessカラム: {column.access_name}",),
                )


def build_column_sql(column: ColumnMapping, primary_key: list[str] | None = None) -> str:
    if serial_columns_support.is_counter_column(column):
        return serial_columns_support.build_column_sql(column, quote_identifier)
    is_primary_key = bool(primary_key) and column.postgres_name in primary_key
    nullable_sql = "" if is_primary_key or not column.nullable else ""
    return f"{quote_identifier(column.postgres_name)} {column.postgres_type}{nullable_sql}"


def sync_counter_sequences(
    cursor: psycopg2.extensions.cursor,
    schema: str,
    mapping: TableMapping,
) -> None:
    serial_columns_support.sync_counter_sequences(
        cursor, schema, mapping, quote_identifier, qualified_name, logging
    )


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
                values = [tuple(normalize_value(value) for value in row) for row in rows]
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


def normalize_value(value: Any) -> Any:
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
        "# Access → PostgreSQL 移行対応表",
        "",
        "## 1. 移行概要",
        "",
        f"- 対象Access DB：{meta.get('database_path', '')}",
        f"- 移行先PostgreSQL DB：{extract_database_name(env['DATABASE_URL'])}",
        "- 接続情報：",
        "  - `.env` の DATABASE_URL を参照",
        f"- 移行日：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- 作成者：Codex",
        "- 備考：現品票DBの15テーブルを忠実に移行。日本語名はPostgreSQL用に英語/ローマ字のスネークケースへ変換し、元名はコメントと本対応表で追跡可能。",
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
        lines.append(
            f"| {index} | {mapping.access_name} | {mapping.postgres_name} | {mapping.table_type} | {access_count} | {postgres_count} | {note} |"
        )

    lines.extend(["", "## 3. テーブル別カラム対応表", ""])
    for mapping in mappings:
        lines.extend(
            [
                f"### Accessテーブル名：{mapping.access_name}",
                f"### PostgreSQLテーブル名：{mapping.postgres_name}",
                "",
                "| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |",
                "|---:|---|---|---|---|---|---|",
            ]
        )
        for index, column in enumerate(mapping.columns, start=1):
            nullable = "可" if column.nullable else "不可"
            lines.append(
                f"| {index} | {column.access_name} | {column.access_type} | {column.postgres_name} | {column.postgres_type} | {nullable} | {column.note} |"
            )
        lines.append("")

    lines.extend(
        [
            "## 4. 主キー・インデックス情報",
            "",
            "| Accessテーブル名 | PostgreSQLテーブル名 | 主キー | インデックス | 備考 |",
            "|---|---|---|---|---|",
        ]
    )
    for mapping in mappings:
        primary_key = ", ".join(mapping.primary_key) if mapping.primary_key else "検出なし"
        indexes = ", ".join(index.get("name", "") for index in mapping.indexes) or "検出なし"
        lines.append(f"| {mapping.access_name} | {mapping.postgres_name} | {primary_key} | {indexes} | FKは未検出 |")

    lines.extend(
        [
            "",
            "## 5. 型変換ルール",
            "",
            "| Access型 | PostgreSQL型 | 備考 |",
            "|---|---|---|",
            "| VARCHAR | varchar(n) | Accessのサイズを維持 |",
            "| COUNTER | bigserial | " + serial_columns_support.counter_type_mapping_note() + " |",
            "| INTEGER | integer | 整数 |",
            "| DOUBLE | double precision | 浮動小数 |",
            "| DATETIME | timestamp | Accessの日付/時刻を保持 |",
            "| BIT | boolean | Yes/No型 |",
            "",
            "## 6. アプリ接続時の参照情報",
            "",
            "### 接続先",
            "",
            "```text",
            ".env の DATABASE_URL を使用",
            "```",
            "",
            "### 主に参照するテーブル",
            "",
            "| 用途 | PostgreSQLテーブル名 | 主なキー | 備考 |",
            "| -- | --------------- | ---- | -- |",
        ]
    )
    for mapping in mappings:
        lines.append(f"| {infer_table_purpose(mapping)} | {mapping.postgres_name} | {infer_key_columns(mapping)} | 元 {mapping.access_name} |")

    lines.extend(
        [
            "",
            "### 主要カラム",
            "",
            "| 用途 | PostgreSQLテーブル名 | PostgreSQLカラム名 | 元Accessカラム名 | 備考 |",
            "| -- | --------------- | -------------- | ----------- | -- |",
        ]
    )
    for mapping in mappings:
        for column in mapping.columns:
            if column.postgres_name in IMPORTANT_COLUMN_NAMES:
                lines.append(
                    f"| {infer_column_purpose(column)} | {mapping.postgres_name} | {column.postgres_name} | {column.access_name} | Accessの値をそのまま保持 |"
                )

    lines.extend(["", "## 7. 注意事項・要確認事項", ""])
    lines.extend(build_caution_lines(meta, mappings))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def build_caution_lines(meta: dict[str, Any], mappings: list[TableMapping]) -> list[str]:
    lines = [
        "- AccessのFKメタデータはODBCドライバが返さなかったため、外部キー制約は作成していません。",
        "- " + serial_columns_support.counter_caution_note(),
        "- 移行対象外: `t_QR履歴(backup_260521)` / `t_QR履歴Tmp`（バックアップ・一時テーブルのため PostgreSQL へは移行しません）。",
        "- `delivery_label_defect_details` / `delivery_label_history` は `production_lot_id` を PRIMARY KEY（NOT NULL・重複なし）としています。",
        "- `.env` の `ACCESS_DB_PATH` が実ファイルを指していない場合は、メタJSONの `database_path` を使用しています。",
    ]
    zero_tables = [mapping.access_name for mapping in mappings if mapping.access_row_count == 0]
    if zero_tables:
        lines.append(f"- 0件テーブルも構造再現のため作成しています: {', '.join(zero_tables)}")
    for warning in meta.get("warnings", []):
        lines.append(f"- メタ抽出警告：{warning}")
    return lines


def write_result(path: Path, access_db_path: Path, results: list[MigrationResult]) -> None:
    lines = [
        "# Access → PostgreSQL 移行結果",
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


def infer_table_purpose(mapping: TableMapping) -> str:
    if "QR履歴" in mapping.access_name:
        return "QR履歴"
    if "現品票履歴" in mapping.access_name:
        return "現品票履歴"
    if "数量差異" in mapping.access_name:
        return "数量差異"
    if "工程マスタ" in mapping.access_name:
        return "工程マスタ"
    if "不具合" in mapping.access_name:
        return "現品票不具合"
    if "ログ" in mapping.access_name:
        return "ログ"
    return "参照テーブル"


def infer_key_columns(mapping: TableMapping) -> str:
    preferred_order = ["id", "qr_code", "production_lot_id", "product_code", "process_code", "date_time"]
    existing_columns = {column.postgres_name for column in mapping.columns}
    keys = [column for column in preferred_order if column in existing_columns]
    return ", ".join(keys) if keys else "要確認"


def infer_column_purpose(column: ColumnMapping) -> str:
    purposes = {
        "id": "ID",
        "date_time": "日時",
        "qr_code": "QRコード",
        "production_lot_id": "生産ロット",
        "date_value": "日付",
        "process": "工程",
        "position": "位置",
        "quantity": "数量",
        "process_code": "工程コード",
        "process_name": "工程名",
        "product_code": "品番",
        "product_name": "品名",
        "customer": "客先",
        "instruction_date": "指示日",
        "current_process_name": "現在工程名",
        "current_process_code": "現在工程コード",
    }
    return purposes.get(column.postgres_name, column.access_name)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def qualified_name(schema: str, table_name: str) -> str:
    return f"{quote_identifier(schema)}.{quote_identifier(table_name)}"


def extract_database_name(database_url: str) -> str:
    parsed = urlparse(database_url)
    return parsed.path.lstrip("/") or "要確認"


if __name__ == "__main__":
    raise SystemExit(main())
