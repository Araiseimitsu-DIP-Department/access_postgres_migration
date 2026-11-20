"""正規化の手順（製品マスタの修復と sql/ 配下のSQL）を開発DBへ順に一括適用する。

実行: リポジトリ直下で python -m access_postgres_normalization.apply_all_dev [--execute] [--down]
既定は手順の一覧を表示するだけで、何も変更しない。適用するには --execute を付ける。
--down を付けると、SQLの戻し（*_down.sql）を逆順に実行する。製品マスタの修復値は戻さない
（必要なら normalization_backup.product_master_before_repair から復元する）。

接続先は dev_db.py と同じく開発ホストに限定する（NORMALIZATION_DEV_HOST が開発ホスト以外なら中止）。
パスワードは NORMALIZATION_DEV_PASSWORD か --password-file で渡し、ログには出さない。
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from access_postgres_normalization.dev_db import POSTGRES_PORT, DevConnectionError, dev_connection_settings

LOGGER = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR / "sql"
REPO_ROOT = BASE_DIR.parent
REPAIR_MODULE = "access_postgres_normalization.repair_arai_product_master"
PASSWORD_VARIABLE = "devpw"
MASKED = "***"


@dataclass(frozen=True)
class SqlStep:
    """1本のSQL手順。database は psql の最初の接続先（SQL内の \\c で切り替わるものを含む）。"""

    name: str
    database: str
    needs_password: bool = False

    def path(self, direction: str) -> Path:
        return SQL_DIR / f"{self.name}_{direction}.sql"


# 実行順。README の手順と同じ順に並べる。
SQL_STEPS: tuple[SqlStep, ...] = (
    SqlStep("product_master/01_arai_masters", "arai_masters", needs_password=True),
    SqlStep("product_master/02_order_management", "order_management", needs_password=True),
    SqlStep("product_master/03_reference_indexes", "delivery_label_db"),
    SqlStep("product_master/04_subcon_manager", "subcon_manager", needs_password=True),
    SqlStep("product_master/05_secondary_process", "secondary_process_record_db"),
    SqlStep("product_master/06_material_scheduling", "material_scheduling", needs_password=True),
    SqlStep("product_master/07_subcon_product_master_full", "subcon_manager"),
    SqlStep("defect_information/01_aggregate_views", "appearance_inspection_db"),
    SqlStep("transactions/01_order_reconciliation", "order_performance_db", needs_password=True),
    SqlStep("transactions/02_delivery_checks", "order_management"),
    SqlStep("materials/01_unused_backups", "material_millsheet_manager"),
    SqlStep("materials/02_inspection_checks", "material_millsheet_manager"),
    SqlStep("materials/03_material_kind_checks", "material_millsheet_manager"),
    SqlStep("materials/04_material_kind_fix", "material_millsheet_manager"),
    SqlStep("materials/05_material_types_register", "material_millsheet_manager"),
)


@dataclass(frozen=True)
class Command:
    """実行する1手順。args にパスワードを含む場合があるため、表示には display() を使う。"""

    label: str
    args: tuple[str, ...]
    secret: str | None = None

    def display(self) -> str:
        shown = (arg.replace(self.secret, MASKED) if self.secret else arg for arg in self.args)
        return " ".join(shown)


def build_commands(settings: dict[str, str], *, down: bool, psql: str = "psql",
                   python: str = sys.executable) -> list[Command]:
    """適用（または戻し）の手順を実行順に組み立てる。"""
    password = settings.get("password")
    direction = "down" if down else "up"
    steps = reversed(SQL_STEPS) if down else SQL_STEPS
    commands: list[Command] = []
    if not down:
        commands.append(Command("製品マスタの形式崩れの修復", (python, "-m", REPAIR_MODULE, "--apply")))
    for step in steps:
        args = [psql, "-X", "-q", "-v", "ON_ERROR_STOP=1",
                "-h", settings["host"], "-p", str(POSTGRES_PORT), "-U", settings["user"],
                "-d", step.database, "-f", str(step.path(direction))]
        # 戻しのSQLはパスワードを使わない（外部サーバーを削除するだけ）
        if step.needs_password and not down:
            if not password:
                raise DevConnectionError(f"{step.name} にはパスワードが必要です。")
            args[1:1] = ["-v", f"{PASSWORD_VARIABLE}={password}"]
        commands.append(Command(f"{step.name}_{direction}.sql", tuple(args), password))
    return commands


def child_environment(settings: dict[str, str]) -> dict[str, str]:
    """psql と修復スクリプトに渡す環境変数（同じ開発ホスト・ユーザー・パスワード）。"""
    env = dict(os.environ)
    env["NORMALIZATION_DEV_HOST"] = settings["host"]
    env["NORMALIZATION_DEV_USER"] = settings["user"]
    env["PGCLIENTENCODING"] = "UTF8"
    if settings.get("password"):
        env["NORMALIZATION_DEV_PASSWORD"] = settings["password"]
        env["PGPASSWORD"] = settings["password"]
    return env


def run_commands(commands: list[Command], env: dict[str, str], runner=subprocess.run) -> int:
    """手順を順に実行し、失敗した時点で中止する。戻り値は終了コード。"""
    for number, command in enumerate(commands, start=1):
        LOGGER.info("[%d/%d] %s", number, len(commands), command.label)
        result = runner(list(command.args), env=env, cwd=str(REPO_ROOT), check=False)
        if result.returncode != 0:
            LOGGER.error("%s が失敗したため中止しました（終了コード %d）。以降の手順は実行していません。",
                         command.label, result.returncode)
            return result.returncode or 1
    LOGGER.info("すべての手順が完了しました（%d件）", len(commands))
    return 0


def _load_settings(password_file: str | None) -> dict[str, str]:
    settings = dev_connection_settings()
    if password_file:
        settings["password"] = Path(password_file).read_text(encoding="utf-8").strip()
    return settings


def main(argv: list[str] | None = None, runner=subprocess.run) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--execute", action="store_true", help="実際に開発DBへ適用する（省略時は一覧表示のみ）")
    parser.add_argument("--down", action="store_true", help="SQLの戻し（*_down.sql）を逆順に実行する")
    parser.add_argument("--password-file", help="開発DBのパスワードを1行で書いたファイル")
    parser.add_argument("--psql", default=os.environ.get("PSQL", "psql"), help="psql の実行ファイル")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        settings = _load_settings(args.password_file)
        commands = build_commands(settings, down=args.down, psql=args.psql)
    except (DevConnectionError, OSError) as error:
        LOGGER.error("%s", error)
        return 1

    missing = [c.label for c in commands if not Path(c.args[-1]).exists() and c.args[-1].endswith(".sql")]
    if missing:
        LOGGER.error("SQLファイルが見つかりません: %s", ", ".join(missing))
        return 1

    LOGGER.info("接続先 %s（ユーザー %s）、手順 %d件（%s）", settings["host"], settings["user"],
                len(commands), "戻し" if args.down else "適用")
    if not args.execute:
        for number, command in enumerate(commands, start=1):
            LOGGER.info("  %d. %s", number, command.display())
        LOGGER.info("変更していません。実行するには --execute を付けてください。")
        return 0
    return run_commands(commands, child_environment(settings), runner)


if __name__ == "__main__":
    raise SystemExit(main())
