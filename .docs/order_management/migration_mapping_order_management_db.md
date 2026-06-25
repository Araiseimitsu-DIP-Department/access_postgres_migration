# Access → PostgreSQL 移行対応表（order_management）

## 1. 移行概要

- 対象Access DB：`C:\Users\seizo\Desktop\受注データDB.accdb`
- 移行先PostgreSQL DB：`order_management`
- 接続情報：`.env` の `DATABASE_URL` / `ACCESS_DB_PATH` を参照
- 移行日：2026-06-25 08:54:08
- 方針：受注データDB.accdb の全16テーブル・全カラムを英語スネークケースへ変換し忠実に移行

## 2. 移行対象テーブル一覧

| No | Accessオブジェクト名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | `imp管理表` | `import_management_sheet` | TABLE | 4540 | 4540 | 成功 |
| 2 | `t_かんばんマスタ` | `kanban_master` | TABLE | 1 | 1 | 成功 |
| 3 | `t_コントロール` | `app_control` | TABLE | 1 | 1 | 成功 |
| 4 | `t_プリンタ名` | `printer_names` | TABLE | 1 | 1 | 成功 |
| 5 | `t_受注` | `orders` | TABLE | 38409 | 38409 | 成功 |
| 6 | `t_営業マスタ` | `sales_rep_master` | TABLE | 6 | 6 | 成功 |
| 7 | `t_客先マスタ` | `customer_master` | TABLE | 117 | 117 | 成功 |
| 8 | `t_納品` | `deliveries` | TABLE | 42630 | 42630 | 成功 |
| 9 | `t_納品書` | `delivery_notes` | TABLE | 0 | 0 | 成功 |
| 10 | `t_納品書データ` | `delivery_note_data` | TABLE | 0 | 0 | 成功 |
| 11 | `t_製品マスタ` | `product_master` | TABLE | 1525 | 1525 | 成功 |
| 12 | `t_請求書` | `invoices` | TABLE | 229 | 229 | 成功 |
| 13 | `t_請求書Tmp` | `invoices_temp` | TABLE | 0 | 0 | 成功 |
| 14 | `t_請求金額` | `billing_amounts` | TABLE | 2072 | 2072 | 成功 |
| 15 | `t_請求金額決算` | `billing_amounts_settlement` | TABLE | 44 | 44 | 成功 |
| 16 | `t_重複客先` | `duplicate_customers` | TABLE | 11 | 11 | 成功 |

## 3. テーブル別カラム対応表

