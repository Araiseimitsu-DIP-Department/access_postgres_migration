#!/usr/bin/env python3
"""
加工進行表DB.accdb の 3 テーブルを English スキーマの PostgreSQL へ複製する。

このファイルは .docs/production_progress 専用です。

移行対象:
  - t_加工進行表   → progress_entries
  - t_予約         → reservations
  - t_予約Backup   → reservations_backup

前提:
  - 移行先: `.docs/production_progress/.env` の `PRODUCTION_PROGRESS_DB` /
      `PRODUCTION_PROGRESS_PG_DSN`、または環境変数・既定 DSN
  - 移行元: 環境変数 PRODUCTION_PROGRESS_ACCESS_DB（省略時は既定 UNC）
  - 更新モード（いずれか1つ必須）: --drop-database / --drop-table / --truncate

テーブル有無判定は ODBC の catalogs を使わず、実際に SELECT できるかで判断する。
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

import psycopg2
import pyodbc

import sys

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from access_migration.migration_common import (  # noqa: E402
    RefreshMode,
    add_refresh_mode_arguments,
    resolve_refresh_mode,
    run_pre_migration_refresh,
    setup_migration_logging,
)
from migrate_support.access_connection import (  # noqa: E402
    DEFAULT_ACCESS_DB_UNC,
    DEFAULT_PG_DSN,
    build_conn_str,
    load_project_dotenv,
    normalize_db_path_for_odbc,
)
from migrate_support.access_to_pg_maps import (
    progress_tuple_from_access_row,
    reservation_tuple_from_access_row,
    row_dict_from_access_cursor,
)

logger = logging.getLogger(__name__)

PG_TABLE_PROGRESS = "progress_entries"
PG_TABLE_RESERVE = "reservations"
PG_TABLE_RESERVE_BACKUP = "reservations_backup"

_PG_TABLES = (
    PG_TABLE_PROGRESS,
    PG_TABLE_RESERVE,
    PG_TABLE_RESERVE_BACKUP,
)

_ENV_PG = "PRODUCTION_PROGRESS_DB"
_ENV_PG_DSN = "PRODUCTION_PROGRESS_PG_DSN"
_ENV_ACCESS = "PRODUCTION_PROGRESS_ACCESS_DB"
_SCHEMA_SQL_FILE = _SCRIPT_DIR / "schema_pg_english_v1.sql"
_ERROR_LOG_FILE = _SCRIPT_DIR / "migration_error_production_progress.log"

AF_PROGRESS = "[t_加工進行表]"
AF_RESERVE = "[t_予約]"
AF_RESERVE_BK = "[t_予約Backup]"
ALT_PROGRESS = "t_加工進行表"
ALT_RESERVE = "t_予約"
ALT_RESERVE_BK = "t_予約Backup"


def resolve_access_from(
    acc: pyodbc.Connection, candidates: tuple[str, ...]
) -> tuple[str, int] | tuple[None, None]:
    """最初に COUNT(*) が通った FROM 断片と件数。"""
    for clause in candidates:
        n = access_count(acc, clause)
        if n is not None:
            logger.debug("Access FROM clause: %s", clause)
            return clause, n
    return None, None


def _configure_logging(verbose: bool) -> None:
    setup_migration_logging(_ERROR_LOG_FILE, verbose=verbose)


def load_production_progress_dotenv() -> None:
    """production_progress フォルダ内 .env を読み込む（既存の環境変数は上書きしない）。"""
    env_path = _SCRIPT_DIR / ".env"
    if env_path.is_file():
        text = env_path.read_text(encoding="utf-8")
        for key, value in _parse_dotenv_lines(text):
            if key not in os.environ:
                os.environ[key] = value
    load_project_dotenv(_PROJECT_ROOT)


def _parse_dotenv_lines(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        pairs.append((key, value))
    return pairs


def connect_access(accdb_path: str) -> pyodbc.Connection:
    normalized = normalize_db_path_for_odbc(accdb_path)
    return pyodbc.connect(build_conn_str(normalized), autocommit=True)


def access_count(acc: pyodbc.Connection, from_clause: str) -> int | None:
    """SELECT COUNT(*) が成功すれば件数、失敗（テーブルなし等）なら None。"""
    try:
        cur = acc.execute(f"SELECT COUNT(*) FROM {from_clause}")
        row = cur.fetchone()
        return int(row[0]) if row else 0
    except pyodbc.Error as e:
        logger.debug("COUNT 失敗 (%s): %s", from_clause, e)
        return None


def pg_count(cur, table: str) -> int:
    if table not in _PG_TABLES:
        raise ValueError(f"invalid table: {table}")
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    row = cur.fetchone()
    return int(row[0]) if row else 0


def apply_pg_schema(pg, sql_path: Path) -> None:
    if not sql_path.is_file():
        logger.error("スキーマ SQL が見つかりません: %s", sql_path)
        raise SystemExit(2)
    sql_text = sql_path.read_text(encoding="utf-8")
    with pg.cursor() as cur:
        cur.execute(sql_text)
    pg.commit()
    logger.info("PostgreSQL スキーマを適用しました: %s", sql_path.name)


def truncate_pg_targets(pg) -> None:
    with pg.cursor() as cur:
        cur.execute(
            "TRUNCATE TABLE "
            f"{PG_TABLE_RESERVE_BACKUP}, {PG_TABLE_RESERVE}, {PG_TABLE_PROGRESS} "
            "RESTART IDENTITY"
        )
    pg.commit()
    logger.info(
        "PostgreSQL: %s を TRUNCATE (RESTART IDENTITY) しました",
        ", ".join(_PG_TABLES),
    )


def sync_id_sequence(pg, table: str) -> None:
    if table not in _PG_TABLES:
        raise ValueError(table)
    with pg.cursor() as cur:
        cur.execute(
            f"""
            SELECT setval(
                pg_get_serial_sequence('{table}', 'id'),
                GREATEST(
                    COALESCE((SELECT MAX(id) FROM {table}), 1)::bigint,
                    1
                ),
                TRUE
            )
            """
        )


def migrate_progress(
    acc: pyodbc.Connection,
    pg,
    dry_run: bool,
) -> int:
    fc, n = resolve_access_from(acc, (AF_PROGRESS, ALT_PROGRESS))
    if fc is None:
        logger.error(
            "加工進行表を読めません（%s / %s）。中止します。",
            AF_PROGRESS,
            ALT_PROGRESS,
        )
        raise SystemExit(1)

    if dry_run:
        logger.info("%s → %s: %s rows (dry-run)", fc, PG_TABLE_PROGRESS, n)
        return n

    try:
        cursor = acc.execute(f"SELECT * FROM {fc}")
    except pyodbc.Error as e:
        logger.error("加工進行表の SELECT に失敗: %s", e)
        raise SystemExit(1) from e

    sql_ins = (
        f"INSERT INTO {PG_TABLE_PROGRESS} ("
        "id, machine_no, machine_sort, serial_number, "
        "production_date, setup_date, customer, part_no, part_name, "
        "planned_qty, due_date, material, shipment_date, material_lot, "
        "daily_output_qty, shipment_qty, trouble_target_qty, trouble_shipment_qty, "
        "trouble_note, change_point, remarks"
        ") VALUES ("
        "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
        "%s, %s, %s, %s, %s, %s, %s"
        ")"
    )

    rows_out: list[tuple] = []
    skipped_id = 0
    desc = cursor.description
    assert desc is not None
    for row in cursor:
        rd = row_dict_from_access_cursor(desc, row)
        tup = progress_tuple_from_access_row(rd)
        if tup[0] is None:
            skipped_id += 1
            continue
        rows_out.append(tup)

    if skipped_id:
        logger.warning("progress_entries: skipped %s rows (missing ID)", skipped_id)

    logger.info("%s → %s: %s rows", fc, PG_TABLE_PROGRESS, len(rows_out))
    if not rows_out:
        return 0
    assert pg is not None
    batch = 2000
    with pg.cursor() as cur:
        for i in range(0, len(rows_out), batch):
            cur.executemany(sql_ins, rows_out[i : i + batch])
    sync_id_sequence(pg, PG_TABLE_PROGRESS)
    pg.commit()
    return len(rows_out)


def _migrate_reservations_like(
    acc: pyodbc.Connection,
    pg,
    candidates: tuple[str, ...],
    pg_table: str,
    dry_run: bool,
) -> int:
    fc, n = resolve_access_from(acc, candidates)
    if fc is None:
        logger.warning("reservations unreadable: %s", " / ".join(candidates))
        return 0

    if dry_run:
        logger.info("%s → %s: %s rows (dry-run)", fc, pg_table, n)
        return n

    try:
        cursor = acc.execute(f"SELECT * FROM {fc}")
    except pyodbc.Error as e:
        logger.warning("reservations SELECT failed (skip) %s — %s", fc, e)
        return 0

    sql_ins = (
        f"INSERT INTO {pg_table} ("
        "id, shipment_date, machine_no, material_lot, change_point, remarks, "
        "trouble, shipment_qty"
        ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )

    rows_out: list[tuple] = []
    skipped = 0
    desc = cursor.description
    assert desc is not None
    for row in cursor:
        rd = row_dict_from_access_cursor(desc, row)
        tup = reservation_tuple_from_access_row(rd)
        if tup is None or tup[0] is None:
            skipped += 1
            continue
        rows_out.append(tup)

    if skipped:
        logger.warning(
            "%s: skipped %s rows (need id, shipment_date, machine_no)",
            fc,
            skipped,
        )

    logger.info("%s → %s: %s rows", fc, pg_table, len(rows_out))
    if not rows_out:
        return 0
    assert pg is not None
    with pg.cursor() as cur:
        cur.executemany(sql_ins, rows_out)
    sync_id_sequence(pg, pg_table)
    pg.commit()
    return len(rows_out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--access-path",
        help="加工進行表 .accdb（PRODUCTION_PROGRESS_ACCESS_DB / 既定 UNC）",
    )
    add_refresh_mode_arguments(parser)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Access の件数集計のみ（PostgreSQL へは書かない）",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="DEBUG ログ")
    args = parser.parse_args()
    _configure_logging(args.verbose)

    load_production_progress_dotenv()
    refresh_mode = resolve_refresh_mode(args)

    dsn = (
        os.environ.get(_ENV_PG, "").strip()
        or os.environ.get(_ENV_PG_DSN, "").strip()
        or DEFAULT_PG_DSN
    )
    if not dsn.startswith("postgresql://") and not dsn.startswith("postgres://"):
        logger.error(
            "%s に postgresql:// 形式の URI を設定してください。"
            "Access パスは %s で指定します。",
            _ENV_PG,
            _ENV_ACCESS,
        )
        raise SystemExit(2)

    acc_path = (
        args.access_path
        or os.environ.get(_ENV_ACCESS, "").strip().strip('"')
        or DEFAULT_ACCESS_DB_UNC
    )

    logger.info("Access DB: %s", acc_path)
    logger.info(
        "PostgreSQL target: …@%s (password not logged)",
        dsn.split("@", 1)[-1],
    )

    try:
        acc = connect_access(acc_path)
    except Exception as e:
        logger.error("Access に接続できません: %s", e)
        raise SystemExit(1) from e

    pg: object | None
    if args.dry_run:
        pg = None
    else:
        if refresh_mode in (RefreshMode.DROP_DATABASE, RefreshMode.DROP_TABLE):
            run_pre_migration_refresh(dsn, refresh_mode, table_names=list(_PG_TABLES))
        try:
            pg = psycopg2.connect(dsn)
            pg.autocommit = False
        except Exception as e:
            logger.error("PostgreSQL 接続に失敗しました: %s", e)
            acc.close()
            raise SystemExit(1) from e

    try:
        if not args.dry_run:
            assert pg is not None
            if refresh_mode in (RefreshMode.DROP_DATABASE, RefreshMode.DROP_TABLE):
                apply_pg_schema(pg, _SCHEMA_SQL_FILE)
            elif refresh_mode == RefreshMode.TRUNCATE:
                truncate_pg_targets(pg)

        migrate_progress(acc, pg, args.dry_run)
        _migrate_reservations_like(
            acc, pg, (AF_RESERVE, ALT_RESERVE), PG_TABLE_RESERVE, args.dry_run
        )
        _migrate_reservations_like(
            acc,
            pg,
            (AF_RESERVE_BK, ALT_RESERVE_BK),
            PG_TABLE_RESERVE_BACKUP,
            args.dry_run,
        )
    finally:
        acc.close()
        if pg is not None:
            pg.close()

    logger.info("done")


if __name__ == "__main__":
    main()
