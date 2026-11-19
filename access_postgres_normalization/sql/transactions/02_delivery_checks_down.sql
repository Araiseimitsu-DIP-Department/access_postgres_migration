-- 02_delivery_checks_up.sql で追加した照合用ビューを削除する（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d order_management -f 02_delivery_checks_down.sql
\set ON_ERROR_STOP on

\ir ../product_master/00_require_dev.sql
DROP VIEW IF EXISTS public.order_delivery_qty_check;

\c subcon_manager
\ir ../product_master/00_require_dev.sql
DROP VIEW IF EXISTS public.purchase_order_delivery_qty_check;