### `imp管理表` → `import_management_sheet`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID1` | COUNTER | `id1` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `ID` | VARCHAR | `id` | VARCHAR(255) | 可 |  |
| 3 | `製品番号` | VARCHAR | `product_no` | VARCHAR(255) | 可 |  |
| 4 | `別管理番号` | VARCHAR | `alt_management_no` | VARCHAR(255) | 可 |  |
| 5 | `製品名` | VARCHAR | `product_name` | VARCHAR(255) | 可 |  |
| 6 | `客先名` | VARCHAR | `customer_name` | VARCHAR(255) | 可 |  |
| 7 | `次工程` | VARCHAR | `next_process` | VARCHAR(255) | 可 |  |
| 8 | `コード` | VARCHAR | `code` | VARCHAR(255) | 可 |  |
| 9 | `締日` | VARCHAR | `closing_day` | VARCHAR(255) | 可 |  |
| 10 | `担当` | VARCHAR | `person_in_charge` | VARCHAR(255) | 可 |  |
| 11 | `材質&材料径` | VARCHAR | `material_and_diameter` | VARCHAR(255) | 可 |  |
| 12 | `納期` | VARCHAR | `due_date` | VARCHAR(255) | 可 |  |
| 13 | `受注残数` | DOUBLE | `order_balance_qty` | DOUBLE PRECISION | 可 |  |
| 14 | `在庫` | DOUBLE | `stock_qty` | DOUBLE PRECISION | 可 |  |
| 15 | `過不足数` | DOUBLE | `shortage_surplus_qty` | DOUBLE PRECISION | 可 |  |
| 16 | `フィールド15` | DOUBLE | `field_15` | DOUBLE PRECISION | 可 |  |
| 17 | `フィールド16` | DOUBLE | `field_16` | DOUBLE PRECISION | 可 |  |
| 18 | `フィールド17` | DOUBLE | `field_17` | DOUBLE PRECISION | 可 |  |
| 19 | `フィールド18` | DOUBLE | `field_18` | DOUBLE PRECISION | 可 |  |
| 20 | `フィールド19` | DOUBLE | `field_19` | DOUBLE PRECISION | 可 |  |
| 21 | `フィールド20` | DOUBLE | `field_20` | DOUBLE PRECISION | 可 |  |
| 22 | `当日完了ロット` | DOUBLE | `same_day_completed_lot` | DOUBLE PRECISION | 可 |  |
| 23 | `フィールド22` | VARCHAR | `field_22` | VARCHAR(255) | 可 |  |
| 24 | `不適合ロット数量` | DOUBLE | `nonconforming_lot_qty` | DOUBLE PRECISION | 可 |  |
| 25 | `フィールド24` | DOUBLE | `field_24` | DOUBLE PRECISION | 可 |  |
| 26 | `加工中` | VARCHAR | `in_process` | VARCHAR(255) | 可 |  |
| 27 | `機械` | VARCHAR | `machine` | VARCHAR(255) | 可 |  |
| 28 | `加工終了日` | VARCHAR | `machining_end_date` | VARCHAR(255) | 可 |  |
| 29 | `生産予定数` | VARCHAR | `planned_production_qty` | VARCHAR(255) | 可 |  |
| 30 | `セット予定日` | VARCHAR | `setup_planned_date` | VARCHAR(255) | 可 |  |
| 31 | `フィールド30` | VARCHAR | `field_30` | VARCHAR(255) | 可 |  |
| 32 | `フィールド31` | VARCHAR | `field_31` | VARCHAR(255) | 可 |  |
| 33 | `フィールド32` | VARCHAR | `field_32` | VARCHAR(255) | 可 |  |
| 34 | `前回加工` | DATETIME | `previous_machining_at` | TIMESTAMP | 可 |  |
| 35 | `フィールド34` | VARCHAR | `field_34` | VARCHAR(255) | 可 |  |
| 36 | `製品全長` | DOUBLE | `product_length` | DOUBLE PRECISION | 可 |  |
| 37 | `突切` | DOUBLE | `cutoff` | DOUBLE PRECISION | 可 |  |
| 38 | `全長＋突切り幅` | DOUBLE | `total_length_with_cutoff` | DOUBLE PRECISION | 可 |  |
| 39 | `前回　　　加工秒数` | DOUBLE | `previous_machining_seconds` | DOUBLE PRECISION | 可 |  |
| 40 | `日産` | DOUBLE | `daily_output` | DOUBLE PRECISION | 可 |  |
| 41 | `取り数` | DOUBLE | `pickup_qty` | DOUBLE PRECISION | 可 |  |
| 42 | `単価` | REAL | `unit_price` | DOUBLE PRECISION | 可 |  |
| 43 | `材料費` | DOUBLE | `material_cost` | DOUBLE PRECISION | 可 |  |
| 44 | `加工費` | DOUBLE | `machining_cost` | DOUBLE PRECISION | 可 |  |
| 45 | `備考　、条件　等` | VARCHAR | `remarks_and_conditions` | VARCHAR(255) | 可 |  |
| 46 | `L/T` | DOUBLE | `lead_time` | DOUBLE PRECISION | 可 |  |
| 47 | `指示書　有無` | VARCHAR | `instruction_sheet_flag` | VARCHAR(255) | 可 |  |
| 48 | `在庫保管場所` | VARCHAR | `stock_storage_location` | VARCHAR(255) | 可 |  |
| 49 | `備考　、条件　等　` | VARCHAR | `remarks_and_conditions_alt` | VARCHAR(255) | 可 |  |

### `t_かんばんマスタ` → `kanban_master`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 2 | `品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 3 | `客先コード` | VARCHAR | `customer_code` | VARCHAR(3) | 可 |  |
| 4 | `営業` | VARCHAR | `sales_rep_short` | VARCHAR(5) | 可 |  |
| 5 | `単価` | DOUBLE | `unit_price` | DOUBLE PRECISION | 可 |  |

### `t_コントロール` → `app_control`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `注文ID年` | VARCHAR | `order_id_year` | VARCHAR(2) | 可 |  |
| 3 | `注文ID連番` | VARCHAR | `order_id_seq` | VARCHAR(5) | 可 |  |
| 4 | `メモ` | VARCHAR | `memo` | VARCHAR(50) | 可 |  |

