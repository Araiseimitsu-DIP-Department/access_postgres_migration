"""本番DB(121)の内容を開発DB(120)へ複製し、外部サーバーを開発向けに直してから正規化を一括適用する。

実行: リポジトリ直下で python -m access_postgres_normalization.refresh_dev_from_prod [--execute]
既定は対象DBの一覧を表示するだけで、何も変更しない。複製するには --execute を付ける。

処理の順序と安全策:
1. 本番と開発の両方にあるDB（postgres を除く）を対象にする。片方にしかないDBには触らない。
2. 対象DBをすべて本番から pg_dump する（読み取り専用の接続）。1件でも失敗したら開発には触らずに中止する。
3. DBごとに、開発のDBを作り直して（ロケール・エンコーディングは開発側の値を引き継ぐ）復元する。
   所有者・権限は復元しない（開発には本番のロールがないため）。ユーザーマッピングは本番の認証情報を
   含むため復元しない。本番を向く外部サーバーを開発へ切り替えてから、開発の認証情報で作り直す。
4. apply_all_dev と同じ手順で正規化を一括適用する。
5. 本番を向く外部サーバーが残っていないことを確認する。

本番へは pg_dump とDB一覧の参照だけを行い、書き込みは一切しない。開発への接続は dev_db.py と同じく
開発ホストに限定する。パスワードは実行時に画面で入力する（ファイル・環境変数でも渡せる）。
コマンド引数とログには出さない。
"""

from __future__ import annotations

import argparse
import getpass
import logging
import os
import re
import subprocess
import sys
import tempfile
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

import psycopg2
from psycopg2 import sql

from access_postgres_normalization import apply_all_dev
from access_postgres_normalization.dev_db import (
    CONNECTION_TIMEOUT_SECONDS,
    POSTGRES_PORT,
    DevConnectionError,
    connect_dev,
    dev_connection_settings,
)

LOGGER = logging.getLogger(__name__)

PROD_HOST = "192.168.1.121"
# 管理用DBは複製しない（接続の基点であり、業務データを持たない）
EXCLUDED_DATABASES = frozenset({"postgres"})
MAINTENANCE_DATABASE = "postgres"
READ_ONLY_PGOPTIONS = "-c default_transaction_read_only=on"
# pg_restore -l の行の例: 3596; 0 0 USER MAPPING - USER MAPPING postgres SERVER arai_masters_srv postgres
USER_MAPPING_TOC = re.compile(r"\bUSER MAPPING - USER MAPPING (?P<user>.+?) SERVER (?P<server>\S+)")
TOC_COMMENT = ";"
PUBLIC_ROLE = "public"


class RefreshError(RuntimeError):
    """複製を続けられない失敗。"""


@dataclass(frozen=True)
class ConnectionSettings:
    host: str
    user: str
    password: str


@dataclass(frozen=True)
class Tools:
    """PostgreSQL のクライアントコマンドの実行ファイル。"""

    pg_dump: str = "pg_dump"
    pg_restore: str = "pg_restore"
    psql: str = "psql"

    @classmethod
    def from_bin_dir(cls, bin_dir: str | None) -> "Tools":
        if not bin_dir:
            return cls()
        base = Path(bin_dir)
        return cls(*(str(base / name) for name in ("pg_dump", "pg_restore", "psql")))


@dataclass(frozen=True)
class UserMapping:
    user: str
    server: str


@dataclass(frozen=True)
class DumpedDatabase:
    name: str
    dump_path: Path
    toc_path: Path
    user_mappings: tuple[UserMapping, ...]


@dataclass(frozen=True)
class FdwPlan:
    """外部サーバーの切替計画。warnings は切り替えずに残す理由。"""

    servers_to_switch: tuple[str, ...]
    mappings_to_create: tuple[UserMapping, ...]
    warnings: tuple[str, ...]


# ---------------------------------------------------------------------------
# 判定・組み立て（DBに触れない処理）
# ---------------------------------------------------------------------------

