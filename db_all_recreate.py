"""`.docs` 配下の移行スクリプトを一括実行し PostgreSQL を更新する。

全 DB 更新時はプロジェクトルートで本スクリプトを実行し、`db_all_recreate.env` を参照します。
個別更新は各 `.docs/<target>/` 内の移行スクリプトを実行し、同フォルダ内 `.env` を参照します。

更新モード（いずれか1つ必須）:
  --drop-database  PostgreSQL データベースを DROP 後に再作成
  --drop-table     移行対象テーブル（public スキーマ）を DROP 後に再作成（既定）
  --truncate       テーブル構造を維持しデータのみ更新

使用例:
  python db_all_recreate.py --list
  python db_all_recreate.py --dry-run --drop-table
  python db_all_recreate.py --target delivery_label_db --truncate --yes
  python db_all_recreate.py --drop-database --yes
"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus, urlparse

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parent
DOCS_DIR = PROJECT_ROOT / ".docs"
DEFAULT_ENV_FILE = PROJECT_ROOT / "db_all_recreate.env"
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from access_migration.migration_common import (  # noqa: E402
    LOG_FORMAT,
    RefreshMode,
    add_refresh_mode_arguments,
    refresh_mode_to_cli_args,
    resolve_refresh_mode,
)


@dataclass(frozen=True)
class RecreateTarget:
    key: str
    env_prefix: str
    docs_subdir: str
    script_name: str
    uses_access_env: bool = True
    env_kind: str = "dotenv"
    default_db_name: str = ""


TARGETS: tuple[RecreateTarget, ...] = (
    RecreateTarget(
        "arai_masters",
        "ARAI_MASTERS",
        "arai_masters",
        "create_product_master.py",
        env_kind="arai_config",
        uses_access_env=False,
        default_db_name="arai_masters",
    ),
    RecreateTarget(
        "appearance_inspection_db",
        "APPEARANCE_INSPECTION",
        "appearance_inspection_db",
        "migrate_access_to_postgres_appearance_inspection_db.py",
        default_db_name="appearance_inspection_db",
    ),
    RecreateTarget(
        "delivery_label_db",
        "DELIVERY_LABEL",
        "delivery_label_db",
        "migrate_access_to_postgres_delivery_label_db.py",
        default_db_name="delivery_label_db",
    ),
    RecreateTarget(
        "secondary_process_record_db",
        "SECONDARY_PROCESS_RECORD",
        "secondary_process_record_db",
        "migrate_access_to_postgres_secondary_process_record_db.py",
        default_db_name="secondary_process_record_db",
    ),
    RecreateTarget(
        "pingauge_management_db",
        "PINGAUGE_MANAGEMENT",
        "pingauge_management_db",
        "migrate_access_to_postgres_pingauge_management_db.py",
        default_db_name="pingauge_management_db",
    ),
    RecreateTarget(
        "qr_scan_history_db",
        "QR_SCAN_HISTORY",
        "qr_scan_history_db",
        "migrate_access_to_postgres_qr_scan_history_db.py",
        default_db_name="qr_scan_history_db",
    ),
    RecreateTarget(
        "material_millsheet_manager",
        "MATERIAL_MILLSHEET_MANAGER",
        "material_millsheet_manager",
        "migrate_access_to_postgres_material_millsheet_manager_db.py",
        default_db_name="material_millsheet_manager",
    ),
    RecreateTarget(
        "material_scheduling",
        "MATERIAL_SCHEDULING",
        "material_scheduling",
        "migrate_access_to_postgres_material_scheduling_db.py",
        default_db_name="material_scheduling",
    ),
    RecreateTarget(
        "shipping_inspection_db",
        "SHIPPING_INSPECTION",
        "shipping_inspection_db",
        "migrate_access_to_postgres_shipping_inspection_db.py",
        default_db_name="shipping_inspection_db",
    ),
    RecreateTarget(
        "order_performance_db",
        "ORDER_PERFORMANCE",
        "order_performance_db",
        "migrate_access_to_postgres_order_performance_db.py",
        default_db_name="order_performance_db",
    ),
    RecreateTarget(
        "order_management",
        "ORDER_MANAGEMENT",
        "order_management",
        "migrate_access_to_postgres_order_management_db.py",
        default_db_name="order_management",
    ),
    RecreateTarget(
        "subcon_manager",
        "SUBCON_MANAGER",
        "subcon_manager",
        "migrate_access_to_postgres_subcon_manager_db.py",
        default_db_name="subcon_manager",
    ),
    RecreateTarget(
        "purchase_summary_db",
        "PURCHASE_SUMMARY",
        "purchase_summary_db",
        "purchase_summary_migrate.py",
        default_db_name="purchase_summary_db",
    ),
    RecreateTarget(
        "production_progress",
        "PRODUCTION_PROGRESS",
        "production_progress",
        "migrate_access_to_pg.py",
        env_kind="production_progress",
        default_db_name="production_progress",
    ),
)


TARGET_BY_KEY = {target.key: target for target in TARGETS}


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format=LOG_FORMAT)


def load_config(env_path: Path) -> dict[str, str]:
    if not env_path.is_file():
        raise FileNotFoundError(
            f"設定ファイルが見つかりません: {env_path}\n"
            "db_all_recreate.env.example を db_all_recreate.env にコピーして編集してください。"
        )
    return {key: value for key, value in dotenv_values(env_path).items() if value is not None}


def config_value(config: dict[str, str], key: str, default: str = "") -> str:
    return config.get(key, default).strip()


def is_enabled(config: dict[str, str], prefix: str) -> bool:
    raw = config_value(config, f"{prefix}_ENABLED", "true").lower()
    return raw not in {"0", "false", "no", "off"}


def build_database_url(config: dict[str, str], prefix: str, default_db_name: str) -> str:
    direct = config_value(config, f"{prefix}_DATABASE_URL")
    if direct:
        return direct

    db_name = config_value(config, f"{prefix}_DB_NAME", default_db_name)
    if not db_name:
        raise ValueError(f"{prefix}_DATABASE_URL または {prefix}_DB_NAME が必要です。")

    host = config_value(config, f"{prefix}_POSTGRES_HOST") or config_value(config, "POSTGRES_HOST")
    port = config_value(config, f"{prefix}_POSTGRES_PORT") or config_value(config, "POSTGRES_PORT", "5432")
    user = config_value(config, f"{prefix}_POSTGRES_USER") or config_value(config, "POSTGRES_USER")
    password = config_value(config, f"{prefix}_POSTGRES_PASSWORD") or config_value(config, "POSTGRES_PASSWORD")
    missing = [
        name
        for name, value in (
            ("POSTGRES_HOST", host),
            ("POSTGRES_USER", user),
            ("POSTGRES_PASSWORD", password),
        )
        if not value
    ]
    if missing:
        raise ValueError(f"{prefix}: DATABASE_URL 未指定時は共通または個別の {', '.join(missing)} が必要です。")
    return (
        f"postgresql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{quote_plus(db_name)}"
    )


def mask_database_url(database_url: str) -> str:
    parsed = urlparse(database_url)
    if not parsed.hostname:
        return database_url
    user = parsed.username or ""
    host = parsed.hostname
    port = f":{parsed.port}" if parsed.port else ""
    db = parsed.path.lstrip("/")
    return f"postgresql://{user}:***@{host}{port}/{db}"


def write_dotenv_file(path: Path, values: dict[str, str]) -> None:
    lines = [f"{key}={value}" for key, value in values.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logging.info("設定ファイルを書き出しました: %s", path)


def materialize_target_env(target: RecreateTarget, config: dict[str, str]) -> dict[str, str]:
    target_dir = DOCS_DIR / target.docs_subdir
    if not target_dir.is_dir():
        raise FileNotFoundError(f"対象フォルダが見つかりません: {target_dir}")

    script_path = target_dir / target.script_name
    if not script_path.is_file():
        raise FileNotFoundError(f"移行スクリプトが見つかりません: {script_path}")

    extra_env: dict[str, str] = {}

    if target.env_kind == "arai_config":
        host = config_value(config, f"{target.env_prefix}_POSTGRES_HOST") or config_value(config, "POSTGRES_HOST")
        port = config_value(config, f"{target.env_prefix}_POSTGRES_PORT") or config_value(config, "POSTGRES_PORT", "5432")
        user = config_value(config, f"{target.env_prefix}_POSTGRES_USER") or config_value(config, "POSTGRES_USER")
        password = config_value(config, f"{target.env_prefix}_POSTGRES_PASSWORD") or config_value(config, "POSTGRES_PASSWORD")
        postgres_db = config_value(config, f"{target.env_prefix}_POSTGRES_DB", target.default_db_name)
        schema = config_value(config, f"{target.env_prefix}_POSTGRES_SCHEMA", "public")
        product_copy = config_value(config, f"{target.env_prefix}_PRODUCT_MASTERS_COPY")
        sheet_name = config_value(config, f"{target.env_prefix}_PRODUCT_MASTER_SHEET_NAME", "製品マスター")
        if not product_copy:
            raise ValueError(f"{target.env_prefix}_PRODUCT_MASTERS_COPY が未設定です。")

        config_path = PROJECT_ROOT / "db_all_recreate_arai_masters.env"
        write_dotenv_file(
            config_path,
            {
                "POSTGRES_HOST": host,
                "POSTGRES_PORT": port,
                "POSTGRES_USER": user,
                "POSTGRES_PASSWORD": password,
                "POSTGRES_DB": postgres_db,
                "POSTGRES_SCHEMA": schema,
                "PRODUCT_MASTERS_COPY": product_copy,
                "PRODUCT_MASTER_SHEET_NAME": sheet_name,
            },
        )
        extra_env["UPDATE_MASTERS_CONFIG_ENV"] = str(config_path)
        database_url = build_database_url(config, target.env_prefix, target.default_db_name)
        return {"database_url": database_url, "extra_env": extra_env}

    database_url = build_database_url(config, target.env_prefix, target.default_db_name)

    if target.env_kind == "production_progress":
        access_path = config_value(config, f"{target.env_prefix}_ACCESS_DB_PATH")
        if access_path:
            extra_env["PRODUCTION_PROGRESS_ACCESS_DB"] = access_path
        extra_env["PRODUCTION_PROGRESS_DB"] = database_url
        return {"database_url": database_url, "extra_env": extra_env}

    dotenv_values_map = {
        "DATABASE_URL": database_url,
        "LOG_LEVEL": config_value(config, "LOG_LEVEL", "INFO"),
    }
    if target.uses_access_env:
        access_path = config_value(config, f"{target.env_prefix}_ACCESS_DB_PATH")
        if not access_path:
            raise ValueError(f"{target.env_prefix}_ACCESS_DB_PATH が未設定です。")
        dotenv_values_map["ACCESS_DB_PATH"] = access_path

    write_dotenv_file(target_dir / ".env", dotenv_values_map)
    return {"database_url": database_url, "extra_env": extra_env}


def run_target_script(
    target: RecreateTarget,
    extra_env: dict[str, str],
    refresh_mode: RefreshMode,
    dry_run: bool,
) -> int:
    script_path = DOCS_DIR / target.docs_subdir / target.script_name
    command = [sys.executable, str(script_path), *refresh_mode_to_cli_args(refresh_mode)]
    logging.info("実行: %s", " ".join(command))

    if dry_run:
        return 0

    env = os.environ.copy()
    env.update(extra_env)
    completed = subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        env=env,
        check=False,
    )
    if completed.returncode != 0:
        logging.error("失敗 (%s): exit code %s", target.key, completed.returncode)
    else:
        logging.info("成功: %s", target.key)
    return completed.returncode


def recreate_target(
    target: RecreateTarget,
    config: dict[str, str],
    refresh_mode: RefreshMode,
    dry_run: bool,
) -> int:
    prepared = materialize_target_env(target, config)
    extra_env = prepared["extra_env"]
    database_url = prepared["database_url"]

    if dry_run:
        logging.info(
            "[dry-run] %s: %s (%s)",
            refresh_mode.value,
            target.key,
            mask_database_url(database_url),
        )
        return run_target_script(target, extra_env, refresh_mode, dry_run=True)

    return run_target_script(target, extra_env, refresh_mode, dry_run=False)


def confirm_execution(selected: list[RecreateTarget], refresh_mode: RefreshMode) -> bool:
    print(f"以下の PostgreSQL データベースを {refresh_mode.value} モードで更新します。")
    for target in selected:
        print(f"  - {target.key} ({target.script_name})")
    answer = input("続行しますか？ [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="`.docs` 内の移行スクリプトで PostgreSQL を一括更新")
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help="設定ファイル（既定: db_all_recreate.env）",
    )
    parser.add_argument(
        "--target",
        action="append",
        dest="targets",
        metavar="KEY",
        help="実行対象（省略時は ENABLED=true の全対象）",
    )
    parser.add_argument("--list", action="store_true", help="対象一覧を表示")
    parser.add_argument("--dry-run", action="store_true", help="実行コマンドのみ表示")
    parser.add_argument("--yes", action="store_true", help="確認プロンプトを省略")
    parser.add_argument("--verbose", "-v", action="store_true", help="DEBUG ログ")
    add_refresh_mode_arguments(parser, required=False)
    return parser.parse_args()


def resolve_refresh_mode_or_default(args: argparse.Namespace) -> RefreshMode:
    if args.drop_database or args.drop_table or args.truncate:
        return resolve_refresh_mode(args)
    return RefreshMode.DROP_TABLE


def select_targets(config: dict[str, str], requested: list[str] | None) -> list[RecreateTarget]:
    if requested:
        selected: list[RecreateTarget] = []
        for key in requested:
            if key not in TARGET_BY_KEY:
                known = ", ".join(sorted(TARGET_BY_KEY))
                raise ValueError(f"未知の target: {key}（指定可能: {known}）")
            selected.append(TARGET_BY_KEY[key])
        return selected

    return [target for target in TARGETS if is_enabled(config, target.env_prefix)]


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)

    if args.list:
        for target in TARGETS:
            print(f"{target.key}\t{target.docs_subdir}/{target.script_name}")
        return 0

    refresh_mode = resolve_refresh_mode_or_default(args)
    config = load_config(args.env_file)
    selected = select_targets(config, args.targets)
    if not selected:
        logging.error("実行対象がありません。db_all_recreate.env の ENABLED を確認してください。")
        return 1

    if not args.dry_run and not args.yes and not confirm_execution(selected, refresh_mode):
        logging.info("ユーザーによりキャンセルされました。")
        return 1

    failures = 0
    for target in selected:
        logging.info("=== 開始: %s (%s) ===", target.key, refresh_mode.value)
        try:
            exit_code = recreate_target(target, config, refresh_mode, args.dry_run)
        except Exception:
            logging.exception("対象処理が失敗しました: %s", target.key)
            exit_code = 1
        if exit_code != 0:
            failures += 1

    if failures:
        logging.error("完了（失敗 %s / %s 件）", failures, len(selected))
        return 1

    logging.info("すべての対象が正常終了しました（%s 件）", len(selected))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
