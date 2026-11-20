-- 04_material_kind_fix_up.sql で書き換えた入庫の材質・区分記号を、控えておいた変更前の値に戻す（開発DB専用）。
-- 控えの表は戻したあと削除する。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f 04_material_kind_fix_down.sql
\set ON_ERROR_STOP on

\ir ../product_master/00_require_dev.sql
BEGIN;
DO $$
BEGIN
  IF to_regclass('normalization_backup.material_kind_fix_before') IS NOT NULL THEN
    UPDATE public.material_delivery_history h
    SET material_kind = b.material_kind,
        category_code = b.category_code
    FROM normalization_backup.material_kind_fix_before b
    WHERE b.id = h.id;
    DROP TABLE normalization_backup.material_kind_fix_before;
  END IF;
END $$;
COMMIT;