def select_targets(prod_databases: list[str], dev_databases: list[str]) -> list[str]:
    """本番と開発の両方にあるDBを対象にする。"""
    return sorted((set(prod_databases) & set(dev_databases)) - EXCLUDED_DATABASES)


def _unquote_identifier(name: str) -> str:
    name = name.strip()
    if len(name) >= 2 and name.startswith('"') and name.endswith('"'):
        return name[1:-1].replace('""', '"')
    return name


def split_toc(toc_text: str) -> tuple[str, tuple[UserMapping, ...]]:
    """復元の目次からユーザーマッピングの行を外し（行頭を ; にする）、外したマッピングを返す。"""
    lines: list[str] = []
    mappings: list[UserMapping] = []
    for line in toc_text.splitlines():
        match = None if line.startswith(TOC_COMMENT) else USER_MAPPING_TOC.search(line)
        if match:
            mappings.append(UserMapping(_unquote_identifier(match["user"]), _unquote_identifier(match["server"])))
            lines.append(f"{TOC_COMMENT}{line}")
        else:
            lines.append(line)
    return "\n".join(lines) + "\n", tuple(mappings)


def parse_options(options: list[str] | None) -> dict[str, str]:
    """pg_foreign_server.srvoptions（"key=value" の配列）を辞書にする。"""
    return dict(option.split("=", 1) for option in options or [])


def plan_fdw_switch(servers: list[tuple[str, list[str] | None]], mappings: tuple[UserMapping, ...],
                    dev_roles: set[str]) -> FdwPlan:
    """本番を向く外部サーバーを切替対象にし、作り直すユーザーマッピングを決める。"""
    switch: list[str] = []
    warnings: list[str] = []
    for name, options in servers:
        host = parse_options(options).get("host")
        if host == PROD_HOST:
            switch.append(name)
        else:
            warnings.append(f"外部サーバー {name} は本番以外（host={host}）を向くため切り替えない")
    create: list[UserMapping] = []
    for mapping in mappings:
        if mapping.server not in switch:
            warnings.append(f"外部サーバー {mapping.server} を切り替えないため、{mapping.user} のユーザーマッピングは作らない")
        elif mapping.user != PUBLIC_ROLE and mapping.user not in dev_roles:
            warnings.append(f"開発にロール {mapping.user} がないため、{mapping.server} のユーザーマッピングは作らない")
        else:
            create.append(mapping)
    return FdwPlan(tuple(switch), tuple(create), tuple(warnings))


def pg_dump_args(tools: Tools, prod: ConnectionSettings, database: str, output: Path) -> list[str]:
    return [tools.pg_dump, "-h", prod.host, "-p", str(POSTGRES_PORT), "-U", prod.user,
            "-d", database, "-Fc", "--no-password", "-f", str(output)]


def pg_restore_list_args(tools: Tools, dump_path: Path) -> list[str]:
    return [tools.pg_restore, "-l", str(dump_path)]


def pg_restore_args(tools: Tools, dev: ConnectionSettings, dumped: DumpedDatabase) -> list[str]:
    return [tools.pg_restore, "-h", dev.host, "-p", str(POSTGRES_PORT), "-U", dev.user, "--no-password",
            "-d", dumped.name, "--no-owner", "--no-privileges", "--exit-on-error", "--single-transaction",
            "-L", str(dumped.toc_path), str(dumped.dump_path)]


def prod_environment(prod: ConnectionSettings) -> dict[str, str]:
    """本番へのコマンド用。読み取り専用のトランザクションを強制する。"""
    env = dict(os.environ)
    env.update(PGPASSWORD=prod.password, PGOPTIONS=READ_ONLY_PGOPTIONS, PGCLIENTENCODING="UTF8")
    return env


def dev_environment(dev: ConnectionSettings) -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PGOPTIONS", None)
    env.update(PGPASSWORD=dev.password, PGCLIENTENCODING="UTF8")
    return env


