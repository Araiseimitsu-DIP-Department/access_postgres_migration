"""product_master テーブルの作成と初回データ投入（手動実行用）。"""
from __future__ import annotations

import argparse
import logging
import math
import os
import shutil
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterator, Literal
from urllib.parse import quote_plus

import psycopg
import xlwings as xw
from psycopg import sql

_SCRIPT_DIR = Path(__file__).resolve().parent
_MIGRATION_ROOT = _SCRIPT_DIR.parents[1]
_SRC = _MIGRATION_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from access_migration.migration_common import (  # noqa: E402
    RefreshMode,
    add_refresh_mode_arguments,
    drop_database,
    resolve_refresh_mode,
    setup_migration_logging,
)

ERROR_LOG_FILE = _SCRIPT_DIR / "migration_error_arai_masters.log"

TABLE_NAME = "product_master"
DATA_START_ROW = 2
DATA_END_COL = "CE"
LAST_ROW_ANCHOR = "A65536"

PgType = Literal["varchar", "float", "int"]


@dataclass(frozen=True)
class ColumnDef:
    excel_col: str
    header_name: str
    pg_col: str
    pg_type: PgType
    varchar_len: int | None = None
    primary_key: bool = False
    unique: bool = False


COLUMN_DEFS: tuple[ColumnDef, ...] = (
    ColumnDef("BU", "ID", "id", "varchar", 7, primary_key=True, unique=True),
    ColumnDef("A", "製品番号", "product_no", "varchar", 30),
    ColumnDef("B", "別管理番号", "alt_management_no", "varchar", 30),
    ColumnDef("C", "製品名", "product_name", "varchar", 30),
    ColumnDef("D", "客先名", "customer_name", "varchar", 30),
    ColumnDef("E", "次工程", "next_process", "varchar", 10),
    ColumnDef("F", "コード", "process_code", "varchar", 4),
    ColumnDef("G", "締日", "closing_day", "varchar", 2),
    ColumnDef("H", "営業　　　担当", "sales_staff", "varchar", 6),
    ColumnDef("I", "材質＆材料径", "material_and_diameter", "varchar", 80),
    ColumnDef("J", "製品全長", "product_length", "float"),
    ColumnDef("K", "突切", "cutoff", "float"),
    ColumnDef("L", "全長＋突切り幅", "total_length_with_cutoff", "float"),
    ColumnDef("M", "前回　　　加工秒数", "previous_machining_seconds", "float"),
    ColumnDef("N", "日産", "daily_output", "float"),
    ColumnDef("O", "取り数", "pickup_qty", "float"),
    ColumnDef("P", "単価", "unit_price", "float"),
    ColumnDef("Q", "材料費", "material_cost", "float"),
    ColumnDef("R", "加工費", "machining_cost", "float"),
    ColumnDef("S", "処理費", "processing_cost", "float"),
    ColumnDef("T", "製品取扱注意事項", "handling_precautions", "varchar", 20),
    ColumnDef("U", "指示書　有無", "instruction_sheet_flag", "varchar", 1),
    ColumnDef("V", "備考　、条件　等　", "remarks_and_conditions", "varchar", 50),
    ColumnDef("W", "前検", "pre_inspection", "varchar", 1),
    ColumnDef("X", "二次工程先", "secondary_process_dest", "varchar", 20),
    ColumnDef("AI", "L/T", "lead_time", "int"),
    ColumnDef("AJ", "洗浄①", "wash_step_1", "varchar", 10),
    ColumnDef("AK", "工程②", "process_2", "varchar", 30),
    ColumnDef("AL", "処理先", "process_2_vendor", "varchar", 20),
    ColumnDef("AM", "工程②集計", "process_2_total", "varchar", 2),
    ColumnDef("AO", "工程③", "process_3", "varchar", 30),
    ColumnDef("AP", "処理先", "process_3_vendor", "varchar", 20),
    ColumnDef("AQ", "工程③集計", "process_3_total", "varchar", 2),
    ColumnDef("AS", "工程④", "process_4", "varchar", 30),
    ColumnDef("AT", "処理先", "process_4_vendor", "varchar", 20),
    ColumnDef("AU", "工程④集計", "process_4_total", "varchar", 2),
    ColumnDef("AW", "工程⑤", "process_5", "varchar", 30),
    ColumnDef("AX", "処理先", "process_5_vendor", "varchar", 20),
    ColumnDef("AY", "工程⑤集計", "process_5_total", "varchar", 2),
    ColumnDef("BA", "工程⑥", "process_6", "varchar", 30),
    ColumnDef("BB", "処理先", "process_6_vendor", "varchar", 20),
    ColumnDef("BC", "工程⑥集計", "process_6_total", "varchar", 2),
    ColumnDef("BE", "工程⑦", "process_7", "varchar", 30),
    ColumnDef("BF", "処理先", "process_7_vendor", "varchar", 20),
    ColumnDef("BG", "工程⑦集計", "process_7_total", "varchar", 2),
    ColumnDef("BI", "工程⑧", "process_8", "varchar", 30),
    ColumnDef("BJ", "処理先", "process_8_vendor", "varchar", 20),
    ColumnDef("BK", "工程⑧集計", "process_8_total", "varchar", 2),
    ColumnDef("BM", "工程⑨", "process_9", "varchar", 30),
    ColumnDef("BN", "処理先", "process_9_vendor", "varchar", 20),
    ColumnDef("BO", "工程⑨集計", "process_9_total", "varchar", 2),
    ColumnDef("BQ", "梱包形態", "packing_style", "varchar", 30),
    ColumnDef("BR", "梱包仕様", "packing_spec", "varchar", 30),
    ColumnDef("BS", "送り先指定", "destination_spec", "varchar", 30),
    ColumnDef("BT", "外部委託加工費", "external_machining_cost", "float"),
    ColumnDef("BV", "納期　　　担当", "delivery_staff", "varchar", 6),
    ColumnDef("BX", "材料　　　　識別", "material_identification", "varchar", 2),
    ColumnDef("BY", "区分", "category", "varchar", 5),
    ColumnDef("BZ", "用途　情報", "usage_info", "varchar", 255),
    ColumnDef("CA", "備考", "remarks", "varchar", 255),
    ColumnDef("CB", "IATF   対象", "iatf_target", "varchar", 1),
    ColumnDef("CC", "指示書　有無BU", "instruction_sheet_flag_bu", "varchar", 1),
    ColumnDef("CD", "呼出ｺｰﾄﾞ", "call_code", "varchar", 7),
    ColumnDef("CE", "製品単重　　(g)", "unit_weight", "float"),
)


