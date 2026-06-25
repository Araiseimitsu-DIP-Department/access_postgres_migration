"""アプリケーション共通のログ設定。"""

from __future__ import annotations

import logging
from pathlib import Path


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"


def setup_logger(name: str = "access_migration", level: str = "INFO") -> logging.Logger:
    """コンソールとlogs/app.logへ出力するロガーを返す。"""

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(_to_log_level(level))
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(logs_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def _to_log_level(level: str) -> int:
    """文字列のログレベルをlogging用の数値へ変換する。"""

    return getattr(logging, level.upper(), logging.INFO)
