-- 03_material_kind_checks_up.sql で追加した照合ビューと表記揺れの対応表を削除する（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f 03_material_kind_checks_down.sql
\set ON_ERROR_STOP on

\ir ../product_master/00_require_dev.sql
BEGIN;
DROP VIEW IF EXISTS public.material_kind_checks;
DROP TABLE IF EXISTS public.material_kind_aliases;
COMMIT;
