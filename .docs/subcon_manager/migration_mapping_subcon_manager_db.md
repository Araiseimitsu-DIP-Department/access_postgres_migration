# Access → PostgreSQL 移行対応表（subcon_manager）

## 1. 移行概要

- 対象Access DB：`C:\Users\seizo\Desktop\協力会社委託加工処理品DB.accdb`
- 移行先PostgreSQL DB：`subcon_manager`
- 接続情報：`.env` の `DATABASE_URL` / `ACCESS_DB_PATH` を参照
- 移行日：2026-06-25 08:54:13
- 方針：協力会社委託加工処理品DB.accdb の全12テーブル・全カラムを英語スネークケースへ変換し忠実に移行

## 2. 移行対象テーブル一覧

| No | Accessオブジェクト名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | `t_クロス集計用` | `cross_tab_summary` | TABLE | 10 | 10 | 成功 |
| 2 | `t_コントロール` | `app_control` | TABLE | 1 | 1 | 成功 |
| 3 | `t_内職マスタ` | `home_work_master` | TABLE | 71 | 71 | 成功 |
| 4 | `t_客先` | `customers` | TABLE | 94 | 94 | 成功 |
| 5 | `t_手配先マスタ` | `supplier_master` | TABLE | 67 | 67 | 成功 |
| 6 | `t_発注` | `purchase_orders` | TABLE | 18758 | 18758 | 成功 |
| 7 | `t_発注 Start` | `purchase_orders_start` | TABLE | 116 | 116 | 成功 |
| 8 | `t_発注書` | `purchase_order_forms` | TABLE | 0 | 0 | 成功 |
| 9 | `t_発注書データ` | `purchase_order_form_data` | TABLE | 0 | 0 | 成功 |
| 10 | `t_納入` | `deliveries` | TABLE | 24130 | 24130 | 成功 |
| 11 | `t_納入 Start` | `deliveries_start` | TABLE | 3298 | 3298 | 成功 |
| 12 | `t_製品マスタ` | `product_master` | TABLE | 1520 | 1520 | 成功 |

## 3. テーブル別カラム対応表

### `t_クロス集計用` → `cross_tab_summary`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `まとめコード` | VARCHAR | `summary_code` | VARCHAR(3) | 可 |  |
| 3 | `手配先名` | VARCHAR | `supplier_name` | VARCHAR(30) | 可 |  |
| 4 | `納入月` | VARCHAR | `delivery_month` | VARCHAR(4) | 可 |  |
| 5 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |

### `t_コントロール` → `app_control`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `購入月From` | VARCHAR | `purchase_month_from` | VARCHAR(4) | 可 |  |
| 3 | `購入月To` | VARCHAR | `purchase_month_to` | VARCHAR(4) | 可 |  |
| 4 | `プリンタ` | VARCHAR | `printer_name` | VARCHAR(255) | 可 |  |

### `t_内職マスタ` → `home_work_master`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 3 | `検査内容` | VARCHAR | `inspection_content` | VARCHAR(50) | 可 |  |
| 4 | `検査治具` | VARCHAR | `inspection_jig` | VARCHAR(10) | 可 |  |
| 5 | `単価` | DOUBLE | `unit_price` | DOUBLE PRECISION | 可 |  |

### `t_客先` → `customers`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `コード` | VARCHAR | `code` | VARCHAR(3) | 可 |  |
| 2 | `客先` | VARCHAR | `customer` | VARCHAR(30) | 可 |  |
| 3 | `かな` | VARCHAR | `kana` | VARCHAR(1) | 可 |  |
| 4 | `担当` | VARCHAR | `person_in_charge` | VARCHAR(5) | 可 |  |

### `t_手配先マスタ` → `supplier_master`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `手配先コード` | VARCHAR | `supplier_code` | VARCHAR(3) | 可 |  |
| 2 | `手配先名` | VARCHAR | `supplier_name` | VARCHAR(30) | 可 |  |
| 3 | `発注区分` | VARCHAR | `order_category` | VARCHAR(1) | 可 |  |
| 4 | `かな` | VARCHAR | `kana` | VARCHAR(1) | 可 |  |
| 5 | `まとめコード` | VARCHAR | `summary_code` | VARCHAR(3) | 可 |  |
| 6 | `集計フラグ` | VARCHAR | `aggregation_flag` | VARCHAR(3) | 可 |  |
| 7 | `計算方法` | VARCHAR | `calculation_method` | VARCHAR(1) | 可 |  |
| 8 | `表示フラグ` | VARCHAR | `display_flag` | VARCHAR(1) | 可 |  |

