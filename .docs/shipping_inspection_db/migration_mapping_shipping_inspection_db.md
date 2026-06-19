# Access → PostgreSQL 移行対応表（shipping_inspection_db）

## 1. 移行概要

- 対象Access DB：`C:\Users\seika\Desktop\出荷検査一覧DB.accdb`
- 移行先PostgreSQL DB：`shipping_inspection_db`
- 接続情報：`.env` の `DATABASE_URL` / `ACCESS_DB_PATH` を参照
- 移行日：2026-06-19 09:49:41
- 作成者：Cursor Agent
- 備考：9テーブルを移行（`T_仕掛数`・`T_外検担` は移行対象外）

## 2. 移行対象テーブル一覧

| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | `T_先行検査一覧` | `advance_inspection_list` | TABLE | 5 | 5 | 成功 |
| 2 | `T_出荷データ` | `shipping_data` | TABLE | 13 | 13 | 成功 |
| 3 | `T_出荷検査残` | `shipping_inspection_remaining` | TABLE | 864 | 864 | 成功 |
| 4 | `T_出荷検査残（前日）` | `shipping_inspection_remaining_prev_day` | TABLE | 872 | 872 | 成功 |
| 5 | `T_品番別検査担当者` | `product_inspection_staff` | TABLE | 5 | 5 | 成功 |
| 6 | `T_工程別仕掛数` | `process_wip_quantities` | TABLE | 158 | 158 | 成功 |
| 7 | `T_更新日時` | `db_updated_at` | TABLE | 1 | 1 | 成功 |
| 8 | `T_梱包担` | `packaging_staff` | TABLE | 9 | 9 | 成功 |
| 9 | `T_検査時間` | `inspection_duration` | TABLE | 1348 | 1348 | 成功 |

## 3. テーブル別カラム対応表

### Accessテーブル名：`T_先行検査一覧`
### PostgreSQLテーブル名：`advance_inspection_list`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `品番` | VARCHAR | `product_code` | VARCHAR(255) | 可 |  |
| 2 | `品名` | VARCHAR | `product_name` | VARCHAR(255) | 可 |  |
| 3 | `客先` | VARCHAR | `customer` | VARCHAR(255) | 可 |  |
| 4 | `注文ID` | VARCHAR | `order_id` | VARCHAR(255) | 可 |  |

### Accessテーブル名：`T_出荷データ`
### PostgreSQLテーブル名：`shipping_data`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `注文ID` | VARCHAR | `order_id` | VARCHAR(255) | 可 |  |
| 2 | `品番` | VARCHAR | `product_code` | VARCHAR(255) | 可 |  |
| 3 | `品名` | VARCHAR | `product_name` | VARCHAR(255) | 可 |  |
| 4 | `客先` | VARCHAR | `customer` | VARCHAR(255) | 可 |  |
| 5 | `出荷予定日` | DATETIME | `scheduled_ship_date` | TIMESTAMP | 可 |  |
| 6 | `着荷予定日` | DATETIME | `scheduled_arrival_date` | TIMESTAMP | 可 |  |
| 7 | `出荷数` | VARCHAR | `shipment_quantity` | VARCHAR(255) | 可 | Access上は文字列型。数値文字列をそのまま保持 |
| 8 | `在庫数` | INTEGER | `stock_quantity` | INTEGER | 可 |  |
| 9 | `当日洗浄` | VARCHAR | `same_day_washing` | VARCHAR(255) | 可 |  |
| 10 | `二次処理` | VARCHAR | `secondary_process` | VARCHAR(255) | 可 |  |
| 11 | `検査備考` | VARCHAR | `inspection_remarks` | VARCHAR(255) | 可 |  |
| 12 | `出荷備考` | VARCHAR | `shipping_remarks` | VARCHAR(255) | 可 |  |
| 13 | `送り先指定` | VARCHAR | `delivery_destination` | VARCHAR(255) | 可 |  |
| 14 | `保管場所` | VARCHAR | `storage_location` | VARCHAR(255) | 可 |  |
| 15 | `外検担` | INTEGER | `external_inspection_staff_id` | INTEGER | 可 |  |
| 16 | `納期担` | VARCHAR | `due_date_person` | VARCHAR(255) | 可 |  |
| 17 | `先行` | BIT | `advance_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 18 | `検査` | BIT | `inspection_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 19 | `計量` | BIT | `weighing_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 20 | `梱包` | BIT | `packaging_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 21 | `変更点` | VARCHAR | `change_notes` | VARCHAR(255) | 可 |  |
| 22 | `累計` | INTEGER | `cumulative_total` | INTEGER | 可 |  |
| 23 | `使用ロット` | LONGCHAR | `used_lots` | TEXT | 可 | ロット割当情報の長文文字列 |
| 24 | `データ` | BIT | `data_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 25 | `先行洗浄` | BIT | `advance_washing_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 26 | `洗浄備考` | VARCHAR | `washing_remarks` | VARCHAR(255) | 可 |  |
| 27 | `梱包担` | INTEGER | `packaging_staff_id` | INTEGER | 可 |  |
| 28 | `確認者` | INTEGER | `confirmer_id` | INTEGER | 可 |  |

