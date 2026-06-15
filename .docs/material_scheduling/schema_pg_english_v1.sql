-- セット予定材料管理DB -> PostgreSQL (material_scheduling)

CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE IF NOT EXISTS "app_control" (
    "id" BIGINT NOT NULL,
    "management_sheet_updated_at" TIMESTAMP,
    "set_schedule_sheet_updated_at" TIMESTAMP,
    "save_folder" VARCHAR(100)
);
COMMENT ON TABLE "app_control" IS '元Accessテーブル: t_コントロール';
COMMENT ON COLUMN "app_control"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "app_control"."management_sheet_updated_at" IS '元Accessカラム: 管理表更新日時';
COMMENT ON COLUMN "app_control"."set_schedule_sheet_updated_at" IS '元Accessカラム: セット予定表更新日時';
COMMENT ON COLUMN "app_control"."save_folder" IS '元Accessカラム: 保存フォルダ';

CREATE TABLE IF NOT EXISTS "set_schedules" (
    "id" BIGINT NOT NULL,
    "set_schedule_date" TIMESTAMP,
    "machine_no" VARCHAR(4),
    "serial_no" VARCHAR(10),
    "part_no" VARCHAR(30),
    "quantity" INTEGER,
    "minimum_required_qty" INTEGER,
    "production_order_qty" INTEGER,
    "material_diameter" VARCHAR(40),
    "material_bars_used" INTEGER,
    "previous_cycle_seconds" INTEGER,
    "previous_daily_output" DOUBLE PRECISION,
    "planned_process_days" DOUBLE PRECISION,
    "process_end_date" TIMESTAMP,
    "management_no" VARCHAR(10),
    "delivery_info" TIMESTAMP,
    "setup_operator" VARCHAR(8),
    "remarks" VARCHAR(50)
);
COMMENT ON TABLE "set_schedules" IS '元Accessテーブル: t_セット予定';
COMMENT ON COLUMN "set_schedules"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "set_schedules"."set_schedule_date" IS '元Accessカラム: セット予定日';
COMMENT ON COLUMN "set_schedules"."machine_no" IS '元Accessカラム: 機械NO';
COMMENT ON COLUMN "set_schedules"."serial_no" IS '元Accessカラム: シリアルNO';
COMMENT ON COLUMN "set_schedules"."part_no" IS '元Accessカラム: 品番';
COMMENT ON COLUMN "set_schedules"."quantity" IS '元Accessカラム: 数量';
COMMENT ON COLUMN "set_schedules"."minimum_required_qty" IS '元Accessカラム: 必要最低数';
COMMENT ON COLUMN "set_schedules"."production_order_qty" IS '元Accessカラム: 生産発注数';
COMMENT ON COLUMN "set_schedules"."material_diameter" IS '元Accessカラム: 材質材料径';
COMMENT ON COLUMN "set_schedules"."material_bars_used" IS '元Accessカラム: 材料使用本数';
COMMENT ON COLUMN "set_schedules"."previous_cycle_seconds" IS '元Accessカラム: 前回秒数';
COMMENT ON COLUMN "set_schedules"."previous_daily_output" IS '元Accessカラム: 前回日産';
COMMENT ON COLUMN "set_schedules"."planned_process_days" IS '元Accessカラム: 加工予定日数';
COMMENT ON COLUMN "set_schedules"."process_end_date" IS '元Accessカラム: 加工終了日';
COMMENT ON COLUMN "set_schedules"."management_no" IS '元Accessカラム: 管理No';
COMMENT ON COLUMN "set_schedules"."delivery_info" IS '元Accessカラム: 納期情報';
COMMENT ON COLUMN "set_schedules"."setup_operator" IS '元Accessカラム: セット者';
COMMENT ON COLUMN "set_schedules"."remarks" IS '元Accessカラム: 備考';

CREATE TABLE IF NOT EXISTS "chuck_master" (
    "id" BIGINT NOT NULL,
    "model_type" VARCHAR(2),
    "category" VARCHAR(1),
    "size" VARCHAR(20),
    "quantity" INTEGER,
    "in_use_count" INTEGER
);
COMMENT ON TABLE "chuck_master" IS '元Accessテーブル: t_チャックマスタ';
COMMENT ON COLUMN "chuck_master"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "chuck_master"."model_type" IS '元Accessカラム: 型';
COMMENT ON COLUMN "chuck_master"."category" IS '元Accessカラム: 種別';
COMMENT ON COLUMN "chuck_master"."size" IS '元Accessカラム: サイズ';
COMMENT ON COLUMN "chuck_master"."quantity" IS '元Accessカラム: 数量';
COMMENT ON COLUMN "chuck_master"."in_use_count" IS '元Accessカラム: 使用中';

