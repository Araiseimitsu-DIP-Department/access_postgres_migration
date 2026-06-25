-- material_management_system 運用に必要なスキーマ拡張（Access 忠実移行・データ投入後に適用）
-- 由来: material_management_system/backend/app/db/migrations/001_init.sql, 002, 003

-- Excel 管理表マスター同期向け列拡張（002 / 003 相当）
ALTER TABLE management_sheet_master
    ALTER COLUMN next_process TYPE VARCHAR(255);
ALTER TABLE management_sheet_master
    ALTER COLUMN material_diameter TYPE VARCHAR(255);

-- app_control 主キー
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'app_control_pkey'
          AND conrelid = 'app_control'::regclass
    ) THEN
        ALTER TABLE app_control ADD PRIMARY KEY (id);
    END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS idx_management_sheet_master_product_code
    ON management_sheet_master (product_code)
    WHERE product_code IS NOT NULL;

-- production_orders: シーケンス・主キー・索引・BOOLEAN デフォルト
CREATE SEQUENCE IF NOT EXISTS production_orders_id_seq OWNED BY production_orders.id;
ALTER TABLE production_orders ALTER COLUMN id SET DEFAULT nextval('production_orders_id_seq');

DO $$
DECLARE
    max_id BIGINT;
BEGIN
    SELECT MAX(id) INTO max_id FROM production_orders;
    IF max_id IS NOT NULL THEN
        PERFORM setval('production_orders_id_seq', max_id, TRUE);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'production_orders_pkey'
          AND conrelid = 'production_orders'::regclass
    ) THEN
        ALTER TABLE production_orders ADD PRIMARY KEY (id);
    END IF;
END $$;

ALTER TABLE production_orders ALTER COLUMN exp_flag SET DEFAULT FALSE;
ALTER TABLE production_orders ALTER COLUMN sales_approved SET DEFAULT FALSE;
ALTER TABLE production_orders ALTER COLUMN imp_flag SET DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_production_orders_part_no ON production_orders (part_no);
CREATE INDEX IF NOT EXISTS idx_production_orders_order_date ON production_orders (order_date);
CREATE INDEX IF NOT EXISTS idx_production_orders_imp_date ON production_orders (imp_date);

-- set_schedules: シーケンス・主キー・索引
CREATE SEQUENCE IF NOT EXISTS set_schedules_id_seq OWNED BY set_schedules.id;
ALTER TABLE set_schedules ALTER COLUMN id SET DEFAULT nextval('set_schedules_id_seq');

DO $$
DECLARE
    max_id BIGINT;
BEGIN
    SELECT MAX(id) INTO max_id FROM set_schedules;
    IF max_id IS NOT NULL THEN
        PERFORM setval('set_schedules_id_seq', max_id, TRUE);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'set_schedules_pkey'
          AND conrelid = 'set_schedules'::regclass
    ) THEN
        ALTER TABLE set_schedules ADD PRIMARY KEY (id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_set_schedules_part_no ON set_schedules (part_no);
