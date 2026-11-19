-- arai_masters.product_master を全アプリ共通の製品マスタとして保護する。
-- 実行: psql -h 192.168.1.120 -d arai_masters -v devpw=<開発DBパスワード> -f 01_arai_masters_up.sql
-- 再実行しても同じ状態になる。戻す場合は 01_arai_masters_down.sql を使う。
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

-- A. 品番の一意性。空欄の確保済みID行は対象外とする。
CREATE UNIQUE INDEX IF NOT EXISTS uq_product_master_product_no
  ON public.product_master (btrim(product_no))
  WHERE btrim(product_no) <> '';
-- 外部テーブル経由の検索（WHERE product_no = $1）は式索引を使えないため、列そのものにも索引を作る
CREATE INDEX IF NOT EXISTS ix_product_master_product_no ON public.product_master (product_no);

-- B. 最終更新の記録と変更履歴
ALTER TABLE public.product_master
  ADD COLUMN IF NOT EXISTS updated_at timestamptz,
  ADD COLUMN IF NOT EXISTS updated_by text;

CREATE TABLE IF NOT EXISTS public.product_master_history (
  history_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  product_id varchar(7) NOT NULL,
  operation varchar(6) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
  changed_at timestamptz NOT NULL DEFAULT now(),
  changed_by text NOT NULL,
  old_values jsonb,
  new_values jsonb
);
CREATE INDEX IF NOT EXISTS ix_product_master_history_product
  ON public.product_master_history (product_id, changed_at);

-- 外部テーブル経由の更新は application_name で接続元DBを識別する
CREATE OR REPLACE FUNCTION public.product_master_actor() RETURNS text
LANGUAGE sql STABLE AS $$
  SELECT session_user || '@' || coalesce(nullif(current_setting('application_name', true), ''), 'unknown')
$$;

CREATE OR REPLACE FUNCTION public.product_master_touch() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := now();
  NEW.updated_by := public.product_master_actor();
  RETURN NEW;
END $$;

CREATE OR REPLACE FUNCTION public.product_master_record_history() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO public.product_master_history (product_id, operation, changed_by, old_values, new_values)
  VALUES (
    CASE WHEN TG_OP = 'DELETE' THEN OLD.id ELSE NEW.id END,
    TG_OP,
    public.product_master_actor(),
    CASE WHEN TG_OP <> 'INSERT' THEN to_jsonb(OLD) END,
    CASE WHEN TG_OP <> 'DELETE' THEN to_jsonb(NEW) END
  );
  RETURN NULL;  -- AFTER トリガーのため戻り値は使われない
END $$;

-- C. 使用中の品番の変更・削除を止めるため、取引データを外部テーブルで照会する
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE SCHEMA IF NOT EXISTS product_refs;

CREATE SERVER IF NOT EXISTS order_management_srv FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host '192.168.1.120', port '5432', dbname 'order_management', application_name 'arai_masters_fdw');
CREATE SERVER IF NOT EXISTS delivery_label_srv FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host '192.168.1.120', port '5432', dbname 'delivery_label_db', application_name 'arai_masters_fdw');
CREATE SERVER IF NOT EXISTS subcon_manager_srv FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host '192.168.1.120', port '5432', dbname 'subcon_manager', application_name 'arai_masters_fdw');

CREATE USER MAPPING IF NOT EXISTS FOR PUBLIC SERVER order_management_srv OPTIONS (user 'postgres', password :'devpw');
CREATE USER MAPPING IF NOT EXISTS FOR PUBLIC SERVER delivery_label_srv OPTIONS (user 'postgres', password :'devpw');
CREATE USER MAPPING IF NOT EXISTS FOR PUBLIC SERVER subcon_manager_srv OPTIONS (user 'postgres', password :'devpw');

-- 委託加工の product_master は共通マスタの複製で利用実績ではないため、発注・納入を照会する
CREATE FOREIGN TABLE IF NOT EXISTS product_refs.orders (product_no varchar(30))
  SERVER order_management_srv OPTIONS (schema_name 'public', table_name 'orders');
CREATE FOREIGN TABLE IF NOT EXISTS product_refs.delivery_label_history (product_code varchar(30))
  SERVER delivery_label_srv OPTIONS (schema_name 'public', table_name 'delivery_label_history');
CREATE FOREIGN TABLE IF NOT EXISTS product_refs.subcon_purchase_orders (product_no varchar(30))
  SERVER subcon_manager_srv OPTIONS (schema_name 'public', table_name 'purchase_orders');
CREATE FOREIGN TABLE IF NOT EXISTS product_refs.subcon_deliveries (product_no varchar(30))
  SERVER subcon_manager_srv OPTIONS (schema_name 'public', table_name 'deliveries');

CREATE OR REPLACE FUNCTION public.product_no_in_use(target text) RETURNS boolean
LANGUAGE sql STABLE AS $$
  SELECT EXISTS (SELECT 1 FROM product_refs.orders WHERE product_no = target)
      OR EXISTS (SELECT 1 FROM product_refs.delivery_label_history WHERE product_code = target)
      OR EXISTS (SELECT 1 FROM product_refs.subcon_purchase_orders WHERE product_no = target)
      OR EXISTS (SELECT 1 FROM product_refs.subcon_deliveries WHERE product_no = target)
$$;
-- 旧版で参照していた委託加工の製品マスタ（複製）は使わない
DROP FOREIGN TABLE IF EXISTS product_refs.subcon_product_master;

-- SQLSTATE PM001 はアプリ側で「使用中の品番」として案内する
CREATE OR REPLACE FUNCTION public.product_master_guard_product_no() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  old_no text := btrim(coalesce(OLD.product_no, ''));
  renamed boolean := TG_OP = 'DELETE' OR btrim(coalesce(NEW.product_no, '')) <> old_no;
BEGIN
  IF old_no <> '' AND renamed AND public.product_no_in_use(old_no) THEN
    RAISE EXCEPTION '製品番号 % は受注・現品票・委託加工で使用中のため変更・削除できません', old_no
      USING ERRCODE = 'PM001';
  END IF;
  RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END $$;

DROP TRIGGER IF EXISTS trg_product_master_guard ON public.product_master;
CREATE TRIGGER trg_product_master_guard
  BEFORE UPDATE OF product_no OR DELETE ON public.product_master
  FOR EACH ROW EXECUTE FUNCTION public.product_master_guard_product_no();

DROP TRIGGER IF EXISTS trg_product_master_touch ON public.product_master;
CREATE TRIGGER trg_product_master_touch
  BEFORE INSERT OR UPDATE ON public.product_master
  FOR EACH ROW EXECUTE FUNCTION public.product_master_touch();

DROP TRIGGER IF EXISTS trg_product_master_history ON public.product_master;
CREATE TRIGGER trg_product_master_history
  AFTER INSERT OR UPDATE OR DELETE ON public.product_master
  FOR EACH ROW EXECUTE FUNCTION public.product_master_record_history();

COMMIT;