CREATE TABLE IF NOT EXISTS "production_pauses" (
    "id" INTEGER,
    "machine_no" VARCHAR(4),
    "part_no" VARCHAR(30),
    "pause_date" TIMESTAMP
);
COMMENT ON TABLE "production_pauses" IS '元Accessテーブル: t_一時停止';
COMMENT ON COLUMN "production_pauses"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "production_pauses"."machine_no" IS '元Accessカラム: 機械NO';
COMMENT ON COLUMN "production_pauses"."part_no" IS '元Accessカラム: 品番';
COMMENT ON COLUMN "production_pauses"."pause_date" IS '元Accessカラム: 停止日';

CREATE TABLE IF NOT EXISTS "inbound_email_master" (
    "supplier_code" VARCHAR(2),
    "supplier_name" VARCHAR(20),
    "contact_to" VARCHAR(8),
    "address_to" VARCHAR(50),
    "contact_cc" VARCHAR(8),
    "address_cc" VARCHAR(50)
);
COMMENT ON TABLE "inbound_email_master" IS '元Accessテーブル: t_受信メールマスタ';
COMMENT ON COLUMN "inbound_email_master"."supplier_code" IS '元Accessカラム: 納入業者コード';
COMMENT ON COLUMN "inbound_email_master"."supplier_name" IS '元Accessカラム: 納入業者名';
COMMENT ON COLUMN "inbound_email_master"."contact_to" IS '元Accessカラム: 担当者To';
COMMENT ON COLUMN "inbound_email_master"."address_to" IS '元Accessカラム: アドレスTo';
COMMENT ON COLUMN "inbound_email_master"."contact_cc" IS '元Accessカラム: 担当者Cc';
COMMENT ON COLUMN "inbound_email_master"."address_cc" IS '元Accessカラム: アドレスCc';

CREATE TABLE IF NOT EXISTS "sales_rep_master" (
    "id" VARCHAR(2),
    "staff_name" VARCHAR(5),
    "display_flag" VARCHAR(1)
);
COMMENT ON TABLE "sales_rep_master" IS '元Accessテーブル: t_営業担当マスタ';
COMMENT ON COLUMN "sales_rep_master"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "sales_rep_master"."staff_name" IS '元Accessカラム: 担当者名';
COMMENT ON COLUMN "sales_rep_master"."display_flag" IS '元Accessカラム: 表示フラグ';

CREATE TABLE IF NOT EXISTS "legacy_machine_ids" (
    "machine_unit" VARCHAR(4),
    "machine_id" VARCHAR(4)
);
COMMENT ON TABLE "legacy_machine_ids" IS '元Accessテーブル: t_旧機械ID';
COMMENT ON COLUMN "legacy_machine_ids"."machine_unit" IS '元Accessカラム: 号機';
COMMENT ON COLUMN "legacy_machine_ids"."machine_id" IS '元Accessカラム: 機械ID';