### `t_プリンタ名` → `printer_names`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `プリンタ` | VARCHAR | `printer_name` | VARCHAR(255) | 可 |  |

### `t_受注` → `orders`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `受注日` | DATETIME | `order_date` | TIMESTAMP | 可 |  |
| 2 | `注文番号` | VARCHAR | `order_no` | VARCHAR(25) | 可 |  |
| 3 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 4 | `品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 5 | `客先` | VARCHAR | `customer` | VARCHAR(30) | 可 |  |
| 6 | `コード` | VARCHAR | `code` | VARCHAR(3) | 可 |  |
| 7 | `締日` | VARCHAR | `closing_day` | VARCHAR(2) | 可 |  |
| 8 | `営業担当` | VARCHAR | `sales_rep` | VARCHAR(5) | 可 |  |
| 9 | `売月` | INTEGER | `sales_month` | INTEGER | 可 |  |
| 10 | `表面処理` | VARCHAR | `surface_treatment` | VARCHAR(25) | 可 |  |
| 11 | `納期` | DATETIME | `due_date` | TIMESTAMP | 可 |  |
| 12 | `注文数` | INTEGER | `order_qty` | INTEGER | 可 |  |
| 13 | `納品数` | INTEGER | `delivery_qty` | INTEGER | 可 |  |
| 14 | `注文残` | INTEGER | `order_balance` | INTEGER | 可 |  |
| 15 | `単価` | CURRENCY | `unit_price` | NUMERIC | 可 |  |
| 16 | `金額` | INTEGER | `amount` | INTEGER | 可 | AccessではINTEGER型のためNUMERICではなくINTEGERで保持 |
| 17 | `完納フラグ` | VARCHAR | `completed_flag` | VARCHAR(1) | 可 |  |
| 18 | `注文ID` | VARCHAR | `order_id` | VARCHAR(8) | 可 |  |

### `t_営業マスタ` → `sales_rep_master`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `コード` | VARCHAR | `code` | VARCHAR(2) | 可 |  |
| 2 | `営業担当` | VARCHAR | `sales_rep` | VARCHAR(5) | 可 |  |
| 3 | `在職フラグ` | VARCHAR | `active_flag` | VARCHAR(1) | 可 |  |

### `t_客先マスタ` → `customer_master`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `コード` | VARCHAR | `code` | VARCHAR(3) | 可 |  |
| 2 | `客先` | VARCHAR | `customer` | VARCHAR(30) | 可 |  |
| 3 | `かな` | VARCHAR | `kana` | VARCHAR(1) | 可 |  |
| 4 | `締日` | VARCHAR | `closing_day` | VARCHAR(2) | 可 |  |
| 5 | `納品書客名` | VARCHAR | `delivery_note_customer_name` | VARCHAR(30) | 可 |  |
| 6 | `消費税計算` | VARCHAR | `consumption_tax_calc` | VARCHAR(1) | 可 |  |
| 7 | `会社区分` | VARCHAR | `company_category` | VARCHAR(2) | 可 |  |
| 8 | `品名印刷` | VARCHAR | `product_name_print` | VARCHAR(1) | 可 |  |
| 9 | `請求書印刷` | VARCHAR | `invoice_print` | VARCHAR(1) | 可 |  |
| 10 | `営業担当` | VARCHAR | `sales_rep` | VARCHAR(5) | 可 |  |
| 11 | `金額計算` | VARCHAR | `amount_calc` | VARCHAR(1) | 可 |  |

### `t_納品` → `deliveries`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `NID` | COUNTER | `delivery_id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `注文ID` | VARCHAR | `order_id` | VARCHAR(8) | 可 |  |
| 3 | `注文番号` | VARCHAR | `order_no` | VARCHAR(30) | 可 |  |
| 4 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 5 | `納入日` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 6 | `納品数` | INTEGER | `delivery_qty` | INTEGER | 可 |  |
| 7 | `単価` | CURRENCY | `unit_price` | NUMERIC | 可 |  |
| 8 | `金額` | INTEGER | `amount` | INTEGER | 可 | AccessではINTEGER型のためNUMERICではなくINTEGERで保持 |
| 9 | `請求月` | VARCHAR | `billing_month` | VARCHAR(4) | 可 |  |
| 10 | `出荷日` | DATETIME | `ship_date` | TIMESTAMP | 可 |  |

