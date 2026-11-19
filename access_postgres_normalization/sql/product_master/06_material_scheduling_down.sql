-- 06_material_scheduling_up.sql を取り消し、退避した表を元に戻す（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_scheduling -f 06_material_scheduling_down.sql
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

DROP VIEW IF EXISTS public.machine_master;
ALTER TABLE normalization_backup.machine_master_before_fdw RENAME TO machine_master;
ALTER TABLE normalization_backup.machine_master SET SCHEMA public;
ALTER TABLE normalization_backup.suppliers_unused RENAME TO suppliers;
ALTER TABLE normalization_backup.suppliers SET SCHEMA public;
DROP FOREIGN TABLE IF EXISTS arai.machine_master;
DROP SCHEMA IF EXISTS arai;
DROP SERVER IF EXISTS arai_masters_srv CASCADE;

COMMIT;
