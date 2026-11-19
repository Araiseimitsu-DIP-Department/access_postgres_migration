-- 01_order_reconciliation_up.sql で追加した照合用ビューと外部テーブルを削除する（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d order_performance_db -f 01_order_reconciliation_down.sql
\set ON_ERROR_STOP on

BEGIN;

\ir ../product_master/00_require_dev.sql

DROP VIEW IF EXISTS public.order_reconciliation;
DROP FOREIGN TABLE IF EXISTS order_management.orders;
DROP SCHEMA IF EXISTS order_management;
DROP SERVER IF EXISTS order_management_srv CASCADE;

COMMIT;
