-- 主キーのないマスタ・台帳に主キーを追加する（開発DB専用）。対象と選定基準は 01_targets.sql。
-- 各DBで、先に空欄・重複を確認し、あれば変更せずに中止する。既に主キーがある表は飛ばす（再実行可）。
-- order_management.customer_master の全列が空の行（業務上の意味がなく、主キーの妨げになる）は
-- normalization_backup.customer_master_blank_rows へ移してから主キーを付ける。
-- 戻す場合は 01_primary_keys_down.sql。
-- 実行: psql -h 192.168.1.120 -U postgres -d appearance_inspection_db -f 01_primary_keys_up.sql
\set ON_ERROR_STOP on
\ir 01_targets.sql

\c appearance_inspection_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_appearance_inspection_db';
\ir 00_add_primary_keys.sql
COMMIT;

\c delivery_label_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_delivery_label_db';
\ir 00_add_primary_keys.sql
COMMIT;

\c material_millsheet_manager
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_material_millsheet_manager';
\ir 00_add_primary_keys.sql
COMMIT;

\c material_scheduling
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_material_scheduling';
\ir 00_add_primary_keys.sql
COMMIT;

\c order_management
\ir ../product_master/00_require_dev.sql
BEGIN;
CREATE SCHEMA IF NOT EXISTS normalization_backup;
CREATE TABLE IF NOT EXISTS normalization_backup.customer_master_blank_rows (LIKE public.customer_master);
COMMENT ON TABLE normalization_backup.customer_master_blank_rows IS
  '01_primary_keys_up.sql で客先マスタから外した、全列が空の行（戻し用）';
WITH removed AS (
  DELETE FROM public.customer_master c
  WHERE NOT EXISTS (SELECT 1 FROM json_each_text(row_to_json(c)) v WHERE nullif(btrim(v.value), '') IS NOT NULL)
  RETURNING c.*
)
INSERT INTO normalization_backup.customer_master_blank_rows SELECT * FROM removed;
SET LOCAL normalization.pk_targets = :'pk_order_management';
\ir 00_add_primary_keys.sql
-- 主キーと同じ列の索引は不要になる
DROP INDEX IF EXISTS public.idx_orders_order_id;
COMMIT;

\c order_performance_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_order_performance_db';
\ir 00_add_primary_keys.sql
COMMIT;

\c pingauge_management_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_pingauge_management_db';
\ir 00_add_primary_keys.sql
COMMIT;

\c secondary_process_record_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_secondary_process_record_db';
\ir 00_add_primary_keys.sql
COMMIT;

\c shipping_inspection_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_shipping_inspection_db';
\ir 00_add_primary_keys.sql
COMMIT;
