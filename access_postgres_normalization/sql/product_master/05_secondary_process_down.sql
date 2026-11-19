-- 05_secondary_process_up.sql で退避した表を元の場所に戻す（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d secondary_process_record_db -f 05_secondary_process_down.sql
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

DO $$
DECLARE
  name text;
BEGIN
  FOREACH name IN ARRAY ARRAY['product_master', 'machine_master'] LOOP
    IF to_regclass('normalization_backup.' || name || '_unused') IS NOT NULL THEN
      EXECUTE format('ALTER TABLE normalization_backup.%I RENAME TO %I', name || '_unused', name);
      EXECUTE format('ALTER TABLE normalization_backup.%I SET SCHEMA public', name);
    END IF;
  END LOOP;
END $$;

COMMIT;