_SCRIPT_DIR_STR = os.path.dirname(os.path.abspath(__file__))


def _config_env_path() -> Path:
    override = os.environ.get("UPDATE_MASTERS_CONFIG_ENV", "").strip()
    if override:
        return Path(override)
    return Path(_SCRIPT_DIR_STR).parent / "config.env"


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise FileNotFoundError(
            f"設定ファイルが見つかりません: {path}\n"
            "config.env を配置して編集してください。"
        )
    values: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition("=")
            if not sep:
                continue
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key] = value
    return values


def _require_env(env: dict[str, str], key: str) -> str:
    value = env.get(key, "").strip()
    if not value:
        raise ValueError(f"config.env に {key} が設定されていません。")
    return value


def _build_postgres_connection_url(env: dict[str, str]) -> str:
    direct = env.get("POSTGRES_CONNECTION_URL", "").strip()
    if direct:
        return direct
    host = _require_env(env, "POSTGRES_HOST")
    port = env.get("POSTGRES_PORT", "5432").strip() or "5432"
    user = _require_env(env, "POSTGRES_USER")
    password = _require_env(env, "POSTGRES_PASSWORD")
    database = _require_env(env, "POSTGRES_DB")
    return (
        f"postgresql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{quote_plus(database)}"
    )


def _pg_type_sql(col: ColumnDef) -> sql.SQL:
    if col.pg_type == "varchar":
        return sql.SQL("VARCHAR({})").format(sql.Literal(col.varchar_len))
    if col.pg_type == "float":
        return sql.SQL("NUMERIC(15, 2)")
    return sql.SQL("INTEGER")


_ENV = _parse_env_file(_config_env_path())
POSTGRES_HOST = _ENV.get("POSTGRES_HOST", "").strip()
POSTGRES_PORT = _ENV.get("POSTGRES_PORT", "5432").strip() or "5432"
POSTGRES_USER = _ENV.get("POSTGRES_USER", "").strip()
POSTGRES_DB = _ENV.get("POSTGRES_DB", "").strip()
POSTGRES_CONNECTION_URL = _build_postgres_connection_url(_ENV)
POSTGRES_SCHEMA = _ENV.get("POSTGRES_SCHEMA", "public").strip() or "public"
PRODUCT_MASTERS_COPY = _require_env(_ENV, "PRODUCT_MASTERS_COPY")
PRODUCT_MASTER_SHEET_NAME = _require_env(_ENV, "PRODUCT_MASTER_SHEET_NAME")


