-- 受注実績（order_performance）と受注管理（order_management.orders）の食い違いを一覧する照合用ビューを追加する（開発DB専用）。
-- どちらの表も変更しない。受注実績は受注管理から写したあと独自に修正・取消する台帳のため、差分は確認用の一覧として扱う。
-- 実行: psql -h 192.168.1.120 -U postgres -d order_performance_db -v devpw=<開発DBパスワード> -f 01_order_reconciliation_up.sql
-- 戻す場合は 01_order_reconciliation_down.sql。
\set ON_ERROR_STOP on

BEGIN;

\ir ../product_master/00_require_dev.sql

CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE SCHEMA IF NOT EXISTS order_management;

CREATE SERVER IF NOT EXISTS order_management_srv FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host '192.168.1.120', port '5432', dbname 'order_management', application_name 'order_performance_fdw');
CREATE USER MAPPING IF NOT EXISTS FOR PUBLIC SERVER order_management_srv OPTIONS (user 'postgres', password :'devpw');

CREATE FOREIGN TABLE IF NOT EXISTS order_management.orders (
  order_id varchar(10),
  order_date timestamp,
  order_no varchar(30),
  product_no varchar(30),
  product_name varchar(30),
  customer varchar(30),
  code varchar(4),
  closing_day varchar(2),
  sales_rep varchar(6),
  sales_month integer,
  due_date timestamp,
  order_qty integer,
  unit_price numeric,
  amount integer
) SERVER order_management_srv OPTIONS (schema_name 'public', table_name 'orders');

-- 注文IDのない旧データ（2014〜2017年）は対象外。食い違いのある注文だけを返す。
CREATE OR REPLACE VIEW public.order_reconciliation AS
WITH paired AS (
  SELECT
    coalesce(m.order_id, p.order_id) AS order_id,
    m.order_id IS NOT NULL AS in_management,
    p.order_id IS NOT NULL AS in_performance,
    p.id AS performance_id,
    m.order_date AS management_order_date,
    p.order_date AS performance_order_date,
    array_remove(ARRAY[
      CASE WHEN m.order_date::date IS DISTINCT FROM p.order_date::date THEN 'order_date' END,
      CASE WHEN btrim(m.order_no) IS DISTINCT FROM btrim(p.order_no) THEN 'order_no' END,
      CASE WHEN btrim(m.product_no) IS DISTINCT FROM btrim(p.product_no) THEN 'product_no' END,
      CASE WHEN btrim(m.product_name) IS DISTINCT FROM btrim(p.product_name) THEN 'product_name' END,
      CASE WHEN btrim(m.customer) IS DISTINCT FROM btrim(p.customer) THEN 'customer' END,
      CASE WHEN btrim(m.code) IS DISTINCT FROM btrim(p.code) THEN 'code' END,
      CASE WHEN btrim(m.closing_day) IS DISTINCT FROM btrim(p.closing_day) THEN 'closing_day' END,
      CASE WHEN btrim(m.sales_rep) IS DISTINCT FROM btrim(p.sales_rep) THEN 'sales_rep' END,
      CASE WHEN m.sales_month IS DISTINCT FROM p.sales_month THEN 'sales_month' END,
      CASE WHEN m.due_date::date IS DISTINCT FROM p.due_date::date THEN 'due_date' END,
      CASE WHEN m.order_qty IS DISTINCT FROM p.order_qty THEN 'order_qty' END,
      CASE WHEN m.unit_price IS DISTINCT FROM p.unit_price THEN 'unit_price' END,
      CASE WHEN m.amount IS DISTINCT FROM p.amount THEN 'amount' END
    ], NULL) AS different_columns
  FROM order_management.orders m
  FULL JOIN (SELECT * FROM public.order_performance WHERE btrim(coalesce(order_id, '')) <> '') p
    ON p.order_id = m.order_id
)
SELECT
  order_id,
  CASE
    WHEN NOT in_performance THEN '受注管理のみ'
    WHEN NOT in_management THEN '受注実績のみ'
    ELSE '内容の食い違い'
  END AS status,
  performance_id,
  coalesce(management_order_date, performance_order_date)::date AS order_date,
  different_columns
FROM paired
WHERE NOT in_management OR NOT in_performance OR cardinality(different_columns) > 0;

COMMENT ON VIEW public.order_reconciliation IS
  '受注管理と受注実績の食い違い（片側のみ・項目の差）。照合用の読み取り専用ビュー';

COMMIT;
