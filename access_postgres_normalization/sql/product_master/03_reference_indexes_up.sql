-- 「使用中の品番」判定（arai_masters.product_no_in_use）で照会する列に索引を作る（開発DB専用）。
-- 受注管理の orders.product_no は既存の idx_orders_product_no を使う。
-- 実行: psql -h 192.168.1.120 -U postgres -d delivery_label_db -f 03_reference_indexes_up.sql
-- 戻す場合は 03_reference_indexes_down.sql。索引の追加のみでデータ・アプリの動作は変わらない。
\set ON_ERROR_STOP on

\ir 00_require_dev.sql
CREATE INDEX IF NOT EXISTS ix_delivery_label_history_product_code
  ON public.delivery_label_history (product_code);

\c subcon_manager
\ir 00_require_dev.sql
CREATE INDEX IF NOT EXISTS ix_purchase_orders_product_no ON public.purchase_orders (product_no);
CREATE INDEX IF NOT EXISTS ix_deliveries_product_no ON public.deliveries (product_no);
