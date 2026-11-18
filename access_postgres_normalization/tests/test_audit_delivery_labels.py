"""現品票履歴の一致件数を検証する。"""

from collections import Counter

from access_postgres_normalization.audit_delivery_labels import summarize


def test_summarize_preserves_nulls_and_duplicate_counts() -> None:
    inspection = Counter({("lot-a", None): 3, ("lot-b", 0): 1})
    labels = Counter({("lot-a", None): 2, ("lot-a", 0): 1, ("lot-c", None): 1})

    assert summarize(inspection, labels) == {
        "外観検査側": 4,
        "現品票側": 4,
        "全11列一致": 2,
        "外観検査側のみ": 2,
        "現品票側のみ": 2,
    }
