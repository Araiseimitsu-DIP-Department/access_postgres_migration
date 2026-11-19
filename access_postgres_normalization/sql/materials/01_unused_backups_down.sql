-- 01_unused_backups_up.sql で退避した表を元の名前・スキーマに戻す（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f 01_unused_backups_down.sql
\set ON_ERROR_STOP on

\ir ../product_master/00_require_dev.sql
BEGIN;
DO $$
BEGIN
  IF to_regclass('normalization_backup.material_delivery_history_before_change_unused') IS NOT NULL THEN
    ALTER TABLE normalization_backup.material_delivery_history_before_change_unused
      RENAME TO material_delivery_history_before_change;
    ALTER TABLE normalization_backup.material_delivery_history_before_change SET SCHEMA public;
  END IF;
END $$;
COMMIT;

\c material_scheduling
\ir ../product_master/00_require_dev.sql
BEGIN;
DO $$
BEGIN
  IF to_regclass('normalization_backup.production_releases_backup_unused') IS NOT NULL THEN
    ALTER TABLE normalization_backup.production_releases_backup_unused RENAME TO production_releases_backup;
    ALTER TABLE normalization_backup.production_releases_backup SET SCHEMA public;
  END IF;
END $$;
COMMIT;