### Accessテーブル名：`T_出荷検査残`
### PostgreSQLテーブル名：`shipping_inspection_remaining`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `注文ID` | VARCHAR | `order_id` | VARCHAR(255) | 可 |  |
| 2 | `品番` | VARCHAR | `product_code` | VARCHAR(255) | 可 |  |
| 3 | `品名` | VARCHAR | `product_name` | VARCHAR(255) | 可 |  |
| 4 | `客先` | VARCHAR | `customer` | VARCHAR(255) | 可 |  |
| 5 | `出荷予定日` | DATETIME | `scheduled_ship_date` | TIMESTAMP | 可 |  |
| 6 | `着荷予定日` | DATETIME | `scheduled_arrival_date` | TIMESTAMP | 可 |  |
| 7 | `出荷数` | VARCHAR | `shipment_quantity` | VARCHAR(255) | 可 | Access上は文字列型。数値文字列をそのまま保持 |
| 8 | `在庫数` | INTEGER | `stock_quantity` | INTEGER | 可 |  |
| 9 | `当日洗浄` | VARCHAR | `same_day_washing` | VARCHAR(255) | 可 |  |
| 10 | `二次処理` | VARCHAR | `secondary_process` | VARCHAR(255) | 可 |  |
| 11 | `検査備考` | VARCHAR | `inspection_remarks` | VARCHAR(255) | 可 |  |
| 12 | `出荷備考` | VARCHAR | `shipping_remarks` | VARCHAR(255) | 可 |  |
| 13 | `送り先指定` | VARCHAR | `delivery_destination` | VARCHAR(255) | 可 |  |
| 14 | `保管場所` | VARCHAR | `storage_location` | VARCHAR(255) | 可 |  |
| 15 | `外検担` | INTEGER | `external_inspection_staff_id` | INTEGER | 可 |  |
| 16 | `納期担` | VARCHAR | `due_date_person` | VARCHAR(255) | 可 |  |
| 17 | `先行` | BIT | `advance_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 18 | `検査` | BIT | `inspection_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 19 | `計量` | BIT | `weighing_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 20 | `梱包` | BIT | `packaging_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 21 | `変更点` | VARCHAR | `change_notes` | VARCHAR(255) | 可 |  |
| 22 | `累計` | INTEGER | `cumulative_total` | INTEGER | 可 |  |
| 23 | `使用ロット` | LONGCHAR | `used_lots` | TEXT | 可 | ロット割当情報の長文文字列 |
| 24 | `データ` | BIT | `data_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 25 | `確認` | BIT | `confirmed_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 26 | `先行洗浄` | BIT | `advance_washing_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 27 | `洗浄備考` | VARCHAR | `washing_remarks` | VARCHAR(255) | 可 |  |
| 28 | `梱包担` | INTEGER | `packaging_staff_id` | INTEGER | 可 |  |
| 29 | `確認者` | INTEGER | `confirmer_id` | INTEGER | 可 |  |

### Accessテーブル名：`T_出荷検査残（前日）`
### PostgreSQLテーブル名：`shipping_inspection_remaining_prev_day`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `注文ID` | VARCHAR | `order_id` | VARCHAR(255) | 可 |  |
| 2 | `品番` | VARCHAR | `product_code` | VARCHAR(255) | 可 |  |
| 3 | `品名` | VARCHAR | `product_name` | VARCHAR(255) | 可 |  |
| 4 | `客先` | VARCHAR | `customer` | VARCHAR(255) | 可 |  |
| 5 | `出荷予定日` | DATETIME | `scheduled_ship_date` | TIMESTAMP | 可 |  |
| 6 | `着荷予定日` | DATETIME | `scheduled_arrival_date` | TIMESTAMP | 可 |  |
| 7 | `出荷数` | VARCHAR | `shipment_quantity` | VARCHAR(255) | 可 | Access上は文字列型。数値文字列をそのまま保持 |
| 8 | `在庫数` | INTEGER | `stock_quantity` | INTEGER | 可 |  |
| 9 | `当日洗浄` | VARCHAR | `same_day_washing` | VARCHAR(255) | 可 |  |
| 10 | `二次処理` | VARCHAR | `secondary_process` | VARCHAR(255) | 可 |  |
| 11 | `検査備考` | VARCHAR | `inspection_remarks` | VARCHAR(255) | 可 |  |
| 12 | `出荷備考` | VARCHAR | `shipping_remarks` | VARCHAR(255) | 可 |  |
| 13 | `送り先指定` | VARCHAR | `delivery_destination` | VARCHAR(255) | 可 |  |
| 14 | `保管場所` | VARCHAR | `storage_location` | VARCHAR(255) | 可 |  |
| 15 | `外検担` | INTEGER | `external_inspection_staff_id` | INTEGER | 可 |  |
| 16 | `納期担` | VARCHAR | `due_date_person` | VARCHAR(255) | 可 |  |
| 17 | `先行` | BIT | `advance_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 18 | `検査` | BIT | `inspection_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 19 | `計量` | BIT | `weighing_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 20 | `梱包` | BIT | `packaging_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 21 | `変更点` | VARCHAR | `change_notes` | VARCHAR(255) | 可 |  |
| 22 | `累計` | INTEGER | `cumulative_total` | INTEGER | 可 |  |
| 23 | `使用ロット` | LONGCHAR | `used_lots` | TEXT | 可 | ロット割当情報の長文文字列 |
| 24 | `データ` | BIT | `data_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 25 | `確認` | BIT | `confirmed_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 26 | `先行洗浄` | BIT | `advance_washing_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 27 | `洗浄備考` | VARCHAR | `washing_remarks` | VARCHAR(255) | 可 |  |
| 28 | `梱包担` | INTEGER | `packaging_staff_id` | INTEGER | 可 |  |
| 29 | `確認者` | INTEGER | `confirmer_id` | INTEGER | 可 |  |

