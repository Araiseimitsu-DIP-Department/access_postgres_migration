"""order_management アプリ互換スキーマパッチの単体テスト。"""

from pathlib import Path


def _patches_sql() -> str:
    path = (
        Path(__file__).resolve().parents[1]
        / ".docs"
        / "order_management"
        / "schema_app_patches.sql"
    )
    return path.read_text(encoding="utf-8")


def test_schema_app_patches_sets_order_indexes() -> None:
    sql = _patches_sql()

    assert "CREATE INDEX IF NOT EXISTS idx_orders_order_date" in sql
    assert "CREATE INDEX IF NOT EXISTS idx_orders_order_id" in sql


def test_schema_app_patches_sets_delivery_sequence_and_indexes() -> None:
    sql = _patches_sql()

    assert "CREATE SEQUENCE IF NOT EXISTS deliveries_delivery_id_seq" in sql
    assert "ALTER TABLE deliveries ALTER COLUMN delivery_id SET DEFAULT nextval" in sql
    assert "idx_deliveries_order_id" in sql


def test_schema_app_patches_sets_duplicate_customers_sequence() -> None:
    sql = _patches_sql()

    assert "CREATE SEQUENCE IF NOT EXISTS duplicate_customers_id_seq" in sql
    assert "ALTER TABLE duplicate_customers ALTER COLUMN id SET DEFAULT nextval" in sql
