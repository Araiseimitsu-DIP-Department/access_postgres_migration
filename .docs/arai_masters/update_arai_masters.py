"""arai_masters の4テーブルを製品マスター.xls から一括更新する。

設定: UPDATE_MASTERS_CONFIG_ENV または .docs/config.env / db_all_recreate 生成 env
更新モード: --drop-database / --drop-table / --truncate
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

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
from arai_masters_common import ERROR_LOG_FILE, load_settings  # noqa: E402
from create_machine_master import run as run_machine_master  # noqa: E402
from create_material_category import run as run_material_category  # noqa: E402
from create_outsource_master import run as run_outsource_master  # noqa: E402
from create_product_master import run as run_product_master  # noqa: E402

TABLE_RUNNERS = (
    ("material_category", run_material_category),
    ("outsource_master", run_outsource_master),
    ("machine_master", run_machine_master),
)


def run_product_master_with_mode(refresh_mode: RefreshMode) -> int:
    return run_product_master(refresh_mode, skip_database_drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_refresh_mode_arguments(parser)
    args = parser.parse_args()
    setup_migration_logging(ERROR_LOG_FILE)
    refresh_mode = resolve_refresh_mode(args)

    settings = load_settings()
    if refresh_mode == RefreshMode.DROP_DATABASE:
        drop_database(settings["POSTGRES_CONNECTION_URL"])

    failures = 0
    for table_name, runner in TABLE_RUNNERS:
        logging.info("=== 開始: %s ===", table_name)
        try:
            exit_code = runner(refresh_mode, skip_database_drop=True)
        except Exception:
            logging.exception("更新に失敗しました: %s", table_name)
            exit_code = 1
        if exit_code != 0:
            failures += 1
            logging.error("失敗: %s", table_name)
        else:
            logging.info("成功: %s", table_name)

    logging.info("=== 開始: product_master ===")
    try:
        product_exit = run_product_master_with_mode(refresh_mode)
    except Exception:
        logging.exception("更新に失敗しました: product_master")
        product_exit = 1
    if product_exit != 0:
        failures += 1
        logging.error("失敗: product_master")
    else:
        logging.info("成功: product_master")

    if failures:
        logging.error("完了（失敗 %s / 4 件）", failures)
        return 1
    logging.info("arai_masters 全4テーブルの更新が完了しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
