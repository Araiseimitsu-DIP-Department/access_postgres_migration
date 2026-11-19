-- secondary_process_record_db.product_master（どのアプリからも参照されていない移行時の複製）を退避する（開発DB専用）。
-- 削除はせず normalization_backup.product_master_unused に移すだけ。戻す場合は 05_secondary_process_down.sql。
-- 実行: psql -h 192.168.1.120 -U postgres -d secondary_process_record_db -f 05_secondary_process_up.sql
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

CREATE SCHEMA IF NOT EXISTS normalization_backup;

DO $$
BEGIN
  IF to_regclass('public.product_master') IS NOT NULL THEN
    ALTER TABLE public.product_master SET SCHEMA normalization_backup;
    ALTER TABLE normalization_backup.product_master RENAME TO product_master_unused;
  END IF;
END $$;

COMMIT;
