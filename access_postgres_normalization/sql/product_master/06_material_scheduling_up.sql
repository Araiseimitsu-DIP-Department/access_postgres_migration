-- material_scheduling の機械マスタを arai_masters.machine_master の互換ビューに置き換え、未使用の仕入先表を退避する（開発DB専用）。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_scheduling -v devpw=<開発DBパスワード> -f 06_material_scheduling_up.sql
-- 旧表は normalization_backup に移して残す。戻す場合は 06_material_scheduling_down.sql。
-- 機械マスタの利用元は production_progress_sheet（機番一覧・存在確認）のみ。suppliers はどのアプリからも参照されていない
-- （材料仕入先の管理元は material_millsheet_manager.suppliers）。
\set ON_ERROR_STOP on

BEGIN;

\ir 00_require_dev.sql

CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE SCHEMA IF NOT EXISTS arai;
CREATE SCHEMA IF NOT EXISTS normalization_backup;

CREATE SERVER IF NOT EXISTS arai_masters_srv FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host '192.168.1.120', port '5432', dbname 'arai_masters', application_name 'material_scheduling_fdw');
CREATE USER MAPPING IF NOT EXISTS FOR PUBLIC SERVER arai_masters_srv OPTIONS (user 'postgres', password :'devpw');

CREATE FOREIGN TABLE IF NOT EXISTS arai.machine_master (
  machine_id varchar(3),
  machine_sort varchar(4),
  machine_no varchar(5),
  model varchar(10),
  spec varchar(10),
  serial_no varchar(10)
) SERVER arai_masters_srv OPTIONS (schema_name 'public', table_name 'machine_master');

-- 既存の表が残っている場合だけ退避する（再実行時は何もしない）
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
             WHERE n.nspname = 'public' AND c.relname = 'machine_master' AND c.relkind = 'r') THEN
    ALTER TABLE public.machine_master SET SCHEMA normalization_backup;
    ALTER TABLE normalization_backup.machine_master RENAME TO machine_master_before_fdw;
  END IF;
  IF to_regclass('public.suppliers') IS NOT NULL THEN
    ALTER TABLE public.suppliers SET SCHEMA normalization_backup;
    ALTER TABLE normalization_backup.suppliers RENAME TO suppliers_unused;
  END IF;
END $$;

-- 旧表と同じ列名・列順。model_type は機種の末尾の数値（例: L12(L16) → 16）で、旧表59台すべてと一致する。
CREATE OR REPLACE VIEW public.machine_master AS
SELECT
  serial_no,
  machine_no,
  model AS machine_model,
  spec AS specification,
  substring(model FROM '(\d+)\D*$')::varchar(2) AS model_type,
  machine_sort AS sort_key
FROM arai.machine_master;

COMMIT;