# ---------------------------------------------------------------------------
# 接続設定
# ---------------------------------------------------------------------------

def _require_password(password_file: str | None, variable: str, label: str, prompt=getpass.getpass) -> str:
    """パスワードをファイル・環境変数の順に探し、どちらにもなければ画面で入力を求める（入力は表示しない）。"""
    if password_file:
        password = Path(password_file).read_text(encoding="utf-8").strip()
    else:
        password = os.environ.get(variable)
        if not password:
            try:
                password = prompt(f"{label}のパスワード: ")
            except EOFError as error:
                raise DevConnectionError(f"{label}のパスワードを入力できませんでした。") from error
    if not password:
        raise DevConnectionError(f"{label}のパスワードが空です。")
    return password


def load_settings(dev_password_file: str | None, prod_password_file: str | None, prompt=getpass.getpass,
                  ) -> tuple[ConnectionSettings, ConnectionSettings]:
    dev_raw = dev_connection_settings()
    prod_user = os.environ.get("NORMALIZATION_PROD_USER", dev_raw["user"])
    dev_password = _require_password(dev_password_file, "NORMALIZATION_DEV_PASSWORD",
                                     f"開発DB {dev_raw['host']}（{dev_raw['user']}）", prompt)
    prod_password = _require_password(prod_password_file, "NORMALIZATION_PROD_PASSWORD",
                                      f"本番DB {PROD_HOST}（{prod_user}）", prompt)
    dev = ConnectionSettings(dev_raw["host"], dev_raw["user"], dev_password)
    prod = ConnectionSettings(PROD_HOST, prod_user, prod_password)
    if dev.host == prod.host:
        raise DevConnectionError("開発と本番の接続先が同じです。")
    return dev, prod


# ---------------------------------------------------------------------------
# DB操作
# ---------------------------------------------------------------------------

def connect_prod_readonly(prod: ConnectionSettings, database: str):
    """本番への読み取り専用接続。DB一覧の参照だけに使う。"""
    conn = psycopg2.connect(host=PROD_HOST, port=POSTGRES_PORT, user=prod.user, password=prod.password,
                            dbname=database, connect_timeout=CONNECTION_TIMEOUT_SECONDS,
                            options=READ_ONLY_PGOPTIONS)
    conn.set_session(readonly=True)
    return conn


def _dev_raw(dev: ConnectionSettings) -> dict[str, str]:
    return {"host": dev.host, "user": dev.user, "password": dev.password}


def connect_dev_write(dev: ConnectionSettings, database: str, *, autocommit: bool = False):
    conn = connect_dev(_dev_raw(dev), database, readonly=False)
    conn.autocommit = autocommit
    with conn.cursor() as cur:
        # DBの作り直しは60秒を超えることがあるため、文のタイムアウトを外す
        cur.execute("SET statement_timeout = 0")
    return conn


def list_databases(conn) -> list[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT datname FROM pg_database WHERE NOT datistemplate AND datallowconn ORDER BY datname")
        return [row[0] for row in cur.fetchall()]


def recreate_dev_database(conn, database: str) -> None:
    """開発のDBを削除して空で作り直す。エンコーディング・ロケール・所有者は開発側の値を引き継ぐ。"""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT pg_encoding_to_char(encoding), datcollate, datctype, pg_get_userbyid(datdba) "
            "FROM pg_database WHERE datname = %s", (database,))
        row = cur.fetchone()
        if row is None:
            raise RefreshError(f"開発に {database} がありません。")
        encoding, collate, ctype, owner = row
        name = sql.Identifier(database)
        cur.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(name))
        cur.execute(sql.SQL("CREATE DATABASE {} WITH TEMPLATE template0 ENCODING {} LC_COLLATE {} "
                            "LC_CTYPE {} OWNER {}").format(
            name, sql.Literal(encoding), sql.Literal(collate), sql.Literal(ctype), sql.Identifier(owner)))


