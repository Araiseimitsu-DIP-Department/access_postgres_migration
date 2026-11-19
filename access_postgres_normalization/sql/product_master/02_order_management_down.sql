-- 02_order_management_up.sql を取り消し、退避した表を元に戻す（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -d order_management -f 02_order_management_down.sql
-- 切替後に受注管理で登録・変更した製品は arai_masters 側に残るため、必要に応じて手動で反映する。
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

DO $$
BEGIN
  IF to_regclass('normalization_backup.product_master_before_fdw') IS NULL THEN
    RAISE EXCEPTION '退避した表 normalization_backup.product_master_before_fdw がありません';
  END IF;
END $$;

DROP VIEW IF EXISTS public.product_master;
ALTER TABLE normalization_backup.product_master_before_fdw RENAME TO product_master;
ALTER TABLE normalization_backup.product_master SET SCHEMA public;
DROP FOREIGN TABLE IF EXISTS arai.product_master;
DROP SEQUENCE IF EXISTS arai.product_master_local_id_seq;
DROP SCHEMA IF EXISTS arai;
DROP SERVER IF EXISTS arai_masters_srv CASCADE;

COMMIT;
