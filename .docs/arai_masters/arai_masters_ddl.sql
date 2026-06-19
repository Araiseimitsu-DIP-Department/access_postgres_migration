-- PostgreSQL DDL（arai_masters データベース）
-- スキーマ: config.env の POSTGRES_SCHEMA（未指定時は public）
-- 接続先 DB: config.env の POSTGRES_DB（推奨名: arai_masters）
-- 元データ: 製品マスター.xls（c:\Users\seika\Desktop\cursor\製品マスター.xls）
--
-- 本ファイルは既存 DB（2026-06-19 時点）の構造定義を文書化したものです。
-- 型・制約は PostgreSQL arai_masters の現行スキーマに準拠しています。
-- DB・データは既に存在するため、通常は再実行不要です。
--
-- テーブル一覧（public スキーマ）:
--   material_category   … 材料識別マスタ（14行）  シート: 材料識別
--   outsource_master    … 加工業者マスタ（73行）  シート: 加工業者マスター
--   machine_master      … 機械マスタ（61行）      シート: 機械ﾏｽﾀｰ
--   product_master      … 製品マスタ（1,563行）   シート: 製品マスター
--
-- 投入スクリプト:
--   create_material_category.py / create_outsource_master.py / create_machine_master.py
--   create_product_master.py

-- ---------------------------------------------------------------------------
-- material_category（材料識別）
-- ---------------------------------------------------------------------------

CREATE TABLE material_category (
    category_no INTEGER NOT NULL PRIMARY KEY,
    category_name VARCHAR(10)
);

COMMENT ON TABLE material_category IS '材料識別マスタ（元: 製品マスター.xls シート「材料識別」）';
COMMENT ON COLUMN material_category.category_no IS '元Excel列 J / ヘッダ: （1行目未定義・識別番号）。主キー';
COMMENT ON COLUMN material_category.category_name IS '元Excel列 I / ヘッダ: （1行目未定義・材料識別名）';

-- ---------------------------------------------------------------------------
-- outsource_master（加工業者マスター）
-- ---------------------------------------------------------------------------

CREATE TABLE outsource_master (
    id VARCHAR(5) NOT NULL PRIMARY KEY,
    mark VARCHAR(5) UNIQUE,
    name VARCHAR(20)
);

COMMENT ON TABLE outsource_master IS '加工業者マスタ（元: 製品マスター.xls シート「加工業者マスター」）';
COMMENT ON COLUMN outsource_master.id IS '元Excel列 A / ヘッダ: 加工業者ID';
COMMENT ON COLUMN outsource_master.mark IS '元Excel列 B / ヘッダ: 加工業者記号';
COMMENT ON COLUMN outsource_master.name IS '元Excel列 C / ヘッダ: 加工業者名';

-- ---------------------------------------------------------------------------
-- machine_master（機械ﾏｽﾀｰ）
-- ---------------------------------------------------------------------------

CREATE TABLE machine_master (
    machine_id VARCHAR(3) NOT NULL PRIMARY KEY,
    machine_sort VARCHAR(4) UNIQUE,
    machine_no VARCHAR(5) UNIQUE,
    model VARCHAR(10),
    spec VARCHAR(10),
    manufacturer VARCHAR(20),
    serial_no VARCHAR(10) UNIQUE,
    machine_operator VARCHAR(10)
);

COMMENT ON TABLE machine_master IS '機械マスタ（元: 製品マスター.xls シート「機械ﾏｽﾀｰ」）';
COMMENT ON COLUMN machine_master.machine_id IS '元Excel列 I / ヘッダ: 機械ID';
COMMENT ON COLUMN machine_master.machine_sort IS '元Excel列 J / ヘッダ: 識別順';
COMMENT ON COLUMN machine_master.machine_no IS '元Excel列 K / ヘッダ: 新号機';
COMMENT ON COLUMN machine_master.model IS '元Excel列 L / ヘッダ: 機種';
COMMENT ON COLUMN machine_master.spec IS '元Excel列 M / ヘッダ: 仕様';
COMMENT ON COLUMN machine_master.manufacturer IS '元Excel列 N / ヘッダ: ﾒｰｶｰ';
COMMENT ON COLUMN machine_master.serial_no IS '元Excel列 U / ヘッダ: ｼﾘｱﾙNO';
COMMENT ON COLUMN machine_master.machine_operator IS '元Excel列 O / ヘッダ: 担当者';

-- ---------------------------------------------------------------------------
-- product_master（製品マスター）
-- ---------------------------------------------------------------------------

