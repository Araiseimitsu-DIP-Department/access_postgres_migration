"""購入品集計DBをPostgreSQLへ移行する専用スクリプト。"""

from __future__ import annotations

import argparse
import csv
import logging
from contextlib import closing
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import sys

_MIGRATION_ROOT = Path(__file__).resolve().parents[2]
_SRC = _MIGRATION_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from access_migration.migration_common import (  # noqa: E402
    REFRESH_MODE_HELP,
    RefreshMode,
    add_refresh_mode_arguments,
    mask_database_url,
    resolve_refresh_mode,
    run_pre_migration_refresh,
    setup_migration_logging,
)
from access_migration import serial_columns as serial_columns_support  # noqa: E402

import psycopg2
import pyodbc
from dotenv import dotenv_values
from psycopg2 import sql


TARGET_DIR = Path(__file__).resolve().parent
META_FILE = TARGET_DIR / "購入品集計DB_meta.json"
ENV_FILE = TARGET_DIR / ".env"
MAPPING_FILE = TARGET_DIR / "migration_mapping.md"
RESULT_FILE = TARGET_DIR / "migration_result.md"
ERROR_LOG_FILE = TARGET_DIR / "migration_error.log"
CSV_DUMP_DIR = TARGET_DIR / "csv_exports"


TABLE_NAME_MAP = {
    "t_クロス集計用": "purchase_cross_summary",
    "t_コントロール": "migration_control",
    "t_科目名マスタ": "account_subject_master",
    "t_購入先マスタ": "supplier_master",
    "t_購入品明細": "purchase_detail",
    "t_購入者マスタ": "purchaser_master",
}


COLUMN_NAME_MAP = {
    "ID": "id",
    "費目コード": "expense_item_code",
    "費目名": "expense_item_name",
    "購入先コード": "supplier_code",
    "購入先名": "supplier_name",
    "購入月": "purchase_month",
    "金額": "amount",
    "購入月From": "purchase_month_from",
    "購入月To": "purchase_month_to",
    "集計方法": "aggregation_method",
    "科目コード": "account_subject_code",
    "科目名": "account_subject_name",
    "締日": "closing_day",
    "かな": "kana",
    "表示フラグ": "display_flag",
    "納入日": "delivery_date",
    "購入者コード": "purchaser_code",
    "購入者名": "purchaser_name",
    "納品書番号": "delivery_note_number",
    "品名": "product_name",
    "数量": "quantity",
    "単価": "unit_price",
    "単位": "unit",
    "備考": "remarks",
    "入力日": "input_date",
}


def main() -> int:
    """コマンドライン引数に従って移行処理を実行する。"""

    parser = argparse.ArgumentParser(description="購入品集計DB Access -> PostgreSQL migration")
    add_refresh_mode_arguments(parser, required=False)
    parser.add_argument("--dump-csv", action="store_true", help="Accessから読み取ったデータをCSVにも保存")
    parser.add_argument("--reset-sequences", action="store_true", help="COUNTER列のidentity sequenceだけを補正")
    args = parser.parse_args()

    has_refresh_mode = args.drop_database or args.drop_table or args.truncate
    if not has_refresh_mode and not args.reset_sequences:
        parser.error(REFRESH_MODE_HELP)

    setup_migration_logging(ERROR_LOG_FILE)
    logger = logging.getLogger("purchase_summary_migration")
    config = load_env()
    metadata = load_metadata()
    access_db_path = resolve_access_db_path(config["ACCESS_DB_PATH"], metadata)
    started_at = datetime.now().astimezone()
    result: dict[str, Any] = {
        "started_at": started_at,
        "database_url_masked": mask_database_url(config["DATABASE_URL"]),
        "access_db_path": access_db_path,
        "schema_applied": False,
        "data_migrated": False,
        "access_available": False,
        "errors": [],
        "table_results": [],
    }

    try:
        refresh_mode = resolve_refresh_mode(args) if has_refresh_mode else None
        if refresh_mode in (RefreshMode.DROP_DATABASE, RefreshMode.DROP_TABLE):
            run_pre_migration_refresh(config["DATABASE_URL"], refresh_mode)

        with closing(psycopg2.connect(config["DATABASE_URL"])) as pg_conn:
            if refresh_mode in (RefreshMode.DROP_DATABASE, RefreshMode.DROP_TABLE):
                apply_schema(pg_conn, metadata, logger)
                result["schema_applied"] = True

            if refresh_mode is not None:
                truncate_before_load = refresh_mode == RefreshMode.TRUNCATE
                migrate_data(
                    pg_conn,
                    access_db_path,
                    metadata,
                    truncate_before_load,
                    args.dump_csv,
                    logger,
                    result,
                )
                result["data_migrated"] = not result["errors"]
            elif args.reset_sequences:
                with pg_conn.cursor() as pg_cur:
                    reset_identity_sequences(pg_cur, metadata, logger)

            if args.reset_sequences and refresh_mode is not None:
                with pg_conn.cursor() as pg_cur:
                    reset_identity_sequences(pg_cur, metadata, logger)

            result["table_results"] = collect_table_results(pg_conn, metadata)
            pg_conn.commit()
    except Exception as exc:  # noqa: BLE001
        logger.exception("PostgreSQL処理でエラーが発生しました")
        result["errors"].append(str(exc))

    write_mapping(metadata, result)
    write_result(metadata, result)
    return 1 if result["errors"] else 0