def _excel_col_to_index(col: str) -> int:
    index = 0
    for ch in col.upper():
        index = index * 26 + (ord(ch) - ord("A") + 1)
    return index - 1


FLOAT_QUANTIZE = Decimal("0.01")


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        if math.isnan(value):
            raise ValueError("nan")
        return Decimal(format(value, ".10f"))
    text = str(value).strip()
    if not text:
        raise ValueError("empty")
    return Decimal(text)


def _round_half_up_2(value: Any) -> Decimal:
    """小数点以下2桁で四捨五入する。"""
    return _to_decimal(value).quantize(FLOAT_QUANTIZE, rounding=ROUND_HALF_UP)


def _insert_placeholder(col: ColumnDef) -> sql.SQL:
    if col.pg_type == "float":
        return sql.SQL("{}::numeric(15, 2)").format(sql.Placeholder())
    return sql.Placeholder()


def _normalize_rows(raw: Any) -> list[list[Any]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        return [[raw]]
    if raw and not isinstance(raw[0], list):
        return [raw]
    return raw


def _cell_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def _coerce_value(value: Any, col: ColumnDef) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    if col.pg_type == "varchar":
        text = _cell_str(value)
        if not text:
            return None
        if col.varchar_len is not None and len(text) > col.varchar_len:
            text = text[: col.varchar_len]
        return text
    if col.pg_type == "float":
        try:
            return format(_round_half_up_2(value), "f")
        except (InvalidOperation, TypeError, ValueError):
            return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


@contextmanager
def _db_connection() -> Iterator[psycopg.Connection]:
    url = (POSTGRES_CONNECTION_URL or "").strip()
    if not url:
        raise ValueError(
            "PostgreSQL 接続設定がありません。"
            "config.env に POSTGRES_HOST / POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB を設定してください。"
        )
    conn = psycopg.connect(url)
    if POSTGRES_SCHEMA and POSTGRES_SCHEMA != "public":
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(POSTGRES_SCHEMA))
            )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def drop_and_create_table(conn: psycopg.Connection, schema: str) -> None:
    cur = conn.cursor()
    cur.execute(
        sql.SQL("DROP TABLE IF EXISTS {}.{}").format(
            sql.Identifier(schema),
            sql.Identifier(TABLE_NAME),
        )
    )
    logging.info("%s: テーブルを削除しました。", TABLE_NAME)
    column_parts: list[sql.Composed] = []
    pk_cols: list[str] = []
    for col in COLUMN_DEFS:
        part = sql.SQL("{} {}").format(sql.Identifier(col.pg_col), _pg_type_sql(col))
        column_parts.append(part)
        if col.primary_key:
            pk_cols.append(col.pg_col)
    if pk_cols:
        column_parts.append(
            sql.SQL("PRIMARY KEY ({})").format(
                sql.SQL(", ").join(sql.Identifier(c) for c in pk_cols)
            )
        )
    cur.execute(
        sql.SQL("CREATE TABLE {}.{} ({})").format(
            sql.Identifier(schema),
            sql.Identifier(TABLE_NAME),
            sql.SQL(", ").join(column_parts),
        )
    )
    logging.info("%s: テーブルを作成しました。", TABLE_NAME)


def truncate_table(conn: psycopg.Connection, schema: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("TRUNCATE TABLE {}.{} RESTART IDENTITY").format(
                sql.Identifier(schema),
                sql.Identifier(TABLE_NAME),
            )
        )
    logging.info("%s: テーブルを TRUNCATE しました。", TABLE_NAME)


