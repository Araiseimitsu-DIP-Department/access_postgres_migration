-- 01_aggregate_views_up.sql で追加した集計用ビューを削除する（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d appearance_inspection_db -f 01_aggregate_views_down.sql
\set ON_ERROR_STOP on

BEGIN;

\ir ../product_master/00_require_dev.sql

DROP VIEW IF EXISTS public.defect_information_counts;
DROP VIEW IF EXISTS public.defect_information_inspectors;

COMMIT;