def load_env() -> dict[str, str]:
    """対象フォルダ内の.envを読み込む。"""

    values = dotenv_values(ENV_FILE)
    required_keys = ["DATABASE_URL", "ACCESS_DB_PATH"]
    missing = [key for key in required_keys if not values.get(key)]
    if missing:
        raise ValueError(f".envに必須項目がありません: {', '.join(missing)}")
    return {key: str(values[key]) for key in values if values.get(key) is not None}


def load_metadata() -> dict[str, Any]:
    """Access解析済みJSONを読み込む。"""

    import json

    return json.loads(META_FILE.read_text(encoding="utf-8-sig"))


def resolve_access_db_path(env_access_path: str, metadata: dict[str, Any]) -> str:
    """実際に参照するAccess DBパスを決定する。"""

    placeholder_values = {"", "C:/path/to/access_database.accdb", "C:\\path\\to\\access_database.accdb"}
    if env_access_path.strip() not in placeholder_values:
        return env_access_path
    metadata_path = str(metadata.get("database_path", "")).strip()
    if metadata_path:
        return metadata_path
    return env_access_path


def apply_schema(pg_conn: Any, metadata: dict[str, Any], logger: logging.Logger) -> None:
    """メタデータに基づくPostgreSQLテーブルを作成する。"""

    with pg_conn.cursor() as cur:
        for table in metadata["tables"]:
            pg_table = TABLE_NAME_MAP[table["name"]]
            columns = []
            for column in table["columns"]:
                pg_column = COLUMN_NAME_MAP[column["name"]]
                if column["access_type"] == "COUNTER":
                    columns.append(sql.SQL("{} BIGSERIAL PRIMARY KEY").format(sql.Identifier(pg_column)))
                    continue
                nullable_sql = sql.SQL("") if column.get("nullable", True) else sql.SQL(" NOT NULL")
                columns.append(
                    sql.SQL("{} {}{}").format(
                        sql.Identifier(pg_column),
                        sql.SQL(postgres_type(column)),
                        nullable_sql,
                    )
                )
            create_sql = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                sql.Identifier(pg_table),
                sql.SQL(", ").join(columns),
            )
            cur.execute(create_sql)
            cur.execute(
                sql.SQL("COMMENT ON TABLE {} IS %s").format(sql.Identifier(pg_table)),
                (f"Access table: {table['name']}",),
            )
            for column in table["columns"]:
                cur.execute(
                    sql.SQL("COMMENT ON COLUMN {}.{} IS %s").format(
                        sql.Identifier(pg_table),
                        sql.Identifier(COLUMN_NAME_MAP[column["name"]]),
                    ),
                    (f"Access column: {column['name']}; Access type: {column['access_type']}",),
                )
            logger.info("PostgreSQLテーブル作成確認: %s", pg_table)


def migrate_data(
    pg_conn: Any,
    access_db_path: str,
    metadata: dict[str, Any],
    truncate: bool,
    dump_csv: bool,
    logger: logging.Logger,
    result: dict[str, Any],
) -> None:
    """AccessからPostgreSQLへ全テーブルのデータを移行する。"""

    access_path = Path(access_db_path)
    if not access_path.exists():
        message = f"Access DBファイルが見つかりません: {access_db_path}"
        logger.error(message)
        result["errors"].append(message)
        return

    conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_db_path};"
    with closing(pyodbc.connect(conn_str, timeout=10)) as access_conn:
        result["access_available"] = True
        with pg_conn.cursor() as pg_cur:
            if truncate:
                truncate_tables(pg_cur, metadata, logger)

            for table in metadata["tables"]:
                migrate_table(access_conn, pg_cur, table, dump_csv, logger)
            reset_identity_sequences(pg_cur, metadata, logger)