CREATE TABLE product_master (
    id VARCHAR(7) NOT NULL,
    product_no VARCHAR(30),
    alt_management_no VARCHAR(30),
    product_name VARCHAR(30),
    customer_name VARCHAR(30),
    next_process VARCHAR(10),
    process_code VARCHAR(4),
    closing_day VARCHAR(2),
    sales_staff VARCHAR(6),
    material_and_diameter VARCHAR(80),
    product_length NUMERIC(15, 2),
    cutoff NUMERIC(15, 2),
    total_length_with_cutoff NUMERIC(15, 2),
    previous_machining_seconds NUMERIC(15, 2),
    daily_output NUMERIC(15, 2),
    pickup_qty NUMERIC(15, 2),
    unit_price NUMERIC(15, 2),
    material_cost NUMERIC(15, 2),
    machining_cost NUMERIC(15, 2),
    processing_cost NUMERIC(15, 2),
    handling_precautions VARCHAR(20),
    instruction_sheet_flag VARCHAR(1),
    remarks_and_conditions VARCHAR(50),
    pre_inspection VARCHAR(1),
    secondary_process_dest VARCHAR(20),
    lead_time INTEGER,
    wash_step_1 VARCHAR(10),
    process_2 VARCHAR(30),
    process_2_vendor VARCHAR(20),
    process_2_total VARCHAR(2),
    process_3 VARCHAR(30),
    process_3_vendor VARCHAR(20),
    process_3_total VARCHAR(2),
    process_4 VARCHAR(30),
    process_4_vendor VARCHAR(20),
    process_4_total VARCHAR(2),
    process_5 VARCHAR(30),
    process_5_vendor VARCHAR(20),
    process_5_total VARCHAR(2),
    process_6 VARCHAR(30),
    process_6_vendor VARCHAR(20),
    process_6_total VARCHAR(2),
    process_7 VARCHAR(30),
    process_7_vendor VARCHAR(20),
    process_7_total VARCHAR(2),
    process_8 VARCHAR(30),
    process_8_vendor VARCHAR(20),
    process_8_total VARCHAR(2),
    process_9 VARCHAR(30),
    process_9_vendor VARCHAR(20),
    process_9_total VARCHAR(2),
    packing_style VARCHAR(30),
    packing_spec VARCHAR(30),
    destination_spec VARCHAR(30),
    external_machining_cost NUMERIC(15, 2),
    delivery_staff VARCHAR(6),
    material_identification VARCHAR(2),
    category VARCHAR(5),
    usage_info VARCHAR(255),
    remarks VARCHAR(255),
    iatf_target VARCHAR(1),
    instruction_sheet_flag_bu VARCHAR(1),
    call_code VARCHAR(7),
    unit_weight NUMERIC(15, 2),
    PRIMARY KEY (id)
);

COMMENT ON TABLE product_master IS '製品マスター（元: 製品マスター Excel シート）';

