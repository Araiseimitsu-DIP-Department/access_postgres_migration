"""Access / PostgreSQL 接続の既定値と .env 読み込み。"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_ACCESS_DB_UNC = (
    r"\\192.168.1.200\共有\生産管理課\AccessDB\加工進行表DB.accdb"
)
DEFAULT_PG_DSN = (
    "postgresql://postgres:Arai7786@192.168.1.120:5432/production_progress"
)


def build_conn_str(db_path: str) -> str:
    return (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={db_path};"
    )


def _to_short_path(path: Path) -> str:
    try:
        import ctypes

        buf = ctypes.create_unicode_buffer(512)
        ctypes.windll.kernel32.GetShortPathNameW(str(path), buf, 512)
        result = buf.value
        if result:
            return result
    except Exception:
        pass
    return str(path)


def normalize_db_path_for_odbc(db_path: str) -> str:
    p = Path(db_path)
    s = str(p)
    if s.startswith("\\\\") or s.startswith("//"):
        return s
    return _to_short_path(p.resolve())


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


def load_project_dotenv(project_root: Path) -> Path | None:
    """プロジェクトルートの .env を読み込む（既存の環境変数は上書きしない）。"""
    env_path = project_root / ".env"
    if not env_path.is_file():
        return None
    text = env_path.read_text(encoding="utf-8")
    for key, value in _parse_dotenv_lines(text):
        if key not in os.environ:
            os.environ[key] = value
    return env_path
