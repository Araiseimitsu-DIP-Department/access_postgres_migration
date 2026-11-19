-- secondary_process_record_db の未使用の複製マスタを退避する（開発DB専用）。
--   product_master: どのアプリからも参照されていない移行時の製品マスタ（旧品番の情報を含むため残す）
--   machine_master: アプリは号機を現品票の文字として扱い、この表を参照しない（機械以外のコードも含む94件）
-- 削除はせず normalization_backup.*_unused に移すだけ。戻す場合は 05_secondary_process_down.sql。
-- 実行: psql -h 192.168.1.120 -U postgres -d secondary_process_record_db -f 05_secondary_process_up.sql
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

CREATE SCHEMA IF NOT EXISTS normalization_backup;

DO $$
DECLARE
  name text;
BEGIN
  FOREACH name IN ARRAY ARRAY['product_master', 'machine_master'] LOOP
    IF to_regclass('public.' || name) IS NOT NULL THEN
      EXECUTE format('ALTER TABLE public.%I SET SCHEMA normalization_backup', name);
      EXECUTE format('ALTER TABLE normalization_backup.%I RENAME TO %I', name, name || '_unused');
    END IF;
  END LOOP;
END $$;

COMMIT;