def read_excel_records() -> list[tuple[Any, ...]]:
    source_path = PRODUCT_MASTERS_COPY.strip()
    sheet_name = PRODUCT_MASTER_SHEET_NAME.strip()

    if not os.path.isfile(source_path):
        raise FileNotFoundError(f"製品マスター Excel が見つかりません: {source_path}")

    base_name = os.path.basename(source_path)
    name, ext = os.path.splitext(base_name)
    local_path = os.path.join(_SCRIPT_DIR_STR, f"{name}_update_copy{ext}")

    logging.info("コピー元: %s", source_path)
    shutil.copy2(source_path, local_path)
    logging.info("コピー先: %s", local_path)

    xw_app: xw.App | None = None
    xw_book: xw.Book | None = None
    header_row: list[Any] = []
    data_rows: list[list[Any]] = []
    try:
        xw_app = xw.App(visible=False, add_book=False)
        xw_app.display_alerts = False
        xw_app.screen_updating = False
        xw_book = xw_app.books.open(local_path, update_links=False, read_only=True)

        sheet_names = [s.name for s in xw_book.sheets]
        if sheet_name not in sheet_names:
            raise ValueError(
                f"シート {sheet_name!r} が見つかりません: {local_path}\n"
                f"利用可能: {', '.join(sheet_names)}"
            )
        ws = xw_book.sheets[sheet_name]

        last_used_row = int(ws.range(LAST_ROW_ANCHOR).end("up").row)
        first_cell = ws.range("A1").value
        if not (last_used_row == 1 and (first_cell is None or _cell_str(first_cell) == "")):
            header_raw = ws.range(f"A1:{DATA_END_COL}1").value
            header_row = _normalize_rows(header_raw)[0] if header_raw else []
            if last_used_row >= DATA_START_ROW:
                data_raw = ws.range(f"A{DATA_START_ROW}:{DATA_END_COL}{last_used_row}").value
                data_rows = _normalize_rows(data_raw)
    finally:
        if xw_book is not None:
            try:
                xw_book.close()
            except Exception:
                pass
        if xw_app is not None:
            try:
                xw_app.quit()
            except Exception:
                pass

    for col in COLUMN_DEFS:
        idx = _excel_col_to_index(col.excel_col)
        if idx >= len(header_row):
            logging.warning(
                "%s 列: ヘッダ行に列が存在しません（期待: %r）",
                col.excel_col,
                col.header_name,
            )
        elif header_row[idx] != col.header_name:
            logging.warning(
                "%s 列: ヘッダ不一致 (期待: %r, 実際: %r)",
                col.excel_col,
                col.header_name,
                header_row[idx],
            )

    col_indices = [_excel_col_to_index(col.excel_col) for col in COLUMN_DEFS]
    pk_index = next(i for i, col in enumerate(COLUMN_DEFS) if col.primary_key)
    records: list[tuple[Any, ...]] = []
    for row in data_rows:
        if not row:
            continue
        values: list[Any] = []
        for col_idx, col_def in zip(col_indices, COLUMN_DEFS):
            raw = row[col_idx] if col_idx < len(row) else None
            values.append(_coerce_value(raw, col_def))
        if values[pk_index] is None:
            continue
        records.append(tuple(values))

    logging.info("Excel 読込: %s 行 -> 投入対象 %s 行", len(data_rows), len(records))
    return records


def insert_records(conn: psycopg.Connection, schema: str, records: list[tuple[Any, ...]]) -> int:
    if not records:
        return 0
    cur = conn.cursor()
    pg_cols = [col.pg_col for col in COLUMN_DEFS]
    insert_sql = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
        sql.Identifier(schema),
        sql.Identifier(TABLE_NAME),
        sql.SQL(", ").join(sql.Identifier(c) for c in pg_cols),
        sql.SQL(", ").join(_insert_placeholder(col) for col in COLUMN_DEFS),
    )
    cur.executemany(insert_sql, records)
    return len(records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_refresh_mode_arguments(parser)
    args = parser.parse_args()
    setup_migration_logging(ERROR_LOG_FILE)
    refresh_mode = resolve_refresh_mode(args)
    schema = POSTGRES_SCHEMA or "public"

    if refresh_mode == RefreshMode.DROP_DATABASE:
        drop_database(POSTGRES_CONNECTION_URL)

    records = read_excel_records()

    with _db_connection() as conn:
        if refresh_mode in (RefreshMode.DROP_DATABASE, RefreshMode.DROP_TABLE):
            drop_and_create_table(conn, schema)
        elif refresh_mode == RefreshMode.TRUNCATE:
            truncate_table(conn, schema)
        count = insert_records(conn, schema, records)

    logging.info(
        "PostgreSQL: %s@%s:%s/%s schema=%s",
        POSTGRES_USER,
        POSTGRES_HOST,
        POSTGRES_PORT,
        POSTGRES_DB,
        schema,
    )
    logging.info("%s: %s 行を投入しました。", TABLE_NAME, count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