CREATE TABLE IF NOT EXISTS "material_orders" (
    "id" BIGINT NOT NULL,
    "management_no" VARCHAR(10),
    "part_no" VARCHAR(30),
    "product_name" VARCHAR(30),
    "customer_name" VARCHAR(30),
    "quantity" INTEGER,
    "material_diameter" VARCHAR(40),
    "arrangement_date" TIMESTAMP,
    "delivery_date" TIMESTAMP,
    "required_bars" DOUBLE PRECISION,
    "ordered_bars" DOUBLE PRECISION,
    "unit" VARCHAR(1),
    "allocated_bars" DOUBLE PRECISION,
    "delivered_qty" INTEGER,
    "remaining_receipt_qty" INTEGER,
    "yield_rate" DOUBLE PRECISION,
    "delivery_response_date" TIMESTAMP,
    "vendor_code" VARCHAR(2),
    "vendor_name" VARCHAR(20),
    "arranged_flag" VARCHAR(1),
    "purchase_order_printed_flag" VARCHAR(1),
    "material_receipt_completed_flag" VARCHAR(1)
);
COMMENT ON TABLE "material_orders" IS '元Accessテーブル: t_材料管理';
COMMENT ON COLUMN "material_orders"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "material_orders"."management_no" IS '元Accessカラム: 管理NO';
COMMENT ON COLUMN "material_orders"."part_no" IS '元Accessカラム: 品番';
COMMENT ON COLUMN "material_orders"."product_name" IS '元Accessカラム: 製品名';
COMMENT ON COLUMN "material_orders"."customer_name" IS '元Accessカラム: 客先名';
COMMENT ON COLUMN "material_orders"."quantity" IS '元Accessカラム: 数量';
COMMENT ON COLUMN "material_orders"."material_diameter" IS '元Accessカラム: 材質材料径';
COMMENT ON COLUMN "material_orders"."arrangement_date" IS '元Accessカラム: 手配日';
COMMENT ON COLUMN "material_orders"."delivery_date" IS '元Accessカラム: 納期';
COMMENT ON COLUMN "material_orders"."required_bars" IS '元Accessカラム: 必要本数';
COMMENT ON COLUMN "material_orders"."ordered_bars" IS '元Accessカラム: 発注本数';
COMMENT ON COLUMN "material_orders"."unit" IS '元Accessカラム: 単位';
COMMENT ON COLUMN "material_orders"."allocated_bars" IS '元Accessカラム: 引当本数';
COMMENT ON COLUMN "material_orders"."delivered_qty" IS '元Accessカラム: 納入済数';
COMMENT ON COLUMN "material_orders"."remaining_receipt_qty" IS '元Accessカラム: 入荷残';
COMMENT ON COLUMN "material_orders"."yield_rate" IS '元Accessカラム: 歩留';
COMMENT ON COLUMN "material_orders"."delivery_response_date" IS '元Accessカラム: 納期回答';
COMMENT ON COLUMN "material_orders"."vendor_code" IS '元Accessカラム: 発注先コード';
COMMENT ON COLUMN "material_orders"."vendor_name" IS '元Accessカラム: 発注先名';
COMMENT ON COLUMN "material_orders"."arranged_flag" IS '元Accessカラム: 手配済フラグ';
COMMENT ON COLUMN "material_orders"."purchase_order_printed_flag" IS '元Accessカラム: 注文書印刷済フラグ';
COMMENT ON COLUMN "material_orders"."material_receipt_completed_flag" IS '元Accessカラム: 材料入荷完了フラグ';

CREATE TABLE IF NOT EXISTS "material_delivery_history" (
    "id" BIGINT NOT NULL,
    "management_no" VARCHAR(10),
    "receipt_date" TIMESTAMP,
    "slip_date" TIMESTAMP,
    "category_code" VARCHAR(1),
    "supplier_code" VARCHAR(2),
    "supplier_name" VARCHAR(20),
    "purchase_month" VARCHAR(4),
    "material_kind" VARCHAR(15),
    "material_diameter" VARCHAR(40),
    "size" VARCHAR(5),
    "bar_count" DOUBLE PRECISION,
    "weight" DOUBLE PRECISION,
    "unit_price" INTEGER,
    "amount" NUMERIC,
    "lot_no" VARCHAR(30),
    "receipt_location" VARCHAR(10),
    "remarks" VARCHAR(30)
);
COMMENT ON TABLE "material_delivery_history" IS '元Accessテーブル: t_材料納入履歴';
COMMENT ON COLUMN "material_delivery_history"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "material_delivery_history"."management_no" IS '元Accessカラム: 管理NO';
COMMENT ON COLUMN "material_delivery_history"."receipt_date" IS '元Accessカラム: 入荷日';
COMMENT ON COLUMN "material_delivery_history"."slip_date" IS '元Accessカラム: 伝票日付';
COMMENT ON COLUMN "material_delivery_history"."category_code" IS '元Accessカラム: 区分';
COMMENT ON COLUMN "material_delivery_history"."supplier_code" IS '元Accessカラム: 納入業者コード';
COMMENT ON COLUMN "material_delivery_history"."supplier_name" IS '元Accessカラム: 納入業者名';
COMMENT ON COLUMN "material_delivery_history"."purchase_month" IS '元Accessカラム: 購入月';
COMMENT ON COLUMN "material_delivery_history"."material_kind" IS '元Accessカラム: 品種';
COMMENT ON COLUMN "material_delivery_history"."material_diameter" IS '元Accessカラム: 材質材料径';
COMMENT ON COLUMN "material_delivery_history"."size" IS '元Accessカラム: サイズ';
COMMENT ON COLUMN "material_delivery_history"."bar_count" IS '元Accessカラム: 本数';
COMMENT ON COLUMN "material_delivery_history"."weight" IS '元Accessカラム: 重量';
COMMENT ON COLUMN "material_delivery_history"."unit_price" IS '元Accessカラム: 単価';
COMMENT ON COLUMN "material_delivery_history"."amount" IS '元Accessカラム: 金額';
COMMENT ON COLUMN "material_delivery_history"."lot_no" IS '元Accessカラム: ロット番号';
COMMENT ON COLUMN "material_delivery_history"."receipt_location" IS '元Accessカラム: 入荷場所';
COMMENT ON COLUMN "material_delivery_history"."remarks" IS '元Accessカラム: 備考';

