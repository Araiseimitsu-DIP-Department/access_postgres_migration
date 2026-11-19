-- 07_subcon_product_master_full_up.sql で退避した表を public.product_master_full に戻す（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d subcon_manager -f 07_subcon_product_master_full_down.sql
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

DO $$
BEGIN
  IF to_regclass('normalization_backup.product_master_full_unused') IS NOT NULL THEN
    ALTER TABLE normalization_backup.product_master_full_unused RENAME TO product_master_full;
    ALTER TABLE normalization_backup.product_master_full SET SCHEMA public;
  END IF;
END $$;

COMMIT;
