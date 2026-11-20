-- 05_material_types_register_up.sql を戻す（開発DB専用）。
--   入庫の材質・区分記号を控えの値に戻し、追加した対応表の行と、登録した材質を削除する。控えの表も削除する。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f 05_material_types_register_down.sql
\set ON_ERROR_STOP on

\ir ../product_master/00_require_dev.sql
BEGIN;
DO $$
BEGIN
  IF to_regclass('normalization_backup.material_category_fix_before') IS NOT NULL THEN
    UPDATE public.material_delivery_history h
    SET material_kind = b.material_kind,
        category_code = b.category_code
    FROM normalization_backup.material_category_fix_before b
    WHERE b.id = h.id;
    DROP TABLE normalization_backup.material_category_fix_before;
  END IF;

  IF to_regclass('public.material_kind_aliases') IS NOT NULL THEN
    DELETE FROM public.material_kind_aliases
    WHERE alias IN ('303', '303Cu', '1144 ASTM A31', 'SUM22φ8.165G');
  END IF;

  IF to_regclass('normalization_backup.material_types_added') IS NOT NULL THEN
    DELETE FROM public.material_types t
    USING normalization_backup.material_types_added a
    WHERE a.material_type = t.material_type;
    DROP TABLE normalization_backup.material_types_added;
  END IF;
END $$;
COMMIT;