COMMENT ON COLUMN product_master.id IS '元Excel列 BU / ヘッダ: ID';
COMMENT ON COLUMN product_master.product_no IS '元Excel列 A / ヘッダ: 製品番号';
COMMENT ON COLUMN product_master.alt_management_no IS '元Excel列 B / ヘッダ: 別管理番号';
COMMENT ON COLUMN product_master.product_name IS '元Excel列 C / ヘッダ: 製品名';
COMMENT ON COLUMN product_master.customer_name IS '元Excel列 D / ヘッダ: 客先名';
COMMENT ON COLUMN product_master.next_process IS '元Excel列 E / ヘッダ: 次工程';
COMMENT ON COLUMN product_master.process_code IS '元Excel列 F / ヘッダ: コード';
COMMENT ON COLUMN product_master.closing_day IS '元Excel列 G / ヘッダ: 締日';
COMMENT ON COLUMN product_master.sales_staff IS '元Excel列 H / ヘッダ: 営業　　　担当';
COMMENT ON COLUMN product_master.material_and_diameter IS '元Excel列 I / ヘッダ: 材質＆材料径';
COMMENT ON COLUMN product_master.product_length IS '元Excel列 J / ヘッダ: 製品全長';
COMMENT ON COLUMN product_master.cutoff IS '元Excel列 K / ヘッダ: 突切';
COMMENT ON COLUMN product_master.total_length_with_cutoff IS '元Excel列 L / ヘッダ: 全長＋突切り幅';
COMMENT ON COLUMN product_master.previous_machining_seconds IS '元Excel列 M / ヘッダ: 前回　　　加工秒数';
COMMENT ON COLUMN product_master.daily_output IS '元Excel列 N / ヘッダ: 日産';
COMMENT ON COLUMN product_master.pickup_qty IS '元Excel列 O / ヘッダ: 取り数';
COMMENT ON COLUMN product_master.unit_price IS '元Excel列 P / ヘッダ: 単価';
COMMENT ON COLUMN product_master.material_cost IS '元Excel列 Q / ヘッダ: 材料費';
COMMENT ON COLUMN product_master.machining_cost IS '元Excel列 R / ヘッダ: 加工費';
COMMENT ON COLUMN product_master.processing_cost IS '元Excel列 S / ヘッダ: 処理費';
COMMENT ON COLUMN product_master.handling_precautions IS '元Excel列 T / ヘッダ: 製品取扱注意事項';
COMMENT ON COLUMN product_master.instruction_sheet_flag IS '元Excel列 U / ヘッダ: 指示書　有無';
COMMENT ON COLUMN product_master.remarks_and_conditions IS '元Excel列 V / ヘッダ: 備考　、条件　等　';
COMMENT ON COLUMN product_master.pre_inspection IS '元Excel列 W / ヘッダ: 前検';
COMMENT ON COLUMN product_master.secondary_process_dest IS '元Excel列 X / ヘッダ: 二次工程先';
COMMENT ON COLUMN product_master.lead_time IS '元Excel列 AI / ヘッダ: L/T';
COMMENT ON COLUMN product_master.wash_step_1 IS '元Excel列 AJ / ヘッダ: 洗浄①';
COMMENT ON COLUMN product_master.process_2 IS '元Excel列 AK / ヘッダ: 工程②';
COMMENT ON COLUMN product_master.process_2_vendor IS '元Excel列 AL / ヘッダ: 処理先（工程②）';
COMMENT ON COLUMN product_master.process_2_total IS '元Excel列 AM / ヘッダ: 工程②集計';
COMMENT ON COLUMN product_master.process_3 IS '元Excel列 AO / ヘッダ: 工程③';
COMMENT ON COLUMN product_master.process_3_vendor IS '元Excel列 AP / ヘッダ: 処理先（工程③）';
COMMENT ON COLUMN product_master.process_3_total IS '元Excel列 AQ / ヘッダ: 工程③集計';
COMMENT ON COLUMN product_master.process_4 IS '元Excel列 AS / ヘッダ: 工程④';
COMMENT ON COLUMN product_master.process_4_vendor IS '元Excel列 AT / ヘッダ: 処理先（工程④）';
COMMENT ON COLUMN product_master.process_4_total IS '元Excel列 AU / ヘッダ: 工程④集計';
COMMENT ON COLUMN product_master.process_5 IS '元Excel列 AW / ヘッダ: 工程⑤';
COMMENT ON COLUMN product_master.process_5_vendor IS '元Excel列 AX / ヘッダ: 処理先（工程⑤）';
COMMENT ON COLUMN product_master.process_5_total IS '元Excel列 AY / ヘッダ: 工程⑤集計';
COMMENT ON COLUMN product_master.process_6 IS '元Excel列 BA / ヘッダ: 工程⑥';
COMMENT ON COLUMN product_master.process_6_vendor IS '元Excel列 BB / ヘッダ: 処理先（工程⑥）';
COMMENT ON COLUMN product_master.process_6_total IS '元Excel列 BC / ヘッダ: 工程⑥集計';
COMMENT ON COLUMN product_master.process_7 IS '元Excel列 BE / ヘッダ: 工程⑦';
COMMENT ON COLUMN product_master.process_7_vendor IS '元Excel列 BF / ヘッダ: 処理先（工程⑦）';
COMMENT ON COLUMN product_master.process_7_total IS '元Excel列 BG / ヘッダ: 工程⑦集計';
COMMENT ON COLUMN product_master.process_8 IS '元Excel列 BI / ヘッダ: 工程⑧';
COMMENT ON COLUMN product_master.process_8_vendor IS '元Excel列 BJ / ヘッダ: 処理先（工程⑧）';
COMMENT ON COLUMN product_master.process_8_total IS '元Excel列 BK / ヘッダ: 工程⑧集計';
COMMENT ON COLUMN product_master.process_9 IS '元Excel列 BM / ヘッダ: 工程⑨';
COMMENT ON COLUMN product_master.process_9_vendor IS '元Excel列 BN / ヘッダ: 処理先（工程⑨）';
COMMENT ON COLUMN product_master.process_9_total IS '元Excel列 BO / ヘッダ: 工程⑨集計';
COMMENT ON COLUMN product_master.packing_style IS '元Excel列 BQ / ヘッダ: 梱包形態';
COMMENT ON COLUMN product_master.packing_spec IS '元Excel列 BR / ヘッダ: 梱包仕様';
COMMENT ON COLUMN product_master.destination_spec IS '元Excel列 BS / ヘッダ: 送り先指定';
COMMENT ON COLUMN product_master.external_machining_cost IS '元Excel列 BT / ヘッダ: 外部委託加工費';
COMMENT ON COLUMN product_master.delivery_staff IS '元Excel列 BV / ヘッダ: 納期　　　担当';
COMMENT ON COLUMN product_master.material_identification IS '元Excel列 BX / ヘッダ: 材料　　　　識別';
COMMENT ON COLUMN product_master.category IS '元Excel列 BY / ヘッダ: 区分';
COMMENT ON COLUMN product_master.usage_info IS '元Excel列 BZ / ヘッダ: 用途　情報';
COMMENT ON COLUMN product_master.remarks IS '元Excel列 CA / ヘッダ: 備考';
COMMENT ON COLUMN product_master.iatf_target IS '元Excel列 CB / ヘッダ: IATF   対象';
COMMENT ON COLUMN product_master.instruction_sheet_flag_bu IS '元Excel列 CC / ヘッダ: 指示書　有無BU';
COMMENT ON COLUMN product_master.call_code IS '元Excel列 CD / ヘッダ: 呼出ｺｰﾄﾞ';
COMMENT ON COLUMN product_master.unit_weight IS '元Excel列 CE / ヘッダ: 製品単重　　(g)';