### `t_発注` → `purchase_orders`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `発注ID` | COUNTER | `purchase_order_id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `発注日` | DATETIME | `order_date` | TIMESTAMP | 可 |  |
| 3 | `注文番号` | VARCHAR | `order_no` | VARCHAR(10) | 可 |  |
| 4 | `発注区分` | VARCHAR | `order_category` | VARCHAR(1) | 可 |  |
| 5 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 6 | `品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 7 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 8 | `表面処理` | VARCHAR | `surface_treatment` | VARCHAR(50) | 可 |  |
| 9 | `担当` | VARCHAR | `person_in_charge` | VARCHAR(5) | 可 |  |
| 10 | `手配先コード` | VARCHAR | `supplier_code` | VARCHAR(3) | 可 |  |
| 11 | `手配先名` | VARCHAR | `supplier_name` | VARCHAR(30) | 可 |  |
| 12 | `納期` | DATETIME | `due_date` | TIMESTAMP | 可 |  |
| 13 | `発注数` | INTEGER | `order_qty` | INTEGER | 可 |  |
| 14 | `単価` | DOUBLE | `unit_price` | DOUBLE PRECISION | 可 |  |
| 15 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |
| 16 | `納入済数` | INTEGER | `delivered_qty` | INTEGER | 可 |  |
| 17 | `納入残` | INTEGER | `delivery_balance` | INTEGER | 可 |  |
| 18 | `備考` | VARCHAR | `remarks` | VARCHAR(30) | 可 |  |
| 19 | `加工日` | DATETIME | `processing_date` | TIMESTAMP | 可 |  |
| 20 | `機番` | VARCHAR | `machine_no` | VARCHAR(5) | 可 |  |
| 21 | `完了フラグ` | VARCHAR | `completed_flag` | VARCHAR(1) | 可 |  |

### `t_発注 Start` → `purchase_orders_start`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `発注ID` | COUNTER | `purchase_order_id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `発注日` | DATETIME | `order_date` | TIMESTAMP | 可 |  |
| 3 | `注文番号` | VARCHAR | `order_no` | VARCHAR(10) | 可 |  |
| 4 | `発注区分` | VARCHAR | `order_category` | VARCHAR(1) | 可 |  |
| 5 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 6 | `品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 7 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 8 | `表面処理` | VARCHAR | `surface_treatment` | VARCHAR(50) | 可 |  |
| 9 | `担当` | VARCHAR | `person_in_charge` | VARCHAR(5) | 可 |  |
| 10 | `手配先コード` | VARCHAR | `supplier_code` | VARCHAR(3) | 可 |  |
| 11 | `手配先名` | VARCHAR | `supplier_name` | VARCHAR(30) | 可 |  |
| 12 | `納期` | DATETIME | `due_date` | TIMESTAMP | 可 |  |
| 13 | `発注数` | INTEGER | `order_qty` | INTEGER | 可 |  |
| 14 | `単価` | DOUBLE | `unit_price` | DOUBLE PRECISION | 可 |  |
| 15 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |
| 16 | `納入済数` | INTEGER | `delivered_qty` | INTEGER | 可 |  |
| 17 | `納入残` | INTEGER | `delivery_balance` | INTEGER | 可 |  |
| 18 | `備考` | VARCHAR | `remarks` | VARCHAR(30) | 可 |  |
| 19 | `加工日` | DATETIME | `processing_date` | TIMESTAMP | 可 |  |
| 20 | `機番` | VARCHAR | `machine_no` | VARCHAR(5) | 可 |  |
| 21 | `完了フラグ` | VARCHAR | `completed_flag` | VARCHAR(1) | 可 |  |

### `t_発注書` → `purchase_order_forms`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `発注日` | DATETIME | `order_date` | TIMESTAMP | 可 |  |
| 3 | `手配先コード` | VARCHAR | `supplier_code` | VARCHAR(3) | 可 |  |
| 4 | `手配先名` | VARCHAR | `supplier_name` | VARCHAR(30) | 可 |  |
| 5 | `注文番号` | VARCHAR | `order_no` | VARCHAR(10) | 可 |  |
| 6 | `品番` | VARCHAR | `product_no` | VARCHAR(40) | 可 |  |
| 7 | `発注数` | INTEGER | `order_qty` | INTEGER | 可 |  |
| 8 | `単価` | DOUBLE | `unit_price` | DOUBLE PRECISION | 可 |  |
| 9 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |
| 10 | `納期` | DATETIME | `due_date` | TIMESTAMP | 可 |  |
| 11 | `摘要` | VARCHAR | `summary` | VARCHAR(30) | 可 |  |
| 12 | `会社区分` | VARCHAR | `company_category` | VARCHAR(2) | 可 |  |
| 13 | `納期担当` | VARCHAR | `due_date_person` | VARCHAR(5) | 可 |  |

### `t_発注書データ` → `purchase_order_form_data`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `発注日` | DATETIME | `order_date` | TIMESTAMP | 可 |  |
| 3 | `手配先コード` | VARCHAR | `supplier_code` | VARCHAR(3) | 可 |  |
| 4 | `手配先名` | VARCHAR | `supplier_name` | VARCHAR(30) | 可 |  |
| 5 | `注文番号` | VARCHAR | `order_no` | VARCHAR(10) | 可 |  |
| 6 | `品番` | VARCHAR | `product_no` | VARCHAR(40) | 可 |  |
| 7 | `発注数` | INTEGER | `order_qty` | INTEGER | 可 |  |
| 8 | `単価` | DOUBLE | `unit_price` | DOUBLE PRECISION | 可 |  |
| 9 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |
| 10 | `納期` | DATETIME | `due_date` | TIMESTAMP | 可 |  |
| 11 | `摘要` | VARCHAR | `summary` | VARCHAR(30) | 可 |  |
| 12 | `会社区分` | VARCHAR | `company_category` | VARCHAR(2) | 可 |  |
| 13 | `納期担当` | VARCHAR | `due_date_person` | VARCHAR(5) | 可 |  |

### `t_納入` → `deliveries`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `納入ID` | COUNTER | `delivery_id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `発注ID` | INTEGER | `purchase_order_id` | INTEGER | 可 |  |
| 3 | `発注区分` | VARCHAR | `order_category` | VARCHAR(1) | 可 |  |
| 4 | `注文番号` | VARCHAR | `order_no` | VARCHAR(10) | 可 |  |
| 5 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 6 | `品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 7 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 8 | `表面処理` | VARCHAR | `surface_treatment` | VARCHAR(50) | 可 |  |
| 9 | `担当` | VARCHAR | `person_in_charge` | VARCHAR(5) | 可 |  |
| 10 | `手配先コード` | VARCHAR | `supplier_code` | VARCHAR(3) | 可 |  |
| 11 | `手配先名` | VARCHAR | `supplier_name` | VARCHAR(30) | 可 |  |
| 12 | `納入日` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 13 | `納入月` | VARCHAR | `delivery_month` | VARCHAR(4) | 可 |  |
| 14 | `納入数` | INTEGER | `delivery_qty` | INTEGER | 可 |  |
| 15 | `単価` | DOUBLE | `unit_price` | DOUBLE PRECISION | 可 |  |
| 16 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |
| 17 | `備考` | VARCHAR | `remarks` | VARCHAR(30) | 可 |  |
| 18 | `加工日` | DATETIME | `processing_date` | TIMESTAMP | 可 |  |
| 19 | `機番` | VARCHAR | `machine_no` | VARCHAR(5) | 可 |  |

### `t_納入 Start` → `deliveries_start`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `納入ID` | COUNTER | `delivery_id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `発注ID` | INTEGER | `purchase_order_id` | INTEGER | 可 |  |
| 3 | `発注区分` | VARCHAR | `order_category` | VARCHAR(1) | 可 |  |
| 4 | `注文番号` | VARCHAR | `order_no` | VARCHAR(10) | 可 |  |
| 5 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 6 | `品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 7 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 8 | `表面処理` | VARCHAR | `surface_treatment` | VARCHAR(50) | 可 |  |
| 9 | `担当` | VARCHAR | `person_in_charge` | VARCHAR(5) | 可 |  |
| 10 | `手配先コード` | VARCHAR | `supplier_code` | VARCHAR(3) | 可 |  |
| 11 | `手配先名` | VARCHAR | `supplier_name` | VARCHAR(30) | 可 |  |
| 12 | `納入日` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 13 | `納入月` | VARCHAR | `delivery_month` | VARCHAR(4) | 可 |  |
| 14 | `納入数` | INTEGER | `delivery_qty` | INTEGER | 可 |  |
| 15 | `単価` | DOUBLE | `unit_price` | DOUBLE PRECISION | 可 |  |
| 16 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |
| 17 | `備考` | VARCHAR | `remarks` | VARCHAR(30) | 可 |  |
| 18 | `加工日` | DATETIME | `processing_date` | TIMESTAMP | 可 |  |
| 19 | `機番` | VARCHAR | `machine_no` | VARCHAR(5) | 可 |  |

### `t_製品マスタ` → `product_master`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `製品番号` | VARCHAR | `product_code` | VARCHAR(30) | 可 |  |
| 2 | `製品名` | VARCHAR | `product_name_full` | VARCHAR(30) | 可 |  |
| 3 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 4 | `次工程` | VARCHAR | `next_process` | VARCHAR(50) | 可 |  |
| 5 | `担当` | VARCHAR | `person_in_charge` | VARCHAR(5) | 可 |  |
| 6 | `納期担当` | VARCHAR | `due_date_person` | VARCHAR(5) | 可 |  |
| 7 | `外部委託加工費` | DOUBLE | `external_subcontract_cost` | DOUBLE PRECISION | 可 |  |

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

- 本移行は `協力会社委託加工処理品DB.accdb` の全12テーブルを対象としています。
- AccessのFKメタデータはODBCで取得できなかったため、外部キー制約は作成していません。
- `t_発注 Start` / `t_納入 Start` はAccess起動時の作業用テーブルです。
- `t_発注書` / `t_発注書データ` は帳票出力用の一時テーブルです（0件）。
- `t_クロス集計用` はクロス集計レポート用の集計データです。
- 0件テーブルも構造再現のため作成しています: `t_発注書`, `t_発注書データ`