def truncate_tables(pg_cur: Any, metadata: dict[str, Any], logger: logging.Logger) -> None:
    """対象テーブルを投入前に空にする。"""

    tables = [sql.Identifier(TABLE_NAME_MAP[table["name"]]) for table in metadata["tables"]]
    pg_cur.execute(sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY").format(sql.SQL(", ").join(tables)))
    logger.warning("PostgreSQL対象テーブルをTRUNCATEしました")


def migrate_table(access_conn: Any, pg_cur: Any, table: dict[str, Any], dump_csv: bool, logger: logging.Logger) -> None:
    """1テーブル分のAccessデータをPostgreSQLへ投入する。"""

    access_table = table["name"]
    pg_table = TABLE_NAME_MAP[access_table]
    access_columns = [column["name"] for column in table["columns"]]
    pg_columns = [COLUMN_NAME_MAP[column] for column in access_columns]

    access_sql = f"SELECT {', '.join(f'[{name}]' for name in access_columns)} FROM [{access_table}]"
    rows = access_conn.cursor().execute(access_sql).fetchall()
    converted_rows = [tuple(convert_value(value) for value in row) for row in rows]

    if dump_csv:
        write_csv(pg_table, pg_columns, converted_rows)

    insert_sql = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(pg_table),
        sql.SQL(", ").join(sql.Identifier(column) for column in pg_columns),
        sql.SQL(", ").join(sql.Placeholder() for _ in pg_columns),
    )
    pg_cur.executemany(insert_sql, converted_rows)
    logger.info("データ移行完了: %s -> %s (%s件)", access_table, pg_table, len(converted_rows))


def reset_identity_sequences(pg_cur: Any, metadata: dict[str, Any], logger: logging.Logger) -> None:
    """COUNTER列に対応するidentity sequenceを最大値の次へ進める。"""

    for table in metadata["tables"]:
        pg_table = TABLE_NAME_MAP[table["name"]]
        for column in table["columns"]:
            if column["access_type"] != "COUNTER":
                continue
            pg_column = COLUMN_NAME_MAP[column["name"]]
            pg_cur.execute(
                sql.SQL("SELECT MAX({column}) FROM {table}").format(
                    column=sql.Identifier(pg_column),
                    table=sql.Identifier(pg_table),
                )
            )
            max_row = pg_cur.fetchone()
            max_id = max_row[0] if max_row else None

            pg_cur.execute(
                "SELECT pg_get_serial_sequence(%s, %s)",
                (pg_table, pg_column),
            )
            sequence_row = pg_cur.fetchone()
            sequence_name = sequence_row[0] if sequence_row else None
            if not sequence_name:
                logger.warning("シーケンスが見つかりません（スキップ）: %s.%s", pg_table, pg_column)
                continue

            if max_id is None:
                pg_cur.execute("SELECT setval(%s, 1, false)", (sequence_name,))
            else:
                pg_cur.execute("SELECT setval(%s, %s, true)", (sequence_name, max_id))
            logger.info("identity sequence更新: %s.%s (max=%s)", pg_table, pg_column, max_id if max_id is not None else 0)


def write_csv(pg_table: str, headers: list[str], rows: list[tuple[Any, ...]]) -> None:
    """移行元データのCSV控えを出力する。"""

    CSV_DUMP_DIR.mkdir(exist_ok=True)
    path = CSV_DUMP_DIR / f"{pg_table}.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)


def collect_table_results(pg_conn: Any, metadata: dict[str, Any]) -> list[dict[str, Any]]:
    """PostgreSQL側件数を収集する。"""

    rows = []
    with pg_conn.cursor() as cur:
        for table in metadata["tables"]:
            pg_table = TABLE_NAME_MAP[table["name"]]
            pg_count: int | None
            try:
                cur.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(pg_table)))
                pg_count = int(cur.fetchone()[0])
            except Exception:
                pg_conn.rollback()
                pg_count = None
            rows.append(
                {
                    "access_table": table["name"],
                    "postgres_table": pg_table,
                    "table_type": table.get("table_type", "TABLE"),
                    "access_count": table.get("row_count"),
                    "postgres_count": pg_count,
                }
            )
    return rows