CREATE TABLE IF NOT EXISTS "material_types" (
    "material_type" VARCHAR(20),
    "symbol" VARCHAR(1)
);
COMMENT ON TABLE "material_types" IS '元Accessテーブル: t_材質';
COMMENT ON COLUMN "material_types"."material_type" IS '元Accessカラム: 材質';
COMMENT ON COLUMN "material_types"."symbol" IS '元Accessカラム: 記号';

CREATE TABLE IF NOT EXISTS "machine_master" (
    "serial_no" VARCHAR(10),
    "machine_no" VARCHAR(4),
    "machine_model" VARCHAR(10),
    "specification" VARCHAR(10),
    "model_type" VARCHAR(2),
    "sort_key" VARCHAR(4)
);
COMMENT ON TABLE "machine_master" IS '元Accessテーブル: t_機械マスタ';
COMMENT ON COLUMN "machine_master"."serial_no" IS '元Accessカラム: シリアルNO';
COMMENT ON COLUMN "machine_master"."machine_no" IS '元Accessカラム: 機械NO';
COMMENT ON COLUMN "machine_master"."machine_model" IS '元Accessカラム: 機種';
COMMENT ON COLUMN "machine_master"."specification" IS '元Accessカラム: 仕様';
COMMENT ON COLUMN "machine_master"."model_type" IS '元Accessカラム: 型';
COMMENT ON COLUMN "machine_master"."sort_key" IS '元Accessカラム: ソートキー';

CREATE TABLE IF NOT EXISTS "setup_operator_master" (
    "id" VARCHAR(2),
    "setup_operator_name" VARCHAR(10),
    "display_flag" VARCHAR(1)
);
COMMENT ON TABLE "setup_operator_master" IS '元Accessテーブル: t_段取り者マスタ';
COMMENT ON COLUMN "setup_operator_master"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "setup_operator_master"."setup_operator_name" IS '元Accessカラム: 段取り者';
COMMENT ON COLUMN "setup_operator_master"."display_flag" IS '元Accessカラム: 表示フラグ';

CREATE TABLE IF NOT EXISTS "general_material_master" (
    "id" BIGINT NOT NULL,
    "material_diameter" VARCHAR(40),
    "supplier_code" VARCHAR(2),
    "supplier_name" VARCHAR(20),
    "remarks" VARCHAR(10),
    "active_flag" VARCHAR(1)
);
COMMENT ON TABLE "general_material_master" IS '元Accessテーブル: t_汎用材料マスタ';
COMMENT ON COLUMN "general_material_master"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "general_material_master"."material_diameter" IS '元Accessカラム: 材質材料径';
COMMENT ON COLUMN "general_material_master"."supplier_code" IS '元Accessカラム: 納入業者コード';
COMMENT ON COLUMN "general_material_master"."supplier_name" IS '元Accessカラム: 納入業者名';
COMMENT ON COLUMN "general_material_master"."remarks" IS '元Accessカラム: 備考';
COMMENT ON COLUMN "general_material_master"."active_flag" IS '元Accessカラム: 使用フラグ';

CREATE TABLE IF NOT EXISTS "general_material_order_results" (
    "id" BIGINT NOT NULL,
    "order_date" TIMESTAMP,
    "material_diameter" VARCHAR(40),
    "supplier_code" VARCHAR(2),
    "quantity" DOUBLE PRECISION,
    "unit" VARCHAR(1),
    "delivery_date" TIMESTAMP
);
COMMENT ON TABLE "general_material_order_results" IS '元Accessテーブル: t_汎用材料発注実績';
COMMENT ON COLUMN "general_material_order_results"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "general_material_order_results"."order_date" IS '元Accessカラム: 発注日';
COMMENT ON COLUMN "general_material_order_results"."material_diameter" IS '元Accessカラム: 材質材料径';
COMMENT ON COLUMN "general_material_order_results"."supplier_code" IS '元Accessカラム: 納入業者コード';
COMMENT ON COLUMN "general_material_order_results"."quantity" IS '元Accessカラム: 数量';
COMMENT ON COLUMN "general_material_order_results"."unit" IS '元Accessカラム: 単位';
COMMENT ON COLUMN "general_material_order_results"."delivery_date" IS '元Accessカラム: 納期';