### `t_納品書` → `delivery_notes`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `コード` | VARCHAR | `code` | VARCHAR(3) | 可 |  |
| 3 | `納入日` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 4 | `納品書客名` | VARCHAR | `delivery_note_customer_name` | VARCHAR(30) | 可 |  |
| 5 | `注文番号` | VARCHAR | `order_no` | VARCHAR(30) | 可 |  |
| 6 | `品番` | VARCHAR | `product_no` | VARCHAR(40) | 可 |  |
| 7 | `納品数` | INTEGER | `delivery_qty` | INTEGER | 可 |  |
| 8 | `単価` | CURRENCY | `unit_price` | NUMERIC | 可 |  |
| 9 | `金額` | INTEGER | `amount` | INTEGER | 可 | AccessではINTEGER型のためNUMERICではなくINTEGERで保持 |
| 10 | `摘要` | VARCHAR | `summary` | VARCHAR(30) | 可 |  |
| 11 | `会社区分` | VARCHAR | `company_category` | VARCHAR(2) | 可 |  |
| 12 | `表示順` | INTEGER | `display_order` | INTEGER | 可 |  |

### `t_納品書データ` → `delivery_note_data`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `コード` | VARCHAR | `code` | VARCHAR(3) | 可 |  |
| 3 | `納入日` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 4 | `納品書客名` | VARCHAR | `delivery_note_customer_name` | VARCHAR(30) | 可 |  |
| 5 | `注文番号` | VARCHAR | `order_no` | VARCHAR(30) | 可 |  |
| 6 | `品番` | VARCHAR | `product_no` | VARCHAR(40) | 可 |  |
| 7 | `納品数` | INTEGER | `delivery_qty` | INTEGER | 可 |  |
| 8 | `単価` | CURRENCY | `unit_price` | NUMERIC | 可 |  |
| 9 | `金額` | INTEGER | `amount` | INTEGER | 可 | AccessではINTEGER型のためNUMERICではなくINTEGERで保持 |
| 10 | `摘要` | VARCHAR | `summary` | VARCHAR(30) | 可 |  |
| 11 | `会社区分` | VARCHAR | `company_category` | VARCHAR(2) | 可 |  |
| 12 | `表示順` | INTEGER | `display_order` | INTEGER | 可 |  |

### `t_製品マスタ` → `product_master`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `製品番号` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 2 | `別管理番号` | VARCHAR | `alt_management_no` | VARCHAR(30) | 可 |  |
| 3 | `製品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 4 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 5 | `次工程` | VARCHAR | `next_process` | VARCHAR(25) | 可 |  |
| 6 | `コード` | VARCHAR | `code` | VARCHAR(3) | 可 |  |
| 7 | `締日` | VARCHAR | `closing_day` | VARCHAR(2) | 可 |  |
| 8 | `担当` | VARCHAR | `person_in_charge` | VARCHAR(5) | 可 |  |
| 9 | `単価` | CURRENCY | `unit_price` | NUMERIC | 可 |  |

### `t_請求書` → `invoices`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `請求月` | VARCHAR | `billing_month` | VARCHAR(4) | 可 |  |
| 3 | `コード` | VARCHAR | `code` | VARCHAR(3) | 可 |  |
| 4 | `納品書客名` | VARCHAR | `delivery_note_customer_name` | VARCHAR(30) | 可 |  |
| 5 | `納入日` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 6 | `注文番号` | VARCHAR | `order_no` | VARCHAR(30) | 可 |  |
| 7 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 8 | `製品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 9 | `納品数` | INTEGER | `delivery_qty` | INTEGER | 可 |  |
| 10 | `単価` | CURRENCY | `unit_price` | NUMERIC | 可 |  |
| 11 | `金額` | INTEGER | `amount` | INTEGER | 可 | AccessではINTEGER型のためNUMERICではなくINTEGERで保持 |
| 12 | `消費税額` | INTEGER | `consumption_tax_amount` | INTEGER | 可 |  |
| 13 | `備考` | VARCHAR | `remarks` | VARCHAR(20) | 可 |  |
| 14 | `消費税計算` | VARCHAR | `consumption_tax_calc` | VARCHAR(1) | 可 |  |
| 15 | `会社区分` | VARCHAR | `company_category` | VARCHAR(2) | 可 |  |

