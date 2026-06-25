# Access → PostgreSQL 移行対応表（order_performance_db）

## 1. 移行概要

- 対象Access DB：`C:\Users\seizo\Desktop\受注実績データ集計DB.accdb`
- 移行先PostgreSQL DB：`order_performance_db`
- 接続情報：`.env` の `DATABASE_URL` / `ACCESS_DB_PATH` を参照
- 移行日：2026-06-25 11:11:07
- 方針：受注実績データ集計DB.accdb の全4テーブル・全カラムを英語スネークケースへ変換し忠実に移行

## 2. 移行対象テーブル一覧

| No | Accessオブジェクト名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | `t_コントロール` | `app_control` | TABLE | 1 | 1 | 成功 |
| 2 | `t_受注キャンセル` | `order_cancellations` | TABLE | 602 | 602 | 成功 |
| 3 | `t_受注実績` | `order_performance` | TABLE | 60538 | 60538 | 成功 |
| 4 | `t_売月` | `sales_months` | TABLE | 156 | 156 | 成功 |

## 3. テーブル別カラム対応表

### `t_コントロール` → `app_control`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | `書込みフォルダ` | VARCHAR | `output_folder` | VARCHAR(255) | 可 |  |
| 3 | `最終日` | DATETIME | `last_date` | TIMESTAMP | 可 |  |
| 4 | `累積客別From` | INTEGER | `cumulative_by_customer_from` | INTEGER | 可 |  |
| 5 | `累積客別To` | INTEGER | `cumulative_by_customer_to` | INTEGER | 可 |  |
| 6 | `累積月別From` | INTEGER | `cumulative_by_month_from` | INTEGER | 可 |  |
| 7 | `累積月別To` | INTEGER | `cumulative_by_month_to` | INTEGER | 可 |  |
| 8 | `当月From` | DATETIME | `current_month_from` | TIMESTAMP | 可 |  |
| 9 | `当月To` | DATETIME | `current_month_to` | TIMESTAMP | 可 |  |

### `t_受注キャンセル` → `order_cancellations`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | `受注日` | DATETIME | `order_date` | TIMESTAMP | 可 |  |
| 3 | `注文番号` | VARCHAR | `order_no` | VARCHAR(25) | 可 |  |
| 4 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 5 | `品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 6 | `客先` | VARCHAR | `customer` | VARCHAR(30) | 可 |  |
| 7 | `コード` | VARCHAR | `code` | VARCHAR(3) | 可 |  |
| 8 | `締日` | VARCHAR | `closing_day` | VARCHAR(2) | 可 |  |
| 9 | `営業担当` | VARCHAR | `sales_rep` | VARCHAR(5) | 可 |  |
| 10 | `売月` | INTEGER | `sales_month` | INTEGER | 可 |  |
| 11 | `納期` | DATETIME | `due_date` | TIMESTAMP | 可 |  |
| 12 | `注文数` | INTEGER | `order_qty` | INTEGER | 可 |  |
| 13 | `単価` | CURRENCY | `unit_price` | NUMERIC | 可 |  |
| 14 | `金額` | INTEGER | `amount` | INTEGER | 可 | AccessではINTEGER型のためNUMERICではなくINTEGERで保持 |
| 15 | `注文ID` | VARCHAR | `order_id` | VARCHAR(8) | 可 |  |

### `t_受注実績` → `order_performance`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | `受注日` | DATETIME | `order_date` | TIMESTAMP | 可 |  |
| 3 | `注文番号` | VARCHAR | `order_no` | VARCHAR(25) | 可 |  |
| 4 | `品番` | VARCHAR | `product_no` | VARCHAR(30) | 可 |  |
| 5 | `品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 6 | `客先` | VARCHAR | `customer` | VARCHAR(30) | 可 |  |
| 7 | `コード` | VARCHAR | `code` | VARCHAR(3) | 可 |  |
| 8 | `締日` | VARCHAR | `closing_day` | VARCHAR(2) | 可 |  |
| 9 | `営業担当` | VARCHAR | `sales_rep` | VARCHAR(5) | 可 |  |
| 10 | `売月` | INTEGER | `sales_month` | INTEGER | 可 |  |
| 11 | `納期` | DATETIME | `due_date` | TIMESTAMP | 可 |  |
| 12 | `注文数` | INTEGER | `order_qty` | INTEGER | 可 |  |
| 13 | `単価` | CURRENCY | `unit_price` | NUMERIC | 可 |  |
| 14 | `金額` | INTEGER | `amount` | INTEGER | 可 | AccessではINTEGER型のためNUMERICではなくINTEGERで保持 |
| 15 | `注文ID` | VARCHAR | `order_id` | VARCHAR(8) | 可 |  |

### `t_売月` → `sales_months`

- Access種別: TABLE

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `売月` | INTEGER | `sales_month` | INTEGER | 可 |  |

## 4. 型変換ルール

| Access型 | PostgreSQL型 | 備考 |
|---|---|---|
| VARCHAR | varchar(n) | Accessのサイズを維持 |
| COUNTER | bigserial | AccessのID値を投入後、setvalで次採番をMAX(id)+1に同期。PRIMARY KEY付与 |
| INTEGER | integer | 整数 |
| DOUBLE | double precision | 浮動小数 |
| DATETIME | timestamp | 日付/時刻 |
| BIT | boolean | Yes/No |
| CURRENCY | numeric | 通貨 |

## 5. 注意事項

- 本移行は `受注実績データ集計DB.accdb` の全4テーブルを対象としています。
- AccessのFKメタデータはODBCで取得できなかったため、外部キー制約は作成していません。
- COUNTER列はBIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期しています。
- `t_コントロール` は集計処理の制御情報（書込みフォルダ・集計期間など）を保持します。
- `t_受注実績` / `t_受注キャンセル` は同一構造の15列テーブルです。
- `.laccdb` はAccessのロックファイルのため、移行元は `.accdb` 本体を使用します。