CREATE TABLE IF NOT EXISTS "purchase_order_documents" (
    "id" BIGINT NOT NULL,
    "order_vendor_code" VARCHAR(2),
    "material_table_id" INTEGER,
    "material_name" VARCHAR(40),
    "management_no" VARCHAR(10),
    "quantity" DOUBLE PRECISION,
    "unit" VARCHAR(1),
    "delivery_date" TIMESTAMP
);
COMMENT ON TABLE "purchase_order_documents" IS '元Accessテーブル: t_注文書データ';
COMMENT ON COLUMN "purchase_order_documents"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "purchase_order_documents"."order_vendor_code" IS '元Accessカラム: 発注業者コード';
COMMENT ON COLUMN "purchase_order_documents"."material_table_id" IS '元Accessカラム: 材料テーブルID';
COMMENT ON COLUMN "purchase_order_documents"."material_name" IS '元Accessカラム: 材料名';
COMMENT ON COLUMN "purchase_order_documents"."management_no" IS '元Accessカラム: 管理NO';
COMMENT ON COLUMN "purchase_order_documents"."quantity" IS '元Accessカラム: 数量';
COMMENT ON COLUMN "purchase_order_documents"."unit" IS '元Accessカラム: 単位';
COMMENT ON COLUMN "purchase_order_documents"."delivery_date" IS '元Accessカラム: 納期';

CREATE TABLE IF NOT EXISTS "production_releases" (
    "id" BIGINT NOT NULL,
    "setup_date" TIMESTAMP,
    "process_end_date" TIMESTAMP,
    "machine_no" VARCHAR(4),
    "machine_model" VARCHAR(10),
    "specification" VARCHAR(10),
    "serial_no" VARCHAR(10),
    "part_no" VARCHAR(30),
    "product_name" VARCHAR(30),
    "customer_name" VARCHAR(30),
    "quantity" INTEGER,
    "material_diameter" VARCHAR(40),
    "product_total_length" DOUBLE PRECISION,
    "cutoff_width" DOUBLE PRECISION,
    "process_seconds" INTEGER,
    "daily_output_qty" DOUBLE PRECISION,
    "dimension_setup_h" DOUBLE PRECISION,
    "planned_process_days" DOUBLE PRECISION,
    "minimum_required_qty" INTEGER,
    "management_no" VARCHAR(10),
    "delivery_info" TIMESTAMP,
    "setup_operator" VARCHAR(8),
    "process_completed_date" TIMESTAMP,
    "completion_flag" VARCHAR(1)
);
COMMENT ON TABLE "production_releases" IS '元Accessテーブル: t_生産リリース';
COMMENT ON COLUMN "production_releases"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "production_releases"."setup_date" IS '元Accessカラム: セット日';
COMMENT ON COLUMN "production_releases"."process_end_date" IS '元Accessカラム: 加工終了日';
COMMENT ON COLUMN "production_releases"."machine_no" IS '元Accessカラム: 機械NO';
COMMENT ON COLUMN "production_releases"."machine_model" IS '元Accessカラム: 機種';
COMMENT ON COLUMN "production_releases"."specification" IS '元Accessカラム: 仕様';
COMMENT ON COLUMN "production_releases"."serial_no" IS '元Accessカラム: シリアルNO';
COMMENT ON COLUMN "production_releases"."part_no" IS '元Accessカラム: 品番';
COMMENT ON COLUMN "production_releases"."product_name" IS '元Accessカラム: 製品名';
COMMENT ON COLUMN "production_releases"."customer_name" IS '元Accessカラム: 客先名';
COMMENT ON COLUMN "production_releases"."quantity" IS '元Accessカラム: 数量';
COMMENT ON COLUMN "production_releases"."material_diameter" IS '元Accessカラム: 材質材料径';
COMMENT ON COLUMN "production_releases"."product_total_length" IS '元Accessカラム: 製品全長';
COMMENT ON COLUMN "production_releases"."cutoff_width" IS '元Accessカラム: 突切り幅';
COMMENT ON COLUMN "production_releases"."process_seconds" IS '元Accessカラム: 加工秒数';
COMMENT ON COLUMN "production_releases"."daily_output_qty" IS '元Accessカラム: 日産数';
COMMENT ON COLUMN "production_releases"."dimension_setup_h" IS '元Accessカラム: 寸法出しH';
COMMENT ON COLUMN "production_releases"."planned_process_days" IS '元Accessカラム: 加工予定日数';
COMMENT ON COLUMN "production_releases"."minimum_required_qty" IS '元Accessカラム: 必要最低数';
COMMENT ON COLUMN "production_releases"."management_no" IS '元Accessカラム: 管理NO';
COMMENT ON COLUMN "production_releases"."delivery_info" IS '元Accessカラム: 納期情報';
COMMENT ON COLUMN "production_releases"."setup_operator" IS '元Accessカラム: セット者';
COMMENT ON COLUMN "production_releases"."process_completed_date" IS '元Accessカラム: 加工完了日';
COMMENT ON COLUMN "production_releases"."completion_flag" IS '元Accessカラム: 完了フラグ';

