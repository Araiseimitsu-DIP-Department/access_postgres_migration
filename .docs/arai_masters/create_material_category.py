"""material_category テーブルの作成とデータ投入。"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
_MIGRATION_ROOT = _SCRIPT_DIR.parents[1]
_SRC = _MIGRATION_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from access_migration.migration_common import (  # noqa: E402
    RefreshMode,
    add_refresh_mode_arguments,
    drop_database,
    resolve_refresh_mode,
    setup_migration_logging,
)
from arai_masters_common import (  # noqa: E402
    ERROR_LOG_FILE,
    ColumnDef,
    apply_table_refresh,
    build_records,
    copy_excel_locally,
    db_connection,
    insert_records,
    load_settings,
    read_sheet_rows,
)

TABLE_NAME = "material_category"
SHEET_NAME = "材料識別"
DATA_END_COL = "J"
DEFAULT_CATEGORY_NO = 99
DEFAULT_CATEGORY_NAME = "マスタ未登録"

COLUMN_DEFS: tuple[ColumnDef, ...] = (
    ColumnDef("J", "", "category_no", "int", primary_key=True),
    ColumnDef("I", "", "category_name", "varchar", 10),
)


def run(refresh_mode: RefreshMode, *, skip_database_drop: bool = False) -> int:
    settings = load_settings()
    schema = settings["POSTGRES_SCHEMA"]
    connection_url = settings["POSTGRES_CONNECTION_URL"]

    table_mode = (
        RefreshMode.DROP_TABLE if refresh_mode == RefreshMode.DROP_DATABASE else refresh_mode
    )
    if refresh_mode == RefreshMode.DROP_DATABASE and not skip_database_drop:
        drop_database(connection_url)

    with db_connection(connection_url, schema) as conn:
        apply_table_refresh(conn, schema, TABLE_NAME, COLUMN_DEFS, table_mode)

    local_path = copy_excel_locally(settings["PRODUCT_MASTERS_COPY"])
    _, data_rows = read_sheet_rows(
        local_path,
        SHEET_NAME,
        DATA_END_COL,
        last_row_anchor="J65536",
    )
    records = build_records(data_rows, COLUMN_DEFS)

    deduped: dict[int, tuple[Any, ...]] = {}
    for record in records:
        deduped[int(record[0])] = record
    deduped.setdefault(DEFAULT_CATEGORY_NO, (DEFAULT_CATEGORY_NO, DEFAULT_CATEGORY_NAME))
    final_records = [deduped[key] for key in sorted(deduped)]

    logging.info("Excel 読込: %s 行 -> 投入対象 %s 行", len(data_rows), len(final_records))

    with db_connection(connection_url, schema) as conn:
        count = insert_records(conn, schema, TABLE_NAME, COLUMN_DEFS, final_records)

    logging.info(
        "PostgreSQL: %s@%s:%s/%s schema=%s",
        settings.get("POSTGRES_USER", ""),
        settings.get("POSTGRES_HOST", ""),
        settings.get("POSTGRES_PORT", "5432"),
        settings.get("POSTGRES_DB", ""),
        schema,
    )
    logging.info("%s: %s 行を投入しました。", TABLE_NAME, count)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_refresh_mode_arguments(parser)
    args = parser.parse_args()
    setup_migration_logging(ERROR_LOG_FILE)
    return run(resolve_refresh_mode(args))


if __name__ == "__main__":
    raise SystemExit(main())
