"""正規化作業用の開発DB接続。本番へ接続しないよう接続先を開発ホストに限定する。"""

import logging
import os

import psycopg2

DEFAULT_DEV_HOST = "192.168.1.120"
# 正規化作業は開発環境だけで行う。本番ホストを誤って指定した場合は接続しない。
ALLOWED_DEV_HOSTS = frozenset({DEFAULT_DEV_HOST})
POSTGRES_PORT = 5432
CONNECTION_TIMEOUT_SECONDS = 5
STATEMENT_TIMEOUT = "60s"
LOCK_TIMEOUT = "5s"

LOGGER = logging.getLogger(__name__)


class DevConnectionError(RuntimeError):
    """開発DBの接続設定が不正な場合のエラー。"""


def dev_connection_settings(environ: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ if environ is None else environ
    host = env.get("NORMALIZATION_DEV_HOST", DEFAULT_DEV_HOST)
    if host not in ALLOWED_DEV_HOSTS:
        raise DevConnectionError(f"開発ホスト以外には接続しません: {host}")
    user = env.get("NORMALIZATION_DEV_USER")
    if not user:
        raise DevConnectionError("NORMALIZATION_DEV_USER を設定してください。")
    settings = {"host": host, "user": user}
    password = env.get("NORMALIZATION_DEV_PASSWORD")
    if password is not None:
        settings["password"] = password
    return settings


def connect_dev(settings: dict[str, str], database: str, *, readonly: bool = True):
    options = f"-c statement_timeout={STATEMENT_TIMEOUT} -c lock_timeout={LOCK_TIMEOUT} -c TimeZone=UTC"
    if readonly:
        options = f"-c default_transaction_read_only=on {options}"
    conn = psycopg2.connect(
        **settings,
        port=POSTGRES_PORT,
        dbname=database,
        connect_timeout=CONNECTION_TIMEOUT_SECONDS,
        options=options,
    )
    if readonly:
        conn.set_session(readonly=True)
    return conn
