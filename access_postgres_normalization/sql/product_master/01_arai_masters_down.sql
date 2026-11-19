-- 01_arai_masters_up.sql を取り消す（開発DB専用）。変更履歴表は記録保全のため残す。
-- 実行: psql -h 192.168.1.120 -d arai_masters -f 01_arai_masters_down.sql
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

DROP TRIGGER IF EXISTS trg_product_master_history ON public.product_master;
DROP TRIGGER IF EXISTS trg_product_master_touch ON public.product_master;
DROP TRIGGER IF EXISTS trg_product_master_guard ON public.product_master;
DROP FUNCTION IF EXISTS public.product_master_guard_product_no();
DROP FUNCTION IF EXISTS public.product_no_in_use(text);
DROP FUNCTION IF EXISTS public.product_master_record_history();
DROP FUNCTION IF EXISTS public.product_master_touch();
DROP FUNCTION IF EXISTS public.product_master_actor();
DROP SCHEMA IF EXISTS product_refs CASCADE;
DROP SERVER IF EXISTS order_management_srv CASCADE;
DROP SERVER IF EXISTS delivery_label_srv CASCADE;
DROP SERVER IF EXISTS subcon_manager_srv CASCADE;
ALTER TABLE public.product_master DROP COLUMN IF EXISTS updated_by, DROP COLUMN IF EXISTS updated_at;
DROP INDEX IF EXISTS public.ix_product_master_product_no;
DROP INDEX IF EXISTS public.uq_product_master_product_no;

COMMIT;
