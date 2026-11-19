-- 03_reference_indexes_up.sql で追加した索引を削除する（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d delivery_label_db -f 03_reference_indexes_down.sql
\set ON_ERROR_STOP on

\ir 00_require_dev.sql
DROP INDEX IF EXISTS public.ix_delivery_label_history_product_code;

\c subcon_manager
\ir 00_require_dev.sql
DROP INDEX IF EXISTS public.ix_purchase_orders_product_no;
DROP INDEX IF EXISTS public.ix_deliveries_product_no;