### `t_請求書Tmp` → `invoices_temp`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `請求月` | VARCHAR | `billing_month` | VARCHAR(4) | 可 |  |
| 3 | `コード` | VARCHAR | `code` | VARCHAR(3) | 可 |  |
| 4 | `納品書客名` | VARCHAR | `delivery_note_customer_name` | VARCHAR(30) | 可 |  |
| 5 | `納入日` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 6 | `注文番号` | VARCHAR | `order_no` | VARCHAR(30) | 可 |  |
| 7 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 8 | `製品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 9 | `納品数` | INTEGER | `delivery_qty` | INTEGER | 可 |  |
| 10 | `単価` | CURRENCY | `unit_price` | NUMERIC | 可 |  |
| 11 | `金額` | INTEGER | `amount` | INTEGER | 可 | AccessではINTEGER型のためNUMERICではなくINTEGERで保持 |
| 12 | `消費税額` | INTEGER | `consumption_tax_amount` | INTEGER | 可 |  |
| 13 | `備考` | VARCHAR | `remarks` | VARCHAR(20) | 可 |  |
| 14 | `消費税計算` | VARCHAR | `consumption_tax_calc` | VARCHAR(1) | 可 |  |
| 15 | `会社区分` | VARCHAR | `company_category` | VARCHAR(2) | 可 |  |

### `t_請求金額` → `billing_amounts`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `請求月` | VARCHAR | `billing_month` | VARCHAR(4) | 可 |  |
| 3 | `客先コード` | VARCHAR | `customer_code` | VARCHAR(3) | 可 |  |
| 4 | `客先` | VARCHAR | `customer` | VARCHAR(10) | 可 |  |
| 5 | `客先正式` | VARCHAR | `customer_official_name` | VARCHAR(30) | 可 |  |
| 6 | `かな` | VARCHAR | `kana` | VARCHAR(1) | 可 |  |
| 7 | `締日` | VARCHAR | `closing_day` | VARCHAR(2) | 可 |  |
| 8 | `請求額` | INTEGER | `billing_amount` | INTEGER | 可 |  |
| 9 | `消費税額` | INTEGER | `consumption_tax_amount` | INTEGER | 可 |  |

### `t_請求金額決算` → `billing_amounts_settlement`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `決算年` | VARCHAR | `settlement_year` | VARCHAR(2) | 可 |  |
| 3 | `客先コード` | VARCHAR | `customer_code` | VARCHAR(3) | 可 |  |
| 4 | `客先` | VARCHAR | `customer` | VARCHAR(10) | 可 |  |
| 5 | `客先正式` | VARCHAR | `customer_official_name` | VARCHAR(30) | 可 |  |
| 6 | `かな` | VARCHAR | `kana` | VARCHAR(1) | 可 |  |
| 7 | `締日` | VARCHAR | `closing_day` | VARCHAR(2) | 可 |  |
| 8 | `9月請求額` | INTEGER | `sep_billing_amount` | INTEGER | 可 |  |
| 9 | `9月消費税額` | INTEGER | `sep_consumption_tax` | INTEGER | 可 |  |
| 10 | `10月請求額` | INTEGER | `oct_billing_amount` | INTEGER | 可 |  |
| 11 | `10月消費税額` | INTEGER | `oct_consumption_tax` | INTEGER | 可 |  |

### `t_重複客先` → `duplicate_customers`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `客先コード` | VARCHAR | `customer_code` | VARCHAR(3) | 可 |  |

## 4. 型変換ルール

| Access型 | PostgreSQL型 | 備考 |
|---|---|---|
| VARCHAR | varchar(n) | Accessのサイズを維持 |
| COUNTER | bigint | 採番値を忠実に移行 |
| INTEGER | integer | 整数 |
| DOUBLE | double precision | 浮動小数 |
| DATETIME | timestamp | 日付/時刻 |
| BIT | boolean | Yes/No |
| CURRENCY | numeric | 通貨 |

## 5. 注意事項

- 本移行は `受注データDB.accdb` の全16テーブルを対象としています。
- AccessのFKメタデータはODBCで取得できなかったため、外部キー制約は作成していません。
- `imp管理表` はExcel等から取り込んだ管理表データです（49列）。
- `t_請求書Tmp` / `t_納品書データ` は帳票出力用の一時テーブルです。
- 誤って移行した `受注データApp.accdb` 由来のテーブルは `--replace` 実行時に削除されます。
- 0件テーブルも構造再現のため作成しています: `t_納品書`, `t_納品書データ`, `t_請求書Tmp`
