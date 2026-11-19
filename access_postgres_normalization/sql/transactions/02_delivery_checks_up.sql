-- 注文・発注に保存された「納入済数」と、納品・納入の合計が合わない行を一覧する照合用ビューを追加する（開発DB専用）。
-- 完納扱い（完了フラグが立ち、済数＝注文数）は各アプリの仕様のため対象外。データとアプリの動作は変えない。
-- 実行: psql -h 192.168.1.120 -U postgres -d order_management -f 02_delivery_checks_up.sql
-- 戻す場合は 02_delivery_checks_down.sql。
\set ON_ERROR_STOP on

-- 受注管理: orders.delivery_qty と deliveries の合計（完納フラグ completed_flag = '1'）
\ir ../product_master/00_require_dev.sql
CREATE OR REPLACE VIEW public.order_delivery_qty_check AS
SELECT
  o.order_id,
  o.order_date::date AS order_date,
  o.product_no,
  o.order_qty,
  o.delivery_qty AS stored_delivery_qty,
  coalesce(d.delivery_total, 0) AS delivery_total,
  o.order_balance,
  o.completed_flag
FROM public.orders o
LEFT JOIN (
  SELECT order_id, sum(delivery_qty) AS delivery_total FROM public.deliveries GROUP BY order_id
) d USING (order_id)
WHERE coalesce(o.delivery_qty, 0) <> coalesce(d.delivery_total, 0)
  AND NOT (o.completed_flag = '1' AND o.delivery_qty = o.order_qty);
COMMENT ON VIEW public.order_delivery_qty_check IS
  '注文の納品数と納品合計の食い違い（完納扱いを除く）。照合用の読み取り専用ビュー';

-- 委託加工: purchase_orders.delivered_qty と deliveries の合計（完了フラグ completed_flag = 'E'）
\c subcon_manager
\ir ../product_master/00_require_dev.sql
CREATE OR REPLACE VIEW public.purchase_order_delivery_qty_check AS
SELECT
  p.purchase_order_id,
  p.order_date::date AS order_date,
  p.product_no,
  p.supplier_code,
  p.order_qty,
  p.delivered_qty AS stored_delivered_qty,
  coalesce(d.delivery_total, 0) AS delivery_total,
  p.delivery_balance,
  p.completed_flag
FROM public.purchase_orders p
LEFT JOIN (
  SELECT purchase_order_id, sum(delivery_qty) AS delivery_total FROM public.deliveries GROUP BY purchase_order_id
) d USING (purchase_order_id)
WHERE coalesce(p.delivered_qty, 0) <> coalesce(d.delivery_total, 0)
  AND NOT (p.completed_flag = 'E' AND p.delivered_qty = p.order_qty);
COMMENT ON VIEW public.purchase_order_delivery_qty_check IS
  '発注の納入済数と納入合計の食い違い（完納扱いを除く）。照合用の読み取り専用ビュー';
