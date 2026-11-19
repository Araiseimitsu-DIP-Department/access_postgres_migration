-- order_management.product_master を arai_masters.product_master の互換ビューに置き換える。
-- 実行: psql -h 192.168.1.120 -d order_management -v devpw=<開発DBパスワード> -f 02_order_management_up.sql
-- 既存の表は normalization_backup.product_master_before_fdw に移して残す。戻す場合は 02_order_management_down.sql。
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE SCHEMA IF NOT EXISTS arai;
CREATE SCHEMA IF NOT EXISTS normalization_backup;

CREATE SERVER IF NOT EXISTS arai_masters_srv FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host '192.168.1.120', port '5432', dbname 'arai_masters', application_name 'order_management_fdw');
CREATE USER MAPPING IF NOT EXISTS FOR PUBLIC SERVER arai_masters_srv OPTIONS (user 'postgres', password :'devpw');

-- 受注管理の画面から登録した品番は、管理表のA番号と重ならない J 番号で採番する（6桁はQRの製品IDと同じ桁数）
CREATE SEQUENCE IF NOT EXISTS arai.product_master_local_id_seq;

CREATE FOREIGN TABLE IF NOT EXISTS arai.product_master (
  id varchar(7) NOT NULL DEFAULT ('J' || lpad(nextval('arai.product_master_local_id_seq')::text, 5, '0')),
  product_no varchar(30),
  alt_management_no varchar(30),
  product_name varchar(30),
  customer_name varchar(30),
  next_process varchar(255),
  process_code varchar(4),
  closing_day varchar(2),
  sales_staff varchar(6),
  unit_price numeric(15, 2)
) SERVER arai_masters_srv OPTIONS (schema_name 'public', table_name 'product_master');

-- 既存の表が残っている場合だけ退避する（再実行時は何もしない）
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
             WHERE n.nspname = 'public' AND c.relname = 'product_master' AND c.relkind = 'r') THEN
    ALTER TABLE public.product_master SET SCHEMA normalization_backup;
    ALTER TABLE normalization_backup.product_master RENAME TO product_master_before_fdw;
  END IF;
END $$;

-- 旧表と同じ列名・列順。code と person_in_charge は arai の列名に対応付ける。
CREATE OR REPLACE VIEW public.product_master AS
SELECT
  product_no,
  alt_management_no,
  product_name,
  customer_name,
  next_process,
  process_code AS code,
  closing_day,
  sales_staff AS person_in_charge,
  unit_price
FROM arai.product_master
WHERE btrim(coalesce(product_no, '')) <> '';

COMMIT;
