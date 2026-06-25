-- 材料入庫管理台帳兼ミルシート管理表DB -> PostgreSQL (material_millsheet_manager)
-- Access 忠実移行の参照 DDL。運用向け主キー・索引は schema_app_patches.sql を適用する。

CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE IF NOT EXISTS cross_aggregation (
    id BIGINT NOT NULL,
    supplier_code VARCHAR(2),
    supplier_name VARCHAR(20),
    purchase_month VARCHAR(4),
    amount NUMERIC
);

CREATE TABLE IF NOT EXISTS app_control (
    id BIGINT NOT NULL,
    write_folder VARCHAR(255),
    purchase_month_from VARCHAR(4),
    purchase_month_to VARCHAR(4)
);

CREATE TABLE IF NOT EXISTS remarks_master (
    code VARCHAR(2),
    remark_text VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS legacy_inspection_data (
    id BIGINT NOT NULL,
    purchase_id INTEGER,
    dimension_1 DOUBLE PRECISION,
    dimension_2 DOUBLE PRECISION,
    judgment_result VARCHAR(3),
    remarks VARCHAR(10),
    inspector_name VARCHAR(8),
    confirmed BOOLEAN NOT NULL,
    content VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS material_delivery_temp (
    id BIGINT NOT NULL,
    receipt_date TIMESTAMP,
    slip_date TIMESTAMP,
    category_code VARCHAR(1),
    supplier_code VARCHAR(2),
    supplier_name VARCHAR(20),
    purchase_month VARCHAR(4),
    material_kind VARCHAR(15),
    delivered_item VARCHAR(50),
    size VARCHAR(10),
    weight DOUBLE PRECISION,
    unit_price INTEGER,
    amount NUMERIC,
    lot_no VARCHAR(50),
    used_product_no VARCHAR(30),
    customer_name VARCHAR(20),
    specification VARCHAR(30),
    remarks VARCHAR(30),
    registered_flag BOOLEAN NOT NULL,
    receipt_location VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS material_delivery_history (
    id BIGINT NOT NULL,
    receipt_date TIMESTAMP,
    slip_date TIMESTAMP,
    category_code VARCHAR(1),
    supplier_code VARCHAR(2),
    supplier_name VARCHAR(20),
    purchase_month VARCHAR(4),
    material_kind VARCHAR(15),
    delivered_item VARCHAR(50),
    size VARCHAR(10),
    weight DOUBLE PRECISION,
    unit_price INTEGER,
    amount NUMERIC,
    lot_no VARCHAR(50),
    used_product_no VARCHAR(30),
    customer_name VARCHAR(20),
    specification VARCHAR(30),
    remarks VARCHAR(30),
    receipt_location VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS material_delivery_history_before_change (
    id BIGINT NOT NULL,
    receipt_date TIMESTAMP,
    slip_date TIMESTAMP,
    category_code VARCHAR(1),
    supplier_code VARCHAR(2),
    supplier_name VARCHAR(20),
    purchase_month VARCHAR(4),
    material_kind VARCHAR(15),
    delivered_item VARCHAR(50),
    size VARCHAR(10),
    weight DOUBLE PRECISION,
    unit_price INTEGER,
    amount INTEGER,
    lot_no VARCHAR(50),
    used_product_no VARCHAR(30),
    customer_name VARCHAR(20),
    specification VARCHAR(30),
    remarks VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS material_types (
    material_type VARCHAR(20),
    symbol VARCHAR(1)
);

CREATE TABLE IF NOT EXISTS inspection_data (
    id BIGINT NOT NULL,
    purchase_id INTEGER,
    dim1_left_max DOUBLE PRECISION,
    dim1_left_min DOUBLE PRECISION,
    dim1_center_max DOUBLE PRECISION,
    dim1_center_min DOUBLE PRECISION,
    dim1_right_max DOUBLE PRECISION,
    dim1_right_min DOUBLE PRECISION,
    dim2_left_max DOUBLE PRECISION,
    dim2_left_min DOUBLE PRECISION,
    dim2_center_max DOUBLE PRECISION,
    dim2_center_min DOUBLE PRECISION,
    dim2_right_max DOUBLE PRECISION,
    dim2_right_min DOUBLE PRECISION,
    judgment_result VARCHAR(3),
    bending VARCHAR(2),
    scratch VARCHAR(2),
    dirt VARCHAR(2),
    inspector_name VARCHAR(8),
    confirmed BOOLEAN NOT NULL,
    content VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS inspectors (
    code VARCHAR(2),
    inspector_name VARCHAR(8)
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_code VARCHAR(2),
    supplier_name VARCHAR(20),
    closing_day VARCHAR(2),
    calculation_method VARCHAR(1)
);
