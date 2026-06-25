"""material_millsheet_manager アプリ互換スキーマパッチの単体テスト。"""

from pathlib import Path


def _patches_sql() -> str:
    path = (
        Path(__file__).resolve().parents[1]
        / ".docs"
        / "material_millsheet_manager"
        / "schema_app_patches.sql"
    )
    return path.read_text(encoding="utf-8")


def test_schema_app_patches_sets_boolean_defaults() -> None:
    sql = _patches_sql()

    assert "ALTER TABLE legacy_inspection_data ALTER COLUMN confirmed SET DEFAULT FALSE" in sql
    assert "ALTER TABLE inspection_data ALTER COLUMN confirmed SET DEFAULT FALSE" in sql
    assert "ALTER TABLE material_delivery_temp ALTER COLUMN registered_flag SET DEFAULT FALSE" in sql


def test_schema_app_patches_sets_primary_keys() -> None:
    sql = _patches_sql()

    assert "legacy_inspection_data_pkey" in sql
    assert "material_delivery_history_pkey" in sql
    assert "inspection_data_pkey" in sql


def test_schema_app_patches_sets_inspection_indexes() -> None:
    sql = _patches_sql()

    assert "idx_material_delivery_history_receipt_date" in sql
    assert "idx_inspection_data_purchase_id" in sql
    assert "idx_legacy_inspection_data_purchase_id" in sql
