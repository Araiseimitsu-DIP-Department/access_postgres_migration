-- 材料入庫・生産リリースの、どのアプリからも参照されていないバックアップ表を退避する（開発DB専用）。
--   material_millsheet_manager.material_delivery_history_before_change:
--     2018-04 時点の材料納入履歴の写し（2,677件）。2,669件は現行と同一、差は lot_no 6件・category_code 1件、現行にない行が1件（id 2644）。
--   material_scheduling.production_releases_backup:
--     2022-09〜11 時点の生産リリースの写し（30,193件）。現行との差は工程終了日の時刻（現行は日付のみ）、完了 35件、号機 1件。
-- 削除はせず normalization_backup.*_unused に移すだけ。戻す場合は 01_unused_backups_down.sql。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f 01_unused_backups_up.sql
\set ON_ERROR_STOP on

\ir ../product_master/00_require_dev.sql
BEGIN;
CREATE SCHEMA IF NOT EXISTS normalization_backup;
DO $$
BEGIN
  IF to_regclass('public.material_delivery_history_before_change') IS NOT NULL THEN
    ALTER TABLE public.material_delivery_history_before_change SET SCHEMA normalization_backup;
    ALTER TABLE normalization_backup.material_delivery_history_before_change
      RENAME TO material_delivery_history_before_change_unused;
  END IF;
END $$;
COMMIT;

\c material_scheduling
\ir ../product_master/00_require_dev.sql
BEGIN;
CREATE SCHEMA IF NOT EXISTS normalization_backup;
DO $$
BEGIN
  IF to_regclass('public.production_releases_backup') IS NOT NULL THEN
    ALTER TABLE public.production_releases_backup SET SCHEMA normalization_backup;
    ALTER TABLE normalization_backup.production_releases_backup RENAME TO production_releases_backup_unused;
  END IF;
END $$;
COMMIT;