def _mapping_role(user: str) -> sql.Composable:
    return sql.SQL("PUBLIC") if user == PUBLIC_ROLE else sql.Identifier(user)


def switch_foreign_servers(dev: ConnectionSettings, dumped: DumpedDatabase) -> FdwPlan:
    """本番を向く外部サーバーを開発へ切り替え、開発の認証情報でユーザーマッピングを作る。"""
    with closing(connect_dev_write(dev, dumped.name)) as conn:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT srvname, srvoptions FROM pg_foreign_server ORDER BY srvname")
            servers = cur.fetchall()
            cur.execute("SELECT rolname FROM pg_roles")
            roles = {row[0] for row in cur.fetchall()}
            plan = plan_fdw_switch(servers, dumped.user_mappings, roles)
            for server in plan.servers_to_switch:
                cur.execute(sql.SQL("ALTER SERVER {} OPTIONS (SET host {})").format(
                    sql.Identifier(server), sql.Literal(dev.host)))
            for mapping in plan.mappings_to_create:
                cur.execute(sql.SQL("CREATE USER MAPPING FOR {} SERVER {} OPTIONS (user {}, password {})").format(
                    _mapping_role(mapping.user), sql.Identifier(mapping.server),
                    sql.Literal(dev.user), sql.Literal(dev.password)))
    return plan


def find_prod_facing_servers(dev: ConnectionSettings, databases: list[str]) -> list[str]:
    """開発の各DBで本番を向く外部サーバーを列挙する（最終確認用、読み取りのみ）。"""
    found: list[str] = []
    for database in databases:
        with closing(connect_dev(_dev_raw(dev), database, readonly=True)) as conn, conn.cursor() as cur:
            cur.execute("SELECT srvname, srvoptions FROM pg_foreign_server")
            found += [f"{database}.{name}" for name, options in cur.fetchall()
                      if parse_options(options).get("host") == PROD_HOST]
    return found


# ---------------------------------------------------------------------------
# 手順
# ---------------------------------------------------------------------------

def _run(args: list[str], env: dict[str, str], runner, *, capture: bool = False):
    result = runner(args, env=env, check=False, capture_output=capture, text=capture,
                    encoding="utf-8" if capture else None)
    if result.returncode != 0:
        detail = (result.stderr or "").strip() if capture else ""
        raise RefreshError(f"{Path(args[0]).name} が失敗しました（終了コード {result.returncode}）{detail}")
    return result


def dump_all(targets: list[str], workdir: Path, prod: ConnectionSettings, tools: Tools,
             runner=subprocess.run) -> list[DumpedDatabase]:
    """対象DBをすべて本番から取得する。1件でも失敗したら例外にする（開発には触らない）。"""
    env = prod_environment(prod)
    dumped: list[DumpedDatabase] = []
    for number, database in enumerate(targets, start=1):
        LOGGER.info("[取得 %d/%d] %s", number, len(targets), database)
        dump_path = workdir / f"{database}.dump"
        _run(pg_dump_args(tools, prod, database, dump_path), env, runner)
        toc = _run(pg_restore_list_args(tools, dump_path), env, runner, capture=True).stdout
        toc_text, mappings = split_toc(toc)
        toc_path = workdir / f"{database}.toc"
        toc_path.write_text(toc_text, encoding="utf-8")
        dumped.append(DumpedDatabase(database, dump_path, toc_path, mappings))
    return dumped


