-- incoming_material_inspection 運用に必要なスキーマ拡張（Access 忠実移行・データ投入後に適用）
-- 由来: incoming_material_inspection/migrations/postgres/001_initial_schema.sql

-- BOOLEAN デフォルト（新規 INSERT 時の Access 相当初期値）
ALTER TABLE legacy_inspection_data ALTER COLUMN confirmed SET DEFAULT FALSE;
ALTER TABLE inspection_data ALTER COLUMN confirmed SET DEFAULT FALSE;
ALTER TABLE material_delivery_temp ALTER COLUMN registered_flag SET DEFAULT FALSE;

-- legacy_inspection_data 主キー
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'legacy_inspection_data_pkey'
          AND conrelid = 'legacy_inspection_data'::regclass
    ) THEN
        ALTER TABLE legacy_inspection_data ADD PRIMARY KEY (id);
    END IF;
END $$;

-- material_delivery_history 主キー
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'material_delivery_history_pkey'
          AND conrelid = 'material_delivery_history'::regclass
    ) THEN
        ALTER TABLE material_delivery_history ADD PRIMARY KEY (id);
    END IF;
END $$;

-- inspection_data 主キー
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'inspection_data_pkey'
          AND conrelid = 'inspection_data'::regclass
    ) THEN
        ALTER TABLE inspection_data ADD PRIMARY KEY (id);
    END IF;
END $$;

-- 入荷日検索（日付別一覧）
CREATE INDEX IF NOT EXISTS idx_material_delivery_history_receipt_date
    ON material_delivery_history (receipt_date);

-- 購入ID による検査データ upsert（purchase_id が NULL の行は対象外）
CREATE UNIQUE INDEX IF NOT EXISTS idx_inspection_data_purchase_id
    ON inspection_data (purchase_id)
    WHERE purchase_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_legacy_inspection_data_purchase_id
    ON legacy_inspection_data (purchase_id)
    WHERE purchase_id IS NOT NULL;
