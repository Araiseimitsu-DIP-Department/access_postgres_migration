"""arai_masters 製品マスタの形式崩れ修復ルールを検証する。"""

import pytest

from access_postgres_normalization.dev_db import DevConnectionError, dev_connection_settings
from access_postgres_normalization.repair_arai_product_master import (
    Repair,
    normalize_numeric_text,
    plan_repairs,
    restore_next_process,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("42.0", "42"), ("114.", "114"), ("5.", "5"), ("7", None), ("ER", None), (None, None), ("1.5", None)],
)
def test_normalize_numeric_text(value, expected) -> None:
    assert normalize_numeric_text(value) == expected


def test_restore_next_process_uses_full_value_when_truncated() -> None:
    assert restore_next_process("ｻﾃﾝ黒色ｱﾙﾏｲﾄ", ["ｻﾃﾝ黒色ｱﾙﾏｲﾄ 膜厚6~10μ", None]) == "ｻﾃﾝ黒色ｱﾙﾏｲﾄ 膜厚6~10μ"


def test_restore_next_process_skips_short_or_conflicting_values() -> None:
    # 10文字未満は切り捨てではない
    assert restore_next_process("洗浄", ["洗浄 追加工程"]) is None
    # 候補どうしが食い違う場合は判断しない
    assert restore_next_process("0123456789", ["0123456789A", "0123456789B"]) is None


def test_restore_next_process_prefers_longest_when_candidate_is_also_truncated() -> None:
    # 受注管理は25文字で切れ、委託加工に完全な値がある場合
    assert restore_next_process("0123456789", ["0123456789ABC", "0123456789ABCDEF"]) == "0123456789ABCDEF"
    # 先頭が一致しない値では復元しない
    assert restore_next_process("0123456789", ["別の工程名です"]) is None


def test_plan_repairs_keeps_content_differences() -> None:
    rows = [("P1", "A-1", "0123456789", "42.0", "5."), ("P2", "B-2", "短い", "57", "20")]
    repairs = plan_repairs(rows, {"A-1": "0123456789XYZ"}, {})
    assert repairs == [
        Repair("P1", "next_process", "0123456789", "0123456789XYZ"),
        Repair("P1", "process_code", "42.0", "42"),
        Repair("P1", "closing_day", "5.", "5"),
    ]


def test_dev_connection_rejects_non_dev_host() -> None:
    with pytest.raises(DevConnectionError):
        dev_connection_settings({"NORMALIZATION_DEV_HOST": "192.168.1.121", "NORMALIZATION_DEV_USER": "postgres"})
