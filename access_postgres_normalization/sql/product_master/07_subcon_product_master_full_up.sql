-- subcon_manager の空の表 product_master_full（Access「製品マスター」の移行対象外の写し、0件）を退避する（開発DB専用）。
-- 委託加工アプリは起動時に create_all を実行するため、先にアプリ側のモデル SeihinMasterFull を外しておくこと
-- （外さないと空の表が public に作り直される）。製品の正は arai_masters.product_master。
-- 削除はせず normalization_backup.product_master_full_unused に移すだけ。戻す場合は 07_subcon_product_master_full_down.sql。
-- 実行: psql -h 192.168.1.120 -U postgres -d subcon_manager -f 07_subcon_product_master_full_up.sql
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

CREATE SCHEMA IF NOT EXISTS normalization_backup;

DO $$
BEGIN
  IF to_regclass('public.product_master_full') IS NOT NULL THEN
    ALTER TABLE public.product_master_full SET SCHEMA normalization_backup;
    ALTER TABLE normalization_backup.product_master_full RENAME TO product_master_full_unused;
  END IF;
END $$;

COMMIT;
