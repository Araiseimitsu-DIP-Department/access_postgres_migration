-- 01_primary_keys_up.sql を戻す（開発DB専用）。追加した主キーを外し、orders は元の一意制約と索引、
-- customer_master は外した全列が空の行を戻す。
-- 実行: psql -h 192.168.1.120 -U postgres -d appearance_inspection_db -f 01_primary_keys_down.sql
\set ON_ERROR_STOP on
\ir 01_targets.sql

\c shipping_inspection_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_shipping_inspection_db';
\ir 00_drop_primary_keys.sql
COMMIT;

\c secondary_process_record_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_secondary_process_record_db';
\ir 00_drop_primary_keys.sql
COMMIT;

\c pingauge_management_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_pingauge_management_db';
\ir 00_drop_primary_keys.sql
COMMIT;

\c order_performance_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_order_performance_db';
\ir 00_drop_primary_keys.sql
COMMIT;

\c order_management
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_order_management';
\ir 00_drop_primary_keys.sql
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON public.orders USING btree (order_id);
DO $$
BEGIN
  IF to_regclass('normalization_backup.customer_master_blank_rows') IS NOT NULL THEN
    INSERT INTO public.customer_master SELECT * FROM normalization_backup.customer_master_blank_rows;
    DROP TABLE normalization_backup.customer_master_blank_rows;
  END IF;
END $$;
COMMIT;

\c material_scheduling
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_material_scheduling';
\ir 00_drop_primary_keys.sql
COMMIT;

\c material_millsheet_manager
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_material_millsheet_manager';
\ir 00_drop_primary_keys.sql
COMMIT;

\c delivery_label_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_delivery_label_db';
\ir 00_drop_primary_keys.sql
COMMIT;

\c appearance_inspection_db
\ir ../product_master/00_require_dev.sql
BEGIN;
SET LOCAL normalization.pk_targets = :'pk_appearance_inspection_db';
\ir 00_drop_primary_keys.sql
COMMIT;