CREATE TABLE IF NOT EXISTS "production_releases_backup" (
    "id" BIGINT NOT NULL,
    "setup_date" TIMESTAMP,
    "process_end_date" TIMESTAMP,
    "machine_no" VARCHAR(4),
    "machine_model" VARCHAR(10),
    "specification" VARCHAR(10),
    "serial_no" VARCHAR(10),
    "part_no" VARCHAR(30),
    "product_name" VARCHAR(30),
    "customer_name" VARCHAR(30),
    "quantity" INTEGER,
    "material_diameter" VARCHAR(40),
    "product_total_length" DOUBLE PRECISION,
    "cutoff_width" DOUBLE PRECISION,
    "process_seconds" INTEGER,
    "daily_output_qty" DOUBLE PRECISION,
    "dimension_setup_h" DOUBLE PRECISION,
    "planned_process_days" DOUBLE PRECISION,
    "minimum_required_qty" INTEGER,
    "management_no" VARCHAR(10),
    "delivery_info" TIMESTAMP,
    "setup_operator" VARCHAR(8),
    "process_completed_date" TIMESTAMP,
    "completion_flag" VARCHAR(1)
);
COMMENT ON TABLE "production_releases_backup" IS '元Accessテーブル: t_生産リリース のコピー';
COMMENT ON COLUMN "production_releases_backup"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "production_releases_backup"."setup_date" IS '元Accessカラム: セット日';
COMMENT ON COLUMN "production_releases_backup"."process_end_date" IS '元Accessカラム: 加工終了日';
COMMENT ON COLUMN "production_releases_backup"."machine_no" IS '元Accessカラム: 機械NO';
COMMENT ON COLUMN "production_releases_backup"."machine_model" IS '元Accessカラム: 機種';
COMMENT ON COLUMN "production_releases_backup"."specification" IS '元Accessカラム: 仕様';
COMMENT ON COLUMN "production_releases_backup"."serial_no" IS '元Accessカラム: シリアルNO';
COMMENT ON COLUMN "production_releases_backup"."part_no" IS '元Accessカラム: 品番';
COMMENT ON COLUMN "production_releases_backup"."product_name" IS '元Accessカラム: 製品名';
COMMENT ON COLUMN "production_releases_backup"."customer_name" IS '元Accessカラム: 客先名';
COMMENT ON COLUMN "production_releases_backup"."quantity" IS '元Accessカラム: 数量';
COMMENT ON COLUMN "production_releases_backup"."material_diameter" IS '元Accessカラム: 材質材料径';
COMMENT ON COLUMN "production_releases_backup"."product_total_length" IS '元Accessカラム: 製品全長';
COMMENT ON COLUMN "production_releases_backup"."cutoff_width" IS '元Accessカラム: 突切り幅';
COMMENT ON COLUMN "production_releases_backup"."process_seconds" IS '元Accessカラム: 加工秒数';
COMMENT ON COLUMN "production_releases_backup"."daily_output_qty" IS '元Accessカラム: 日産数';
COMMENT ON COLUMN "production_releases_backup"."dimension_setup_h" IS '元Accessカラム: 寸法出しH';
COMMENT ON COLUMN "production_releases_backup"."planned_process_days" IS '元Accessカラム: 加工予定日数';
COMMENT ON COLUMN "production_releases_backup"."minimum_required_qty" IS '元Accessカラム: 必要最低数';
COMMENT ON COLUMN "production_releases_backup"."management_no" IS '元Accessカラム: 管理NO';
COMMENT ON COLUMN "production_releases_backup"."delivery_info" IS '元Accessカラム: 納期情報';
COMMENT ON COLUMN "production_releases_backup"."setup_operator" IS '元Accessカラム: セット者';
COMMENT ON COLUMN "production_releases_backup"."process_completed_date" IS '元Accessカラム: 加工完了日';
COMMENT ON COLUMN "production_releases_backup"."completion_flag" IS '元Accessカラム: 完了フラグ';

