"""material_scheduling アプリ互換スキーマパッチの単体テスト。"""

from pathlib import Path


def _patches_sql() -> str:
    path = (
        Path(__file__).resolve().parents[1]
        / ".docs"
        / "material_scheduling"
        / "schema_app_patches.sql"
    )
    return path.read_text(encoding="utf-8")


def test_schema_app_patches_expands_management_sheet_master_columns() -> None:
    sql = _patches_sql()

    assert "ALTER COLUMN next_process TYPE VARCHAR(255)" in sql
    assert "ALTER COLUMN material_diameter TYPE VARCHAR(255)" in sql


def test_schema_app_patches_sets_production_order_sequences_and_defaults() -> None:
    sql = _patches_sql()

    assert "CREATE SEQUENCE IF NOT EXISTS production_orders_id_seq" in sql
    assert "ALTER TABLE production_orders ALTER COLUMN exp_flag SET DEFAULT FALSE" in sql
    assert "idx_production_orders_part_no" in sql


def test_schema_app_patches_sets_set_schedule_sequences() -> None:
    sql = _patches_sql()

    assert "CREATE SEQUENCE IF NOT EXISTS set_schedules_id_seq" in sql
    assert "idx_set_schedules_part_no" in sql
