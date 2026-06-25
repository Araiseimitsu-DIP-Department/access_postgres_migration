"""arai_masters 投入スクリプト共通処理。"""
from __future__ import annotations

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

from access_migration.migration_common import RefreshMode  # noqa: E402

PgType = Literal["varchar", "float", "int"]
DATA_START_ROW = 2
LAST_ROW_ANCHOR = "A65536"
FLOAT_QUANTIZE = Decimal("0.01")
ERROR_LOG_FILE = _SCRIPT_DIR / "migration_error_arai_masters.log"


@dataclass(frozen=True)
class ColumnDef:
    excel_col: str
    header_name: str
    pg_col: str
    pg_type: PgType
    varchar_len: int | None = None
    primary_key: bool = False
    unique: bool = False


def config_env_path() -> Path:
    override = os.environ.get("UPDATE_MASTERS_CONFIG_ENV", "").strip()
    if override:
        return Path(override)
    return _SCRIPT_DIR.parent / "config.env"


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise FileNotFoundError(
            f"設定ファイルが見つかりません: {path}\n"
            "config.env を配置するか、UPDATE_MASTERS_CONFIG_ENV でパスを指定してください。"
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


def require_env(env: dict[str, str], key: str) -> str:
    value = env.get(key, "").strip()
    if not value:
        raise ValueError(f"設定ファイルに {key} が設定されていません。")
    return value


def build_postgres_connection_url(env: dict[str, str]) -> str:
    direct = env.get("POSTGRES_CONNECTION_URL", "").strip()
    if direct:
        return direct
    host = require_env(env, "POSTGRES_HOST")
    port = env.get("POSTGRES_PORT", "5432").strip() or "5432"
    user = require_env(env, "POSTGRES_USER")
    password = require_env(env, "POSTGRES_PASSWORD")
    database = require_env(env, "POSTGRES_DB")
    return (
        f"postgresql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{quote_plus(database)}"
    )


def load_settings() -> dict[str, str]:
    env = parse_env_file(config_env_path())
    env["POSTGRES_CONNECTION_URL"] = build_postgres_connection_url(env)
    env["POSTGRES_SCHEMA"] = env.get("POSTGRES_SCHEMA", "public").strip() or "public"
    env["PRODUCT_MASTERS_COPY"] = require_env(env, "PRODUCT_MASTERS_COPY")
    return env


def excel_col_to_index(col: str) -> int:
    index = 0
    for ch in col.upper():
        index = index * 26 + (ord(ch) - ord("A") + 1)
    return index - 1


def to_decimal(value: Any) -> Decimal:
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


def round_half_up_2(value: Any) -> Decimal:
    return to_decimal(value).quantize(FLOAT_QUANTIZE, rounding=ROUND_HALF_UP)


def insert_placeholder(col: ColumnDef) -> sql.SQL:
    if col.pg_type == "float":
        return sql.SQL("{}::numeric(15, 2)").format(sql.Placeholder())
    return sql.Placeholder()


def normalize_rows(raw: Any) -> list[list[Any]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        return [[raw]]
    if raw and not isinstance(raw[0], list):
        return [raw]
    return raw


def cell_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def coerce_value(value: Any, col: ColumnDef) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    if col.pg_type == "varchar":
        text = cell_str(value)
        if not text:
            return None
        if col.varchar_len is not None and len(text) > col.varchar_len:
            text = text[: col.varchar_len]
        return text
    if col.pg_type == "float":
        try:
            return format(round_half_up_2(value), "f")
        except (InvalidOperation, TypeError, ValueError):
            return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def pg_type_sql(col: ColumnDef) -> sql.SQL:
    if col.pg_type == "varchar":
        return sql.SQL("VARCHAR({})").format(sql.Literal(col.varchar_len))
    if col.pg_type == "float":
        return sql.SQL("NUMERIC(15, 2)")
    return sql.SQL("INTEGER")


@contextmanager
def db_connection(connection_url: str, schema: str) -> Iterator[psycopg.Connection]:
    if not connection_url.strip():
        raise ValueError("PostgreSQL 接続設定がありません。")
    conn = psycopg.connect(connection_url)
    if schema and schema != "public":
        with conn.cursor() as cur:
            cur.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def copy_excel_locally(source_path: str) -> str:
    if not os.path.isfile(source_path):
        raise FileNotFoundError(f"製品マスター Excel が見つかりません: {source_path}")
    base_name = os.path.basename(source_path)
    name, ext = os.path.splitext(base_name)
    local_path = str(_SCRIPT_DIR / f"{name}_update_copy{ext}")
    logging.info("コピー元: %s", source_path)
    shutil.copy2(source_path, local_path)
    logging.info("コピー先: %s", local_path)
    return local_path


def read_sheet_rows(
    local_path: str,
    sheet_name: str,
    data_end_col: str,
    header_defs: tuple[ColumnDef, ...] | None = None,
    last_row_anchor: str = LAST_ROW_ANCHOR,
) -> tuple[list[Any], list[list[Any]]]:
    xw_app: xw.App | None = None
    xw_book: xw.Book | None = None
    header_row: list[Any] = []
    data_rows: list[list[Any]] = []
    try:
        xw_app = xw.App(visible=False, add_book=False)
        xw_app.display_alerts = False
        xw_app.screen_updating = False
        xw_book = xw_app.books.open(local_path, update_links=False, read_only=True)
        sheet_names = [sheet.name for sheet in xw_book.sheets]
        if sheet_name not in sheet_names:
            raise ValueError(
                f"シート {sheet_name!r} が見つかりません: {local_path}\n"
                f"利用可能: {', '.join(sheet_names)}"
            )
        ws = xw_book.sheets[sheet_name]
        last_used_row = int(ws.range(last_row_anchor).end("up").row)
        first_cell = ws.range("A1").value
        if not (last_used_row == 1 and (first_cell is None or cell_str(first_cell) == "")):
            header_raw = ws.range(f"A1:{data_end_col}1").value
            header_row = normalize_rows(header_raw)[0] if header_raw else []
            if last_used_row >= DATA_START_ROW:
                data_raw = ws.range(f"A{DATA_START_ROW}:{data_end_col}{last_used_row}").value
                data_rows = normalize_rows(data_raw)
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

    if header_defs:
        for col in header_defs:
            if not col.header_name:
                continue
            idx = excel_col_to_index(col.excel_col)
            if idx >= len(header_row):
                logging.warning("%s 列: ヘッダ行に列が存在しません（期待: %r）", col.excel_col, col.header_name)
            elif header_row[idx] != col.header_name:
                logging.warning(
                    "%s 列: ヘッダ不一致 (期待: %r, 実際: %r)",
                    col.excel_col,
                    col.header_name,
                    header_row[idx],
                )
    return header_row, data_rows


def build_records(data_rows: list[list[Any]], column_defs: tuple[ColumnDef, ...]) -> list[tuple[Any, ...]]:
    col_indices = [excel_col_to_index(col.excel_col) for col in column_defs]
    pk_indices = [index for index, col in enumerate(column_defs) if col.primary_key]
    records: list[tuple[Any, ...]] = []
    for row in data_rows:
        if not row:
            continue
        values: list[Any] = []
        for col_idx, col_def in zip(col_indices, column_defs):
            raw = row[col_idx] if col_idx < len(row) else None
            values.append(coerce_value(raw, col_def))
        if pk_indices and values[pk_indices[0]] is None:
            continue
        records.append(tuple(values))
    return records


def recreate_table(
    conn: psycopg.Connection,
    schema: str,
    table_name: str,
    column_defs: tuple[ColumnDef, ...],
) -> None:
    cur = conn.cursor()
    cur.execute(
        sql.SQL("DROP TABLE IF EXISTS {}.{}").format(
            sql.Identifier(schema),
            sql.Identifier(table_name),
        )
    )
    logging.info("%s: テーブルを削除しました。", table_name)
    column_parts: list[sql.Composed] = []
    pk_cols = [col.pg_col for col in column_defs if col.primary_key]
    for col in column_defs:
        column_parts.append(
            sql.SQL("{} {}").format(sql.Identifier(col.pg_col), pg_type_sql(col))
        )
    if pk_cols:
        column_parts.append(
            sql.SQL("PRIMARY KEY ({})").format(
                sql.SQL(", ").join(sql.Identifier(name) for name in pk_cols)
            )
        )
    for col in column_defs:
        if col.unique and not col.primary_key:
            column_parts.append(
                sql.SQL("UNIQUE ({})").format(sql.Identifier(col.pg_col))
            )
    cur.execute(
        sql.SQL("CREATE TABLE {}.{} ({})").format(
            sql.Identifier(schema),
            sql.Identifier(table_name),
            sql.SQL(", ").join(column_parts),
        )
    )
    logging.info("%s: テーブルを作成しました。", table_name)


def truncate_table(conn: psycopg.Connection, schema: str, table_name: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("TRUNCATE TABLE {}.{} RESTART IDENTITY").format(
                sql.Identifier(schema),
                sql.Identifier(table_name),
            )
        )
    logging.info("%s: テーブルを TRUNCATE しました。", table_name)


def apply_table_refresh(
    conn: psycopg.Connection,
    schema: str,
    table_name: str,
    column_defs: tuple[ColumnDef, ...],
    refresh_mode: RefreshMode,
) -> None:
    if refresh_mode in (RefreshMode.DROP_DATABASE, RefreshMode.DROP_TABLE):
        recreate_table(conn, schema, table_name, column_defs)
    elif refresh_mode == RefreshMode.TRUNCATE:
        truncate_table(conn, schema, table_name)
    else:
        raise ValueError(f"未対応の更新モード: {refresh_mode}")


def insert_records(
    conn: psycopg.Connection,
    schema: str,
    table_name: str,
    column_defs: tuple[ColumnDef, ...],
    records: list[tuple[Any, ...]],
) -> int:
    if not records:
        return 0
    pg_cols = [col.pg_col for col in column_defs]
    insert_sql = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
        sql.Identifier(schema),
        sql.Identifier(table_name),
        sql.SQL(", ").join(sql.Identifier(name) for name in pg_cols),
        sql.SQL(", ").join(insert_placeholder(col) for col in column_defs),
    )
    with conn.cursor() as cur:
        cur.executemany(insert_sql, records)
    return len(records)
