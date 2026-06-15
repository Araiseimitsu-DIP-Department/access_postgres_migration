"""Access / ODBC が返す値を PostgreSQL 向けに正規化する。"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any


def coerce_date_opt(val: Any) -> date | None:
    """日付として格納する列用。DATETIME で来た場合は日付のみ採る。"""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    return None


def coerce_int_opt(val: Any) -> int | None:
    """整数列用。小数・DECIMAL が整数なら変換する。"""
    if val is None:
        return None
    if isinstance(val, bool):
        return int(val)
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        if val != val:  # NaN
            return None
        if val.is_integer():
            return int(val)
        return int(round(val))
    if isinstance(val, Decimal):
        try:
            return int(val)
        except Exception:
            return None
    if isinstance(val, str):
        stripped = val.strip()
        if not stripped:
            return None
        try:
            return int(Decimal(stripped))
        except Exception:
            return None
    return None


def truncate_str(val: Any, maxlen: int) -> str | None:
    """VARCHAR の上限遵守。長すぎる場合は切り詰める。"""
    if val is None:
        return None
    text = str(val).strip()
    if maxlen <= 0:
        return text
    if len(text) > maxlen:
        return text[:maxlen]
    return text


def coerce_str_optional(val: Any, maxlen: int) -> str | None:
    """空文字は DB NULL とみなしたいとき用。"""
    s = truncate_str(val, maxlen)
    if s is None or s == "":
        return None
    return s
