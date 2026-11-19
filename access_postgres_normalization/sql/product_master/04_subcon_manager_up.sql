-- subcon_manager.product_master（arai_masters からの同期コピー）を共通製品マスタの互換ビューに置き換える。
-- 実行: psql -h 192.168.1.120 -U postgres -d subcon_manager -v devpw=<開発DBパスワード> -f 04_subcon_manager_up.sql
-- 既存の表は normalization_backup.product_master_before_fdw に移して残す。戻す場合は 04_subcon_manager_down.sql。
-- 委託加工の画面で更新した品名・次工程・担当・納期担当・外部委託加工費は arai_masters に保存され、全アプリに反映される。
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE SCHEMA IF NOT EXISTS arai;
CREATE SCHEMA IF NOT EXISTS normalization_backup;

CREATE SERVER IF NOT EXISTS arai_masters_srv FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host '192.168.1.120', port '5432', dbname 'arai_masters', application_name 'subcon_manager_fdw');
CREATE USER MAPPING IF NOT EXISTS FOR PUBLIC SERVER arai_masters_srv OPTIONS (user 'postgres', password :'devpw');

-- 委託加工では製品の新規登録をしないため、採番列（id）は持たない
CREATE FOREIGN TABLE IF NOT EXISTS arai.product_master (
  product_no varchar(30),
  product_name varchar(30),
  customer_name varchar(30),
  next_process varchar(255),
  sales_staff varchar(6),
  delivery_staff varchar(6),
  external_machining_cost numeric
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

-- 旧表と同じ列名・列順。品番・担当・納期担当・外部委託加工費は arai の列名に対応付ける。
CREATE OR REPLACE VIEW public.product_master AS
SELECT
  product_no AS product_code,
  product_name AS product_name_full,
  customer_name,
  next_process,
  sales_staff AS person_in_charge,
  delivery_staff AS due_date_person,
  external_machining_cost AS external_subcontract_cost
FROM arai.product_master
WHERE btrim(coalesce(product_no, '')) <> '';

COMMIT;