CREATE TABLE IF NOT EXISTS "production_orders" (
    "id" BIGINT NOT NULL,
    "order_date" TIMESTAMP,
    "export_date" TIMESTAMP,
    "part_no" VARCHAR(30),
    "product_name" VARCHAR(30),
    "customer_name" VARCHAR(30),
    "backorder_qty" INTEGER,
    "stock_qty" INTEGER,
    "order_qty" INTEGER,
    "purchase_qty" INTEGER,
    "optimal_stock_qty" INTEGER,
    "delivery_date" TIMESTAMP,
    "orderer" VARCHAR(5),
    "sales_rep" VARCHAR(5),
    "category_code" VARCHAR(4),
    "remarks" VARCHAR(15),
    "exp_flag" BOOLEAN NOT NULL,
    "sales_approved" BOOLEAN NOT NULL,
    "imp_flag" BOOLEAN NOT NULL,
    "imp_date" TIMESTAMP
);
COMMENT ON TABLE "production_orders" IS '元Accessテーブル: t_生産発注';
COMMENT ON COLUMN "production_orders"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "production_orders"."order_date" IS '元Accessカラム: 発注日';
COMMENT ON COLUMN "production_orders"."export_date" IS '元Accessカラム: 出力日';
COMMENT ON COLUMN "production_orders"."part_no" IS '元Accessカラム: 品番';
COMMENT ON COLUMN "production_orders"."product_name" IS '元Accessカラム: 製品名';
COMMENT ON COLUMN "production_orders"."customer_name" IS '元Accessカラム: 客先名';
COMMENT ON COLUMN "production_orders"."backorder_qty" IS '元Accessカラム: 受注残数';
COMMENT ON COLUMN "production_orders"."stock_qty" IS '元Accessカラム: 在庫';
COMMENT ON COLUMN "production_orders"."order_qty" IS '元Accessカラム: 受注数';
COMMENT ON COLUMN "production_orders"."purchase_qty" IS '元Accessカラム: 注文数';
COMMENT ON COLUMN "production_orders"."optimal_stock_qty" IS '元Accessカラム: 適正在庫';
COMMENT ON COLUMN "production_orders"."delivery_date" IS '元Accessカラム: 納期';
COMMENT ON COLUMN "production_orders"."orderer" IS '元Accessカラム: 発注者';
COMMENT ON COLUMN "production_orders"."sales_rep" IS '元Accessカラム: 営業担当';
COMMENT ON COLUMN "production_orders"."category_code" IS '元Accessカラム: 区分';
COMMENT ON COLUMN "production_orders"."remarks" IS '元Accessカラム: 備考';
COMMENT ON COLUMN "production_orders"."exp_flag" IS '元Accessカラム: Expフラグ';
COMMENT ON COLUMN "production_orders"."sales_approved" IS '元Accessカラム: 営業承認';
COMMENT ON COLUMN "production_orders"."imp_flag" IS '元Accessカラム: Impフラグ';
COMMENT ON COLUMN "production_orders"."imp_date" IS '元Accessカラム: Imp日';

CREATE TABLE IF NOT EXISTS "orderer_master" (
    "id" VARCHAR(2),
    "orderer_name" VARCHAR(5),
    "display_flag" VARCHAR(1)
);
COMMENT ON TABLE "orderer_master" IS '元Accessテーブル: t_発注者マスタ';
COMMENT ON COLUMN "orderer_master"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "orderer_master"."orderer_name" IS '元Accessカラム: 発注者名';
COMMENT ON COLUMN "orderer_master"."display_flag" IS '元Accessカラム: 表示フラグ';