### Accessテーブル名：`T_品番別検査担当者`
### PostgreSQLテーブル名：`product_inspection_staff`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `品番` | VARCHAR | `product_code` | VARCHAR(255) | 可 |  |
| 2 | `品名` | VARCHAR | `product_name` | VARCHAR(255) | 可 |  |
| 3 | `客先` | VARCHAR | `customer` | VARCHAR(255) | 可 |  |
| 4 | `検査員名` | VARCHAR | `inspector_names` | VARCHAR(255) | 可 |  |

### Accessテーブル名：`T_工程別仕掛数`
### PostgreSQLテーブル名：`process_wip_quantities`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `品番` | VARCHAR | `product_code` | VARCHAR(255) | 可 |  |
| 2 | `工程1` | DOUBLE | `process_1` | DOUBLE PRECISION | 可 |  |
| 3 | `工程2` | DOUBLE | `process_2` | DOUBLE PRECISION | 可 |  |
| 4 | `工程3` | DOUBLE | `process_3` | DOUBLE PRECISION | 可 |  |
| 5 | `工程4` | DOUBLE | `process_4` | DOUBLE PRECISION | 可 |  |
| 6 | `工程5` | DOUBLE | `process_5` | DOUBLE PRECISION | 可 |  |
| 7 | `工程6` | DOUBLE | `process_6` | DOUBLE PRECISION | 可 |  |
| 8 | `工程7` | DOUBLE | `process_7` | DOUBLE PRECISION | 可 |  |
| 9 | `工程8` | DOUBLE | `process_8` | DOUBLE PRECISION | 可 |  |
| 10 | `工程9` | DOUBLE | `process_9` | DOUBLE PRECISION | 可 |  |
| 11 | `洗浄` | DOUBLE | `washing` | DOUBLE PRECISION | 可 |  |
| 12 | `数値検査` | DOUBLE | `dimensional_inspection` | DOUBLE PRECISION | 可 |  |
| 13 | `外観検査` | DOUBLE | `appearance_inspection` | DOUBLE PRECISION | 可 |  |
| 14 | `その他` | DOUBLE | `other` | DOUBLE PRECISION | 可 |  |
| 15 | `仕掛梱包` | DOUBLE | `wip_packaging` | DOUBLE PRECISION | 可 |  |
| 16 | `処理済` | DOUBLE | `processed` | DOUBLE PRECISION | 可 |  |
| 17 | `不適合品` | DOUBLE | `nonconforming_items` | DOUBLE PRECISION | 可 |  |
| 18 | `完了ロット` | DOUBLE | `completed_lots` | DOUBLE PRECISION | 可 |  |
| 19 | `最終洗浄工程番号` | INTEGER | `final_washing_process_no` | INTEGER | 可 |  |