def postgres_type(column: dict[str, Any]) -> str:
    """Access列情報からPostgreSQL型を返す。"""

    access_type = column["access_type"]
    if access_type == "COUNTER":
        return serial_columns_support.counter_postgres_type()
    if access_type in {"VARCHAR", "CHAR"}:
        size = column.get("column_size")
        return f"VARCHAR({size})" if size else "TEXT"
    if access_type in {"LONGCHAR", "LONGVARCHAR"}:
        return "TEXT"
    if access_type in {"DATETIME", "DATE"}:
        return "TIMESTAMP"
    if access_type in {"CURRENCY", "DECIMAL", "NUMERIC"}:
        size = column.get("column_size") or 19
        digits = column.get("decimal_digits")
        return f"NUMERIC({size},{digits})" if digits is not None else "NUMERIC"
    if access_type in {"INTEGER", "SMALLINT"}:
        return "INTEGER"
    if access_type in {"DOUBLE", "FLOAT", "REAL"}:
        return "DOUBLE PRECISION"
    if access_type in {"BIT", "YESNO", "BOOLEAN"}:
        return "BOOLEAN"
    return "TEXT"


def convert_value(value: Any) -> Any:
    """pyodbcから得た値をpsycopg2へ渡しやすい型に整える。"""

    if isinstance(value, Decimal):
        return value
    return value


