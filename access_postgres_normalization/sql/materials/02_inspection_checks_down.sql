-- 02_inspection_checks_up.sql で追加した照合用ビューを削除する（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f 02_inspection_checks_down.sql
\set ON_ERROR_STOP on

BEGIN;
\ir ../product_master/00_require_dev.sql
DROP VIEW IF EXISTS public.material_inspection_orphans;
COMMIT;