### Accessテーブル名：`T_更新日時`
### PostgreSQLテーブル名：`db_updated_at`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `日時` | DATETIME | `updated_at` | TIMESTAMP | 可 |  |

### Accessテーブル名：`T_梱包担`
### PostgreSQLテーブル名：`packaging_staff`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | INTEGER | `id` | INTEGER | 可 |  |
| 2 | `担当者` | VARCHAR | `staff_name` | VARCHAR(6) | 可 |  |
| 3 | `表示フラグ` | BIT | `display_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |

### Accessテーブル名：`T_検査時間`
### PostgreSQLテーブル名：`inspection_duration`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `品番` | VARCHAR | `product_code` | VARCHAR(30) | 可 |  |
| 2 | `秒` | DOUBLE | `seconds` | DOUBLE PRECISION | 可 |  |


### 移行対象外テーブル

| Accessテーブル名 | 理由 |
|---|---|
| `T_仕掛数` | 別システムで管理 |
| `T_外検担` | 別システムで管理 |

## 4. 主キー・インデックス情報

| Accessテーブル名 | PostgreSQLテーブル名 | 主キー | インデックス | 備考 |
|---|---|---|---|---|
| `T_先行検査一覧` | `advance_inspection_list` | なし | なし | Access側で主キー未設定 |
| `T_出荷データ` | `shipping_data` | なし | なし | Access側で主キー未設定 |
| `T_出荷検査残` | `shipping_inspection_remaining` | なし | なし | Access側で主キー未設定 |
| `T_出荷検査残（前日）` | `shipping_inspection_remaining_prev_day` | なし | なし | Access側で主キー未設定 |
| `T_品番別検査担当者` | `product_inspection_staff` | なし | なし | Access側で主キー未設定 |
| `T_工程別仕掛数` | `process_wip_quantities` | なし | なし | Access側で主キー未設定 |
| `T_更新日時` | `db_updated_at` | なし | なし | Access側で主キー未設定 |
| `T_梱包担` | `packaging_staff` | なし | なし | Access側で主キー未設定 |
| `T_検査時間` | `inspection_duration` | なし | なし | Access側で主キー未設定 |

## 5. 型変換ルール

| Access型 | PostgreSQL型 | 備考 |
|---|---|---|
| Short Text (VARCHAR) | varchar(n) | Accessのサイズを維持 |
| Long Text (LONGCHAR) | text | 長文（使用ロット等） |
| Number (INTEGER) | integer | 整数 |
| Number (DOUBLE) | double precision | 浮動小数 |
| Date/Time | timestamp | 日付/時刻 |
| Yes/No (BIT) | boolean | True/False |

## 6. アプリ接続時の参照情報

### 接続先

```text
.env の DATABASE_URL を使用
```

### 主に参照するテーブル

| 用途 | PostgreSQLテーブル名 | 主なキー | 備考 |
| --- | --- | --- | --- |
| 当日出荷データ | `shipping_data` | `order_id` | T_出荷データ |
| 出荷検査残一覧 | `shipping_inspection_remaining` | `order_id` | T_出荷検査残 |
| 前日出荷検査残 | `shipping_inspection_remaining_prev_day` | `order_id` | T_出荷検査残（前日） |
| 先行検査対象 | `advance_inspection_list` | `product_code`, `order_id` | T_先行検査一覧 |
| 梱包担当マスタ | `packaging_staff` | `id` | T_梱包担 |
| 品番別検査担当 | `product_inspection_staff` | `product_code` | T_品番別検査担当者 |
| 工程別仕掛数 | `process_wip_quantities` | `product_code` | T_工程別仕掛数 |
| 検査時間 | `inspection_duration` | `product_code` | T_検査時間 |
| DB更新日時 | `db_updated_at` | — | T_更新日時（1行） |

### 主要カラム

| 用途 | PostgreSQLテーブル名 | PostgreSQLカラム名 | 元Accessカラム名 | 備考 |
| --- | --- | --- | --- | --- |
| 参照 | `shipping_data` | `order_id` | `注文ID` | |
| 参照 | `shipping_data` | `product_code` | `品番` | |
| 参照 | `shipping_data` | `scheduled_ship_date` | `出荷予定日` | |
| 参照 | `shipping_data` | `shipment_quantity` | `出荷数` | |
| 参照 | `shipping_inspection_remaining` | `order_id` | `注文ID` | |
| 参照 | `shipping_inspection_remaining` | `product_code` | `品番` | |
| 参照 | `shipping_inspection_remaining` | `scheduled_ship_date` | `出荷予定日` | |
| 参照 | `shipping_inspection_remaining_prev_day` | `order_id` | `注文ID` | |
| 参照 | `shipping_inspection_remaining_prev_day` | `product_code` | `品番` | |
| 参照 | `shipping_inspection_remaining_prev_day` | `scheduled_ship_date` | `出荷予定日` | |
| 参照 | `advance_inspection_list` | `product_code` | `品番` | |
| 参照 | `advance_inspection_list` | `order_id` | `注文ID` | |
| 参照 | `packaging_staff` | `id` | `ID` | |
| 参照 | `packaging_staff` | `staff_name` | `担当者` | |

## 7. 注意事項・要確認事項

- 本移行は `出荷検査一覧DB.accdb` のうち9テーブルを対象としています。
- 移行対象外: `T_仕掛数`（別システムで管理）、`T_外検担`（別システムで管理）。
- AccessのFKメタデータはODBCで取得できなかったため、外部キー制約は作成していません。
- `T_出荷データ`.`外検担` は担当者ID（INTEGER）として `external_inspection_staff_id` に移行。マスタ `T_外検担` は移行しない。
- `出荷数` はAccess上 VARCHAR 型のため、PostgreSQLでも文字列として保持しています。
- `使用ロット` はロット割当情報のエンコード文字列です。
- `T_出荷検査残（前日）` は前日スナップショット用テーブルです。
- `T_更新日時` はAccess側の最終更新日時（1行）です。
- `T_検査時間`.`品番` に `########` という不正表示値が1件存在します（Access側データ要確認）。
- `最終洗浄工程番号` はAccess上すべてNULLです。