CREATE TABLE IF NOT EXISTS "management_sheet_master" (
    "product_code" VARCHAR(30),
    "product_name" VARCHAR(30),
    "customer_name" VARCHAR(30),
    "sales_rep" VARCHAR(5),
    "material_diameter" VARCHAR(40),
    "next_process" VARCHAR(25),
    "other_conditions" VARCHAR(50),
    "previous_cycle_seconds" INTEGER,
    "previous_daily_output" DOUBLE PRECISION,
    "previous_machine_no" VARCHAR(4),
    "previous_process_date" TIMESTAMP,
    "pieces_per_set" DOUBLE PRECISION,
    "stock_location" VARCHAR(10),
    "delivery_date" TIMESTAMP,
    "backorder_qty" INTEGER,
    "stock_qty" INTEGER,
    "wip_stock_qty" INTEGER,
    "has_work_order" VARCHAR(1),
    "material_identification" INTEGER
);
COMMENT ON TABLE "management_sheet_master" IS '元Accessテーブル: t_管理表マスタ';
COMMENT ON COLUMN "management_sheet_master"."product_code" IS '元Accessカラム: 製品番号';
COMMENT ON COLUMN "management_sheet_master"."product_name" IS '元Accessカラム: 製品名';
COMMENT ON COLUMN "management_sheet_master"."customer_name" IS '元Accessカラム: 客先名';
COMMENT ON COLUMN "management_sheet_master"."sales_rep" IS '元Accessカラム: 営業担当';
COMMENT ON COLUMN "management_sheet_master"."material_diameter" IS '元Accessカラム: 材質材料径';
COMMENT ON COLUMN "management_sheet_master"."next_process" IS '元Accessカラム: 次工程';
COMMENT ON COLUMN "management_sheet_master"."other_conditions" IS '元Accessカラム: 条件他';
COMMENT ON COLUMN "management_sheet_master"."previous_cycle_seconds" IS '元Accessカラム: 前回秒数';
COMMENT ON COLUMN "management_sheet_master"."previous_daily_output" IS '元Accessカラム: 前回日産';
COMMENT ON COLUMN "management_sheet_master"."previous_machine_no" IS '元Accessカラム: 前回加工機';
COMMENT ON COLUMN "management_sheet_master"."previous_process_date" IS '元Accessカラム: 前回加工日';
COMMENT ON COLUMN "management_sheet_master"."pieces_per_set" IS '元Accessカラム: 取り数';
COMMENT ON COLUMN "management_sheet_master"."stock_location" IS '元Accessカラム: 在庫保管場所';
COMMENT ON COLUMN "management_sheet_master"."delivery_date" IS '元Accessカラム: 納期';
COMMENT ON COLUMN "management_sheet_master"."backorder_qty" IS '元Accessカラム: 受注残数';
COMMENT ON COLUMN "management_sheet_master"."stock_qty" IS '元Accessカラム: 在庫';
COMMENT ON COLUMN "management_sheet_master"."wip_stock_qty" IS '元Accessカラム: 仕掛在庫';
COMMENT ON COLUMN "management_sheet_master"."has_work_order" IS '元Accessカラム: 指示書有無';
COMMENT ON COLUMN "management_sheet_master"."material_identification" IS '元Accessカラム: 材料識別';

CREATE TABLE IF NOT EXISTS "suppliers" (
    "supplier_code" VARCHAR(2),
    "supplier_name" VARCHAR(20),
    "closing_day" VARCHAR(2),
    "calculation_method" VARCHAR(1),
    "addressee" VARCHAR(20)
);
COMMENT ON TABLE "suppliers" IS '元Accessテーブル: t_納入業者';
COMMENT ON COLUMN "suppliers"."supplier_code" IS '元Accessカラム: 納入業者コード';
COMMENT ON COLUMN "suppliers"."supplier_name" IS '元Accessカラム: 納入業者名';
COMMENT ON COLUMN "suppliers"."closing_day" IS '元Accessカラム: 締日';
COMMENT ON COLUMN "suppliers"."calculation_method" IS '元Accessカラム: 計算方法';
COMMENT ON COLUMN "suppliers"."addressee" IS '元Accessカラム: 宛名';

CREATE TABLE IF NOT EXISTS "outbound_email_master" (
    "id" BIGINT NOT NULL,
    "staff_name" VARCHAR(8),
    "email_address" VARCHAR(50),
    "password" VARCHAR(20),
    "primary_contact_flag" VARCHAR(1)
);
COMMENT ON TABLE "outbound_email_master" IS '元Accessテーブル: t_送信メールマスタ';
COMMENT ON COLUMN "outbound_email_master"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "outbound_email_master"."staff_name" IS '元Accessカラム: 担当者名';
COMMENT ON COLUMN "outbound_email_master"."email_address" IS '元Accessカラム: アドレス';
COMMENT ON COLUMN "outbound_email_master"."password" IS '元Accessカラム: パスワード';
COMMENT ON COLUMN "outbound_email_master"."primary_contact_flag" IS '元Accessカラム: 主担当フラグ';

CREATE TABLE IF NOT EXISTS "part_chuck_master" (
    "id" BIGINT NOT NULL,
    "part_no" VARCHAR(30),
    "model_type" VARCHAR(2),
    "category" VARCHAR(1),
    "size" VARCHAR(20)
);
COMMENT ON TABLE "part_chuck_master" IS '元Accessテーブル: t_部品別チャックマスタ';
COMMENT ON COLUMN "part_chuck_master"."id" IS '元Accessカラム: ID';
COMMENT ON COLUMN "part_chuck_master"."part_no" IS '元Accessカラム: 品番';
COMMENT ON COLUMN "part_chuck_master"."model_type" IS '元Accessカラム: 型';
COMMENT ON COLUMN "part_chuck_master"."category" IS '元Accessカラム: 種別';
COMMENT ON COLUMN "part_chuck_master"."size" IS '元Accessカラム: サイズ';

