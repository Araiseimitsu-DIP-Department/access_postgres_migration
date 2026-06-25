-- jucyu_manager 運用に必要なスキーマ拡張（Access 忠実移行・データ投入後に適用）
-- 由来: jucyu_manager/backend/sql/001_schema.sql, 002_deliveries_delivery_id_serial.sql

-- orders
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders (order_date);
CREATE INDEX IF NOT EXISTS idx_orders_due_date ON orders (due_date);
CREATE INDEX IF NOT EXISTS idx_orders_sales_month ON orders (sales_month);
CREATE INDEX IF NOT EXISTS idx_orders_code ON orders (code);
CREATE INDEX IF NOT EXISTS idx_orders_sales_rep ON orders (sales_rep);
CREATE INDEX IF NOT EXISTS idx_orders_order_no ON orders (order_no);
CREATE INDEX IF NOT EXISTS idx_orders_product_no ON orders (product_no);
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders (order_id);

-- customer_master
CREATE INDEX IF NOT EXISTS idx_customer_master_customer ON customer_master (customer);
CREATE INDEX IF NOT EXISTS idx_customer_master_kana ON customer_master (kana);

-- product_master
CREATE INDEX IF NOT EXISTS idx_product_master_name ON product_master (product_name);
CREATE INDEX IF NOT EXISTS idx_product_master_customer_name ON product_master (customer_name);

-- deliveries: シーケンス・索引
CREATE SEQUENCE IF NOT EXISTS deliveries_delivery_id_seq;
ALTER TABLE deliveries ALTER COLUMN delivery_id SET DEFAULT nextval('deliveries_delivery_id_seq');

DO $$
DECLARE
    max_id BIGINT;
BEGIN
    SELECT MAX(delivery_id) INTO max_id FROM deliveries;
    IF max_id IS NOT NULL THEN
        PERFORM setval('deliveries_delivery_id_seq', max_id, TRUE);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_deliveries_order_id ON deliveries (order_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_billing_month ON deliveries (billing_month);
CREATE INDEX IF NOT EXISTS idx_deliveries_delivery_date ON deliveries (delivery_date);
CREATE INDEX IF NOT EXISTS idx_deliveries_ship_date ON deliveries (ship_date);

-- delivery_notes
CREATE SEQUENCE IF NOT EXISTS delivery_notes_id_seq;
ALTER TABLE delivery_notes ALTER COLUMN id SET DEFAULT nextval('delivery_notes_id_seq');

DO $$
DECLARE
    max_id BIGINT;
BEGIN
    SELECT MAX(id) INTO max_id FROM delivery_notes;
    IF max_id IS NOT NULL THEN
        PERFORM setval('delivery_notes_id_seq', max_id, TRUE);
    END IF;
END $$;

-- delivery_note_data
CREATE SEQUENCE IF NOT EXISTS delivery_note_data_id_seq;
ALTER TABLE delivery_note_data ALTER COLUMN id SET DEFAULT nextval('delivery_note_data_id_seq');

DO $$
DECLARE
    max_id BIGINT;
BEGIN
    SELECT MAX(id) INTO max_id FROM delivery_note_data;
    IF max_id IS NOT NULL THEN
        PERFORM setval('delivery_note_data_id_seq', max_id, TRUE);
    END IF;
END $$;

-- invoices
CREATE SEQUENCE IF NOT EXISTS invoices_id_seq;
ALTER TABLE invoices ALTER COLUMN id SET DEFAULT nextval('invoices_id_seq');

DO $$
DECLARE
    max_id BIGINT;
BEGIN
    SELECT MAX(id) INTO max_id FROM invoices;
    IF max_id IS NOT NULL THEN
        PERFORM setval('invoices_id_seq', max_id, TRUE);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_invoices_code_month ON invoices (code, billing_month);

-- invoices_temp
CREATE SEQUENCE IF NOT EXISTS invoices_temp_id_seq;
ALTER TABLE invoices_temp ALTER COLUMN id SET DEFAULT nextval('invoices_temp_id_seq');

DO $$
DECLARE
    max_id BIGINT;
BEGIN
    SELECT MAX(id) INTO max_id FROM invoices_temp;
    IF max_id IS NOT NULL THEN
        PERFORM setval('invoices_temp_id_seq', max_id, TRUE);
    END IF;
END $$;

-- billing_amounts
CREATE SEQUENCE IF NOT EXISTS billing_amounts_id_seq;
ALTER TABLE billing_amounts ALTER COLUMN id SET DEFAULT nextval('billing_amounts_id_seq');

DO $$
DECLARE
    max_id BIGINT;
BEGIN
    SELECT MAX(id) INTO max_id FROM billing_amounts;
    IF max_id IS NOT NULL THEN
        PERFORM setval('billing_amounts_id_seq', max_id, TRUE);
    END IF;
END $$;

-- billing_amounts_settlement
CREATE SEQUENCE IF NOT EXISTS billing_amounts_settlement_id_seq;
ALTER TABLE billing_amounts_settlement ALTER COLUMN id SET DEFAULT nextval('billing_amounts_settlement_id_seq');

DO $$
DECLARE
    max_id BIGINT;
BEGIN
    SELECT MAX(id) INTO max_id FROM billing_amounts_settlement;
    IF max_id IS NOT NULL THEN
        PERFORM setval('billing_amounts_settlement_id_seq', max_id, TRUE);
    END IF;
END $$;

-- duplicate_customers
CREATE SEQUENCE IF NOT EXISTS duplicate_customers_id_seq;
ALTER TABLE duplicate_customers ALTER COLUMN id SET DEFAULT nextval('duplicate_customers_id_seq');

DO $$
DECLARE
    max_id BIGINT;
BEGIN
    SELECT MAX(id) INTO max_id FROM duplicate_customers;
    IF max_id IS NOT NULL THEN
        PERFORM setval('duplicate_customers_id_seq', max_id, TRUE);
    END IF;
END $$;