def restore_all(dumped: list[DumpedDatabase], dev: ConnectionSettings, tools: Tools,
                runner=subprocess.run) -> None:
    """開発のDBを作り直して復元し、すぐに外部サーバーを開発へ切り替える。"""
    env = dev_environment(dev)
    for number, item in enumerate(dumped, start=1):
        LOGGER.info("[復元 %d/%d] %s", number, len(dumped), item.name)
        try:
            with closing(connect_dev_write(dev, MAINTENANCE_DATABASE, autocommit=True)) as admin:
                recreate_dev_database(admin, item.name)
            _run(pg_restore_args(tools, dev, item), env, runner)
            plan = switch_foreign_servers(dev, item)
        except (RefreshError, psycopg2.Error) as error:
            remaining = ", ".join(d.name for d in dumped[number:]) or "なし"
            raise RefreshError(f"{item.name} の復元に失敗しました（このDBは空か途中の状態です）。"
                               f"未処理: {remaining}。原因: {error}") from error
        for server in plan.servers_to_switch:
            LOGGER.info("  外部サーバー %s を %s へ切り替えました", server, dev.host)
        for warning in plan.warnings:
            LOGGER.warning("  %s", warning)


def normalize(dev: ConnectionSettings, tools: Tools, runner=subprocess.run) -> None:
    """apply_all_dev と同じ手順で正規化を一括適用する。"""
    settings = _dev_raw(dev)
    commands = apply_all_dev.build_commands(settings, down=False, psql=tools.psql)
    if apply_all_dev.run_commands(commands, apply_all_dev.child_environment(settings), runner) != 0:
        raise RefreshError("正規化の一括適用に失敗しました。")


def list_both(dev: ConnectionSettings, prod: ConnectionSettings) -> tuple[list[str], list[str]]:
    with closing(connect_prod_readonly(prod, MAINTENANCE_DATABASE)) as prod_conn:
        prod_databases = list_databases(prod_conn)
    with closing(connect_dev(_dev_raw(dev), MAINTENANCE_DATABASE, readonly=True)) as dev_conn:
        dev_databases = list_databases(dev_conn)
    return prod_databases, dev_databases


def refresh(targets: list[str], dev: ConnectionSettings, prod: ConnectionSettings, tools: Tools,
            runner=subprocess.run) -> None:
    with tempfile.TemporaryDirectory(prefix="refresh_dev_") as workdir:
        dumped = dump_all(targets, Path(workdir), prod, tools, runner)
        restore_all(dumped, dev, tools, runner)
    normalize(dev, tools, runner)
    remaining = find_prod_facing_servers(dev, targets)
    if remaining:
        raise RefreshError(f"本番を向く外部サーバーが残っています: {', '.join(remaining)}")


def main(argv: list[str] | None = None, runner=subprocess.run) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--execute", action="store_true", help="実際に複製する（省略時は対象の一覧表示のみ）")
    parser.add_argument("--dev-password-file", help="開発DBのパスワードを1行で書いたファイル（省略時は入力を求める）")
    parser.add_argument("--prod-password-file", help="本番DBのパスワードを1行で書いたファイル（省略時は入力を求める）")
    parser.add_argument("--pg-bin", default=os.environ.get("PG_BIN"),
                        help="pg_dump・pg_restore・psql のあるフォルダ（省略時は PATH から探す）")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        dev, prod = load_settings(args.dev_password_file, args.prod_password_file)
        prod_databases, dev_databases = list_both(dev, prod)
    except (DevConnectionError, OSError, psycopg2.Error) as error:
        LOGGER.error("%s", error)
        return 1

    targets = select_targets(prod_databases, dev_databases)
    skipped = sorted(set(dev_databases) - set(targets))
    LOGGER.info("複製元 %s → 複製先 %s、対象 %d件: %s", prod.host, dev.host, len(targets), ", ".join(targets))
    LOGGER.info("触らない開発DB: %s", ", ".join(skipped) or "なし")
    if not args.execute:
        LOGGER.info("変更していません。複製するには --execute を付けてください。")
        return 0

    try:
        refresh(targets, dev, prod, Tools.from_bin_dir(args.pg_bin), runner)
    except (RefreshError, DevConnectionError, OSError, psycopg2.Error) as error:
        LOGGER.error("%s", error)
        return 1
    LOGGER.info("本番の内容を開発へ複製し、正規化まで完了しました（%d件）", len(targets))
    return 0


if __name__ == "__main__":
    sys.exit(main())