def write_mapping(metadata: dict[str, Any], result: dict[str, Any]) -> None:
    """後続アプリ開発向けの移行対応表Markdownを出力する。"""

    lines = [
        "# Access → PostgreSQL 移行対応表",
        "",
        "## 1. 移行概要",
        "",
        f"- 対象Access DB：`{metadata.get('database_path', result['access_db_path'])}`",
        f"- 移行先PostgreSQL DB：`{database_name_from_url(result['database_url_masked'])}`",
        "- 接続情報：",
        "  - `.env` の `DATABASE_URL` を参照",
        f"- 移行日：{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- 作成者：Codex",
        "- 備考：Access実ファイルに接続できない場合、件数は解析済みメタデータを元に記載しています。",
        "",
        "## 2. 移行対象テーブル一覧",
        "",
        "| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |",
        "|---:|---|---|---|---:|---:|---|",
    ]
    result_by_table = {row["access_table"]: row for row in result.get("table_results", [])}
    for index, table in enumerate(metadata["tables"], start=1):
        table_result = result_by_table.get(table["name"], {})
        pg_count = format_count(table_result.get("postgres_count"))
        note = "リンクテーブルではなく実テーブル" if table.get("table_type") == "TABLE" else "要確認"
        lines.append(
            f"| {index} | `{table['name']}` | `{TABLE_NAME_MAP[table['name']]}` | {table.get('table_type', '')} | "
            f"{format_count(table.get('row_count'))} | {pg_count} | {note} |"
        )

    lines.extend(["", "## 3. テーブル別カラム対応表", ""])
    for table in metadata["tables"]:
        lines.extend(
            [
                f"### Accessテーブル名：{table['name']}",
                f"### PostgreSQLテーブル名：{TABLE_NAME_MAP[table['name']]}",
                "",
                "| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |",
                "|---:|---|---|---|---|---|---|",
            ]
        )
        for index, column in enumerate(table["columns"], start=1):
            nullable = "可" if column.get("nullable", True) else "不可"
            note = serial_columns_support.counter_column_note() if column["access_type"] == "COUNTER" else ""
            lines.append(
                f"| {index} | `{column['name']}` | {column['access_type']} | "
                f"`{COLUMN_NAME_MAP[column['name']]}` | {postgres_type(column)} | {nullable} | {note} |"
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
    for table in metadata["tables"]:
        primary_key = ", ".join(table.get("primary_key") or []) or "未検出"
        indexes = ", ".join(index.get("name", "") for index in table.get("indexes", [])) or "未検出"
        lines.append(
            f"| `{table['name']}` | `{TABLE_NAME_MAP[table['name']]}` | {primary_key} | {indexes} | "
            "Access ODBCメタデータ上はPK/Index未検出。業務上の一意性は要確認。 |"
        )

    lines.extend(
        [
            "",
            "## 5. 型変換ルール",
            "",
            "| Access型 | PostgreSQL型 | 備考 |",
            "|---|---|---|",
            "| COUNTER | bigserial | " + serial_columns_support.counter_type_mapping_note() + " |",
            "| VARCHAR | VARCHAR(n) | Accessのcolumn_sizeを反映。 |",
            "| DATETIME | TIMESTAMP | Accessの日付時刻を保持。日付のみかは要確認。 |",
            "| INTEGER | INTEGER | 整数。 |",
            "| DOUBLE | DOUBLE PRECISION | 浮動小数。 |",
            "| CURRENCY | NUMERIC(19,4) | 金額。小数4桁を保持。 |",
            "| YES/NO | BOOLEAN | 今回の対象列には未検出。 |",
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
            "| 購入品明細 | `purchase_detail` | `id`, `purchase_month`, `supplier_code`, `purchaser_code` | 主データ。Access `t_購入品明細`。 |",
            "| 購入先マスタ | `supplier_master` | `supplier_code` | 購入先名・費目情報。業務上一意か要確認。 |",
            "| 購入者マスタ | `purchaser_master` | `purchaser_code` | 購入者名。業務上一意か要確認。 |",
            "| 科目名マスタ | `account_subject_master` | `account_subject_code` | 科目コードと科目名。 |",
            "| クロス集計用 | `purchase_cross_summary` | `id`, `purchase_month` | Access側の集計用テーブル。 |",
            "| コントロール | `migration_control` | `id` | 集計範囲・集計方法の制御値。 |",
            "",
            "### 主要カラム",
            "",
            "| 用途 | PostgreSQLテーブル名 | PostgreSQLカラム名 | 元Accessカラム名 | 備考 |",
            "| -- | --------------- | -------------- | ----------- | -- |",
            "| 購入月 | `purchase_detail` | `purchase_month` | `購入月` | `YYMM`形式と見られるため文字列保持。 |",
            "| 納入日 | `purchase_detail` | `delivery_date` | `納入日` | TIMESTAMP。 |",
            "| 購入先 | `purchase_detail` | `supplier_code`, `supplier_name` | `購入先コード`, `購入先名` | マスタと併用。 |",
            "| 購入者 | `purchase_detail` | `purchaser_code`, `purchaser_name` | `購入者コード`, `購入者名` | マスタと併用。 |",
            "| 金額 | `purchase_detail` | `amount` | `金額` | NUMERIC(19,4)。 |",
            "| 品名 | `purchase_detail` | `product_name` | `品名` | VARCHAR(60)。 |",
            "",
            "## 7. 注意事項・要確認事項",
            "",
        ]
    )
    lines.extend(build_notes(metadata, result))
    MAPPING_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_result(metadata: dict[str, Any], result: dict[str, Any]) -> None:
    """移行実行結果Markdownを出力する。"""

    lines = [
        "# Access → PostgreSQL 移行結果",
        "",
        f"- 実行日時：{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- 対象Access DB：`{metadata.get('database_path', result['access_db_path'])}`",
        f"- 移行先PostgreSQL DB：`{database_name_from_url(result['database_url_masked'])}`",
        f"- スキーマ作成：{'実行' if result.get('schema_applied') else '未実行'}",
        f"- データ移行：{'実行' if result.get('data_migrated') else '未実行または未完了'}",
        "",
        "## 件数確認",
        "",
        "| Accessテーブル名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 差異 |",
        "|---|---|---:|---:|---:|",
    ]
    for row in result.get("table_results", []):
        access_count = row.get("access_count")
        pg_count = row.get("postgres_count")
        diff = "" if access_count is None or pg_count is None else str(pg_count - access_count)
        lines.append(
            f"| `{row['access_table']}` | `{row['postgres_table']}` | {format_count(access_count)} | "
            f"{format_count(pg_count)} | {diff or '確認不可'} |"
        )

    lines.extend(["", "## エラー", ""])
    if result.get("errors"):
        lines.extend(f"- {error}" for error in result["errors"])
    else:
        lines.append("- なし")

    lines.extend(["", "## 注意事項", ""])
    lines.extend(build_notes(metadata, result))
    RESULT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_notes(metadata: dict[str, Any], result: dict[str, Any]) -> list[str]:
    """移行資料に記載する注意事項を組み立てる。"""

    notes = [
        "- Access側のテーブル削除・統合・列削除は行っていません。",
        "- Access ODBCメタデータ上、主キー・インデックス・リレーションは未検出です。後続でAccess画面または業務資料による確認が必要です。",
        "- リンクテーブル相当（ODBC: SYNONYM）は0件です。",
        "- `購入月`はサンプル上`2304`のような値のため、日付型へ変換せずVARCHAR(4)として保持しています。",
        "- `表示フラグ`、`かな`、`締日`はAccess定義どおりVARCHARで保持しています。意味づけは要確認です。",
    ]
    if result.get("errors"):
        notes.append("- Access DBへ接続できなかったため、実データ移行は未完了です。`migration_error.log`を確認してください。")
    if metadata.get("warnings"):
        notes.append(f"- Access解析時警告が{len(metadata['warnings'])}件あります。主に外部キー取得スキップです。")
    return notes


def database_name_from_url(masked_url: str) -> str:
    """URL末尾からDB名を取り出す。"""

    return masked_url.rsplit("/", 1)[-1] if "/" in masked_url else masked_url


def format_count(value: Any) -> str:
    """件数表示用の文字列を返す。"""

    return "確認不可" if value is None else f"{int(value):,}"


if __name__ == "__main__":
    raise SystemExit(main())
