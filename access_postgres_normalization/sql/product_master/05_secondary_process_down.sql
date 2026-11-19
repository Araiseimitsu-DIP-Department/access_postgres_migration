-- 05_secondary_process_up.sql で退避した product_master を元の場所に戻す（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d secondary_process_record_db -f 05_secondary_process_down.sql
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

ALTER TABLE normalization_backup.product_master_unused RENAME TO product_master;
ALTER TABLE normalization_backup.product_master SET SCHEMA public;

COMMIT;
