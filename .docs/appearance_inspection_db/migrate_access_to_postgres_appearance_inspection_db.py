"""外観検査記録DBをAccessからPostgreSQLへ忠実に移行する対象専用スクリプト。

このファイルは .docs/appearance_inspection_db 専用です。
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
META_FILE = "外観検査記録DB_meta.json"
RESULT_FILE = "migration_result_appearance_inspection_db.md"
MAPPING_FILE = "migration_mapping_appearance_inspection_db.md"
ERROR_LOG_FILE = "migration_error_appearance_inspection_db.log"
DEFAULT_SCHEMA = "public"
DEFAULT_BATCH_SIZE = 1000


TABLE_NAME_MAP = {
    "t_Excel現品票履歴": "excel_product_slip_history",
    "t_チェックシートリスト": "check_sheet_list",
    "t_不具合情報": "defect_information",
    "t_外観検査記録": "appearance_inspection_records",
    "t_外観検査記録保存": "appearance_inspection_record_archives",
    "t_外観検査集計": "appearance_inspection_summaries",
    "t_外観検査集計保存": "appearance_inspection_summary_archives",
    "t_工程マスタ": "process_master",
    "t_数値検査員マスタ": "numeric_inspector_master",
    "t_数値検査記録": "numeric_inspection_records",
    "t_検査中": "inspection_in_progress",
    "t_検査員マスタ": "inspector_master",
    "t_検査者マスタ": "inspection_person_master",
}


COLUMN_NAME_MAP = {
    "ID": "id",
    "No": "no",
    "生産ロットID": "production_lot_id",
    "号機": "machine_no",
    "品番": "product_code",
    "品名": "product_name",
    "客先": "customer",
    "材質": "material",
    "材料ロットNO": "material_lot_no",
    "数量": "quantity",
    "備考": "remarks",
    "指示日": "instruction_date",
    "完了フラグ": "completion_flag",
    "ファイルNo": "file_no",
    "検査者1": "inspector_1",
    "検査者2": "inspector_2",
    "検査者3": "inspector_3",
    "検査者4": "inspector_4",
    "検査者5": "inspector_5",
    "時間": "time_value",
    "総不具合数": "total_defect_count",
    "不良率": "defect_rate",
    "外観キズ": "appearance_scratch",
    "圧痕": "dent",
    "切粉": "cutting_chip",
    "毟れ": "mushire",
    "穴大": "oversized_hole",
    "穴小": "undersized_hole",
    "穴キズ": "hole_scratch",
    "バリ": "burr",
    "短寸": "short_length",
    "面粗": "rough_surface",
    "サビ": "rust",
    "ボケ": "blur",
    "挽目": "turning_mark",
    "汚れ": "stain",
    "メッキ": "plating",
    "落下": "dropped",
    "フクレ": "swelling",
    "ツブレ": "crush",
    "ボッチ": "bump",
    "段差": "step",
    "バレル石": "barrel_stone",
    "径プラス": "diameter_plus",
    "径マイナス": "diameter_minus",
    "ゲージ": "gauge",
    "異物混入": "foreign_matter",
    "形状不良": "shape_defect",
    "こすれ": "abrasion",
    "変色シミ": "discoloration_stain",
    "材料キズ": "material_scratch",
    "ゴミ": "dust",
    "その他": "other",
    "その他内容": "other_detail",
    "検査員ID": "inspector_id",
    "工程NO": "process_no",
    "日付": "inspection_date",
    "時刻": "time_at",
    "更新フラグ": "update_flag",
    "集計除外フラグ": "aggregation_exclusion_flag",
    "作業時間": "work_time",
    "工程名": "process_name",
    "区別": "category",
    "表示フラグ": "display_flag",
    "検査員名": "inspector_name",
    "表示位置": "display_position",
    "チーム": "team",
    "ふりがな": "furigana",
    "日付時刻": "inspected_at",
    "検査者": "inspector_name",
}


IMPORTANT_COLUMN_NAMES = {
    "id",
    "no",
    "production_lot_id",
    "machine_no",
    "product_code",
    "product_name",
    "customer",
    "instruction_date",
    "inspection_date",
    "inspected_at",
    "quantity",
    "inspector_id",
    "process_no",
    "process_name",
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
    error_log_path = TARGET_DIR / ERROR_LOG_FILE
    setup_logging(error_log_path)

    try:
        env = load_env(TARGET_DIR / ".env")
        meta = load_meta(TARGET_DIR / META_FILE)
        access_db_path = resolve_access_db_path(env, meta)
        mappings = build_mappings(meta)
        validate_target_tables(mappings)
        write_mapping(TARGET_DIR / MAPPING_FILE, env, meta, mappings, [])

        if args.verify_only:
            results = verify_counts(env["DATABASE_URL"], access_db_path, mappings, args.schema)
        else:
            refresh_mode = migration_common.resolve_refresh_mode(args)
            migration_common.run_pre_migration_refresh(env["DATABASE_URL"], refresh_mode, args.schema)
            results = migrate(
                database_url=env["DATABASE_URL"],
                access_db_path=access_db_path,
                mappings=mappings,
                schema=args.schema,
                batch_size=args.batch_size,
                refresh_mode=refresh_mode,
            )
        write_mapping(TARGET_DIR / MAPPING_FILE, env, meta, mappings, results)
        write_result(TARGET_DIR / RESULT_FILE, access_db_path, results)
        return 0 if all(result.status == "成功" for result in results) else 1
    except Exception:
        logging.exception("移行処理が失敗しました")
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="外観検査記録DBをPostgreSQLへ移行")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="PostgreSQLスキーマ名")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="一括投入件数")
    parser.add_argument("--verify-only", action="store_true", help="投入せずAccess/PostgreSQL件数だけ再確認")
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
        if access_table_name not in TABLE_NAME_MAP:
            raise ValueError(f"未定義のテーブル名があります。推測せず停止します: {access_table_name}")
        postgres_table_name = TABLE_NAME_MAP[access_table_name]
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
        mappings.append(
            TableMapping(
                access_name=access_table_name,
                postgres_name=postgres_table_name,
                table_type=table["table_type"],
                access_row_count=int(table["row_count"] or 0),
                columns=columns,
                primary_key=table.get("primary_key", []),
                indexes=table.get("indexes", []),
            )
        )
    return mappings


def validate_target_tables(mappings: list[TableMapping]) -> None:
    access_table_names = {mapping.access_name for mapping in mappings}
    expected_table_names = set(TABLE_NAME_MAP)
    missing_tables = expected_table_names - access_table_names
    unexpected_tables = access_table_names - expected_table_names
    if missing_tables or unexpected_tables:
        raise ValueError(
            "移行対象テーブルが外観検査記録DBの定義と一致しません。"
            f" 不足: {sorted(missing_tables)} / 想定外: {sorted(unexpected_tables)}"
        )


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
                result.postgres_row_count = count_postgres_rows(
                    postgres_cursor,
                    schema,
                    result.table.postgres_name,
                )
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


def connect_access(access_db_path: Path) -> pyodbc.Connection:
    connection_string = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={access_db_path};"
    )
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
        joined = ", ".join(existing_tables)
        raise RuntimeError(f"移行先テーブルが既に存在するため停止しました: {joined}")


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
            cursor.execute(
                f"COMMENT ON TABLE {table_name} IS %s",
                (f"元Accessテーブル: {mapping.access_name}",),
            )
            for column in mapping.columns:
                cursor.execute(
                    f"COMMENT ON COLUMN {table_name}.{quote_identifier(column.postgres_name)} IS %s",
                    (f"元Accessカラム: {column.access_name}",),
                )


def build_column_sql(column: ColumnMapping) -> str:
    return serial_columns_support.build_column_sql(column, quote_identifier)


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
        logging.info(
            "移行完了: %s Access=%s PostgreSQL=%s",
            mapping.access_name,
            result.access_row_count,
            result.postgres_row_count,
        )
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
        "- 備考：外観検査記録DBの13テーブルを忠実に移行。日本語名はPostgreSQL用に英語/ローマ字のスネークケースへ変換し、元名はコメントと本対応表で追跡可能。",
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
            f"| {index} | {mapping.access_name} | {mapping.postgres_name} | {mapping.table_type} | "
            f"{access_count} | {postgres_count} | {note} |"
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
                f"| {index} | {column.access_name} | {column.access_type} | {column.postgres_name} | "
                f"{column.postgres_type} | {nullable} | {column.note} |"
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
        key_columns = infer_key_columns(mapping)
        lines.append(
            f"| {infer_table_purpose(mapping)} | {mapping.postgres_name} | {key_columns} | 元 {mapping.access_name} |"
        )

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
                    f"| {infer_column_purpose(column)} | {mapping.postgres_name} | {column.postgres_name} | "
                    f"{column.access_name} | Accessの値をそのまま保持 |"
                )

    has_counter = any(column.access_type == "COUNTER" for mapping in mappings for column in mapping.columns)
    caution_lines = [
        "- AccessのFKメタデータはODBCドライバが返さなかったため、外部キー制約は作成していません。",
        "- `時刻` はAccess上で `1899-12-30 HH:MM:SS` のtimestampとして保持されている場合、そのままtimestampで移行します。",
        "- `.env` の `ACCESS_DB_PATH` が実ファイルを指していない場合は、メタJSONの `database_path` を使用しています。",
    ]
    if has_counter:
        caution_lines.insert(
            1,
            "- " + serial_columns_support.counter_caution_note(),
        )
    else:
        caution_lines.insert(1, "- 主キーはメタデータ上は検出なしです。")
    for warning in meta.get("warnings", []):
        caution_lines.append(f"- メタ抽出警告：{warning}")

    lines.extend(
        [
            "",
            "## 7. 注意事項・要確認事項",
            "",
        ]
        + caution_lines
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
            f"| {result.table.access_name} | {result.table.postgres_name} | {access_count} | "
            f"{result.postgres_row_count} | {result.inserted_row_count} | {result.status} | {result.error} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def infer_table_purpose(mapping: TableMapping) -> str:
    if "Excel現品票履歴" in mapping.access_name:
        return "現品票履歴"
    if "外観検査記録" in mapping.access_name:
        return "外観検査記録"
    if "外観検査集計" in mapping.access_name:
        return "外観検査集計"
    if "不具合" in mapping.access_name:
        return "不具合情報"
    if "マスタ" in mapping.access_name:
        return "マスタ"
    return "参照テーブル"


def infer_key_columns(mapping: TableMapping) -> str:
    preferred_order = ["id", "production_lot_id", "product_code", "inspector_id", "process_no", "no"]
    existing_columns = {column.postgres_name for column in mapping.columns}
    keys = [column for column in preferred_order if column in existing_columns]
    return ", ".join(keys) if keys else "要確認"


def infer_column_purpose(column: ColumnMapping) -> str:
    purposes = {
        "id": "ID",
        "no": "番号",
        "production_lot_id": "生産ロット",
        "machine_no": "号機",
        "product_code": "品番",
        "product_name": "品名",
        "customer": "客先",
        "instruction_date": "指示日",
        "inspection_date": "検査日",
        "inspected_at": "検査日時",
        "quantity": "数量",
        "inspector_id": "検査員",
        "process_no": "工程",
        "process_name": "工程名",
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
