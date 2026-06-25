# Access → PostgreSQL 移行対応表（material_millsheet_manager）

## 1. 移行概要

- 対象Access DB：`C:\Users\seizo\Desktop\材料入庫管理台帳兼ミルシート管理表DB.accdb`
- 移行先PostgreSQL DB：`material_millsheet_manager`
- 接続情報：`.env` の `DATABASE_URL` / `ACCESS_DB_PATH` を参照
- 移行日：2026-06-25 08:53:22
- 方針：材料入庫管理台帳兼ミルシート管理表DB.accdb の全11テーブル・全カラムを英語スネークケースへ変換し忠実に移行

## 2. 移行対象テーブル一覧

| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | `t_クロス集計用` | `cross_aggregation` | TABLE | 8 | 8 | 成功 |
| 2 | `t_コントロール` | `app_control` | TABLE | 1 | 1 | 成功 |
| 3 | `t_備考内容` | `remarks_master` | TABLE | 3 | 3 | 成功 |
| 4 | `t_旧検査データ` | `legacy_inspection_data` | TABLE | 7993 | 7993 | 成功 |
| 5 | `t_材料納入Tmp` | `material_delivery_temp` | TABLE | 0 | 0 | 成功 |
| 6 | `t_材料納入履歴` | `material_delivery_history` | TABLE | 14633 | 14633 | 成功 |
| 7 | `t_材料納入履歴 変更前` | `material_delivery_history_before_change` | TABLE | 2677 | 2677 | 成功 |
| 8 | `t_材質` | `material_types` | TABLE | 92 | 92 | 成功 |
| 9 | `t_検査データ` | `inspection_data` | TABLE | 1053 | 1053 | 成功 |
| 10 | `t_検査員` | `inspectors` | TABLE | 6 | 6 | 成功 |
| 11 | `t_納入業者` | `suppliers` | TABLE | 21 | 21 | 成功 |

## 3. テーブル別カラム対応表

### `t_クロス集計用` → `cross_aggregation`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `納入業者コード` | VARCHAR | `supplier_code` | VARCHAR(2) | 可 |  |
| 3 | `納入業者名` | VARCHAR | `supplier_name` | VARCHAR(20) | 可 |  |
| 4 | `購入月` | VARCHAR | `purchase_month` | VARCHAR(4) | 可 |  |
| 5 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |

### `t_コントロール` → `app_control`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `書込みフォルダ` | VARCHAR | `write_folder` | VARCHAR(255) | 可 |  |
| 3 | `購入月From` | VARCHAR | `purchase_month_from` | VARCHAR(4) | 可 |  |
| 4 | `購入月To` | VARCHAR | `purchase_month_to` | VARCHAR(4) | 可 |  |

### `t_備考内容` → `remarks_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `コード` | VARCHAR | `code` | VARCHAR(2) | 可 |  |
| 2 | `備考内容` | VARCHAR | `remark_text` | VARCHAR(10) | 可 |  |

### `t_旧検査データ` → `legacy_inspection_data`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `購入ID` | INTEGER | `purchase_id` | INTEGER | 可 |  |
| 3 | `寸法1` | DOUBLE | `dimension_1` | DOUBLE PRECISION | 可 |  |
| 4 | `寸法2` | DOUBLE | `dimension_2` | DOUBLE PRECISION | 可 |  |
| 5 | `判定結果` | VARCHAR | `judgment_result` | VARCHAR(3) | 可 |  |
| 6 | `備考` | VARCHAR | `remarks` | VARCHAR(10) | 可 |  |
| 7 | `検査員名` | VARCHAR | `inspector_name` | VARCHAR(8) | 可 |  |
| 8 | `確認` | BIT | `confirmed` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 9 | `内容` | VARCHAR | `content` | VARCHAR(10) | 可 |  |

### `t_材料納入Tmp` → `material_delivery_temp`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `入荷日` | DATETIME | `receipt_date` | TIMESTAMP | 可 |  |
| 3 | `伝票日付` | DATETIME | `slip_date` | TIMESTAMP | 可 |  |
| 4 | `区分` | VARCHAR | `category_code` | VARCHAR(1) | 可 |  |
| 5 | `納入業者コード` | VARCHAR | `supplier_code` | VARCHAR(2) | 可 |  |
| 6 | `納入業者名` | VARCHAR | `supplier_name` | VARCHAR(20) | 可 |  |
| 7 | `購入月` | VARCHAR | `purchase_month` | VARCHAR(4) | 可 |  |
| 8 | `品種` | VARCHAR | `material_kind` | VARCHAR(15) | 可 |  |
| 9 | `納入品目` | VARCHAR | `delivered_item` | VARCHAR(50) | 可 |  |
| 10 | `サイズ` | VARCHAR | `size` | VARCHAR(10) | 可 |  |
| 11 | `重量` | DOUBLE | `weight` | DOUBLE PRECISION | 可 |  |
| 12 | `単価` | INTEGER | `unit_price` | INTEGER | 可 |  |
| 13 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |
| 14 | `ロット番号` | VARCHAR | `lot_no` | VARCHAR(50) | 可 |  |
| 15 | `使用製品番号` | VARCHAR | `used_product_no` | VARCHAR(30) | 可 |  |
| 16 | `客先名` | VARCHAR | `customer_name` | VARCHAR(20) | 可 |  |
| 17 | `仕様` | VARCHAR | `specification` | VARCHAR(30) | 可 |  |
| 18 | `備考` | VARCHAR | `remarks` | VARCHAR(30) | 可 |  |
| 19 | `登録フラグ` | BIT | `registered_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 20 | `入荷場所` | VARCHAR | `receipt_location` | VARCHAR(15) | 可 |  |

### `t_材料納入履歴` → `material_delivery_history`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `入荷日` | DATETIME | `receipt_date` | TIMESTAMP | 可 |  |
| 3 | `伝票日付` | DATETIME | `slip_date` | TIMESTAMP | 可 |  |
| 4 | `区分` | VARCHAR | `category_code` | VARCHAR(1) | 可 |  |
| 5 | `納入業者コード` | VARCHAR | `supplier_code` | VARCHAR(2) | 可 |  |
| 6 | `納入業者名` | VARCHAR | `supplier_name` | VARCHAR(20) | 可 |  |
| 7 | `購入月` | VARCHAR | `purchase_month` | VARCHAR(4) | 可 |  |
| 8 | `品種` | VARCHAR | `material_kind` | VARCHAR(15) | 可 |  |
| 9 | `納入品目` | VARCHAR | `delivered_item` | VARCHAR(50) | 可 |  |
| 10 | `サイズ` | VARCHAR | `size` | VARCHAR(10) | 可 |  |
| 11 | `重量` | DOUBLE | `weight` | DOUBLE PRECISION | 可 |  |
| 12 | `単価` | INTEGER | `unit_price` | INTEGER | 可 |  |
| 13 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |
| 14 | `ロット番号` | VARCHAR | `lot_no` | VARCHAR(50) | 可 |  |
| 15 | `使用製品番号` | VARCHAR | `used_product_no` | VARCHAR(30) | 可 |  |
| 16 | `客先名` | VARCHAR | `customer_name` | VARCHAR(20) | 可 |  |
| 17 | `仕様` | VARCHAR | `specification` | VARCHAR(30) | 可 |  |
| 18 | `備考` | VARCHAR | `remarks` | VARCHAR(30) | 可 |  |
| 19 | `入荷場所` | VARCHAR | `receipt_location` | VARCHAR(15) | 可 |  |

### `t_材料納入履歴 変更前` → `material_delivery_history_before_change`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `入荷日` | DATETIME | `receipt_date` | TIMESTAMP | 可 |  |
| 3 | `伝票日付` | DATETIME | `slip_date` | TIMESTAMP | 可 |  |
| 4 | `区分` | VARCHAR | `category_code` | VARCHAR(1) | 可 |  |
| 5 | `納入業者コード` | VARCHAR | `supplier_code` | VARCHAR(2) | 可 |  |
| 6 | `納入業者名` | VARCHAR | `supplier_name` | VARCHAR(20) | 可 |  |
| 7 | `購入月` | VARCHAR | `purchase_month` | VARCHAR(4) | 可 |  |
| 8 | `品種` | VARCHAR | `material_kind` | VARCHAR(15) | 可 |  |
| 9 | `納入品目` | VARCHAR | `delivered_item` | VARCHAR(50) | 可 |  |
| 10 | `サイズ` | VARCHAR | `size` | VARCHAR(10) | 可 |  |
| 11 | `重量` | DOUBLE | `weight` | DOUBLE PRECISION | 可 |  |
| 12 | `単価` | INTEGER | `unit_price` | INTEGER | 可 |  |
| 13 | `金額` | INTEGER | `amount` | INTEGER | 可 | 変更前履歴テーブルではINTEGER型のためNUMERICではなくINTEGERで保持 |
| 14 | `ロット番号` | VARCHAR | `lot_no` | VARCHAR(50) | 可 |  |
| 15 | `使用製品番号` | VARCHAR | `used_product_no` | VARCHAR(30) | 可 |  |
| 16 | `客先名` | VARCHAR | `customer_name` | VARCHAR(20) | 可 |  |
| 17 | `仕様` | VARCHAR | `specification` | VARCHAR(30) | 可 |  |
| 18 | `備考` | VARCHAR | `remarks` | VARCHAR(30) | 可 |  |

### `t_材質` → `material_types`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `材質` | VARCHAR | `material_type` | VARCHAR(20) | 可 |  |
| 2 | `記号` | VARCHAR | `symbol` | VARCHAR(1) | 可 |  |

### `t_検査データ` → `inspection_data`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `購入ID` | INTEGER | `purchase_id` | INTEGER | 可 |  |
| 3 | `寸法1左最大` | DOUBLE | `dim1_left_max` | DOUBLE PRECISION | 可 |  |
| 4 | `寸法1左最小` | DOUBLE | `dim1_left_min` | DOUBLE PRECISION | 可 |  |
| 5 | `寸法1中最大` | DOUBLE | `dim1_center_max` | DOUBLE PRECISION | 可 |  |
| 6 | `寸法1中最小` | DOUBLE | `dim1_center_min` | DOUBLE PRECISION | 可 |  |
| 7 | `寸法1右最大` | DOUBLE | `dim1_right_max` | DOUBLE PRECISION | 可 |  |
| 8 | `寸法1右最小` | DOUBLE | `dim1_right_min` | DOUBLE PRECISION | 可 |  |
| 9 | `寸法2左最大` | DOUBLE | `dim2_left_max` | DOUBLE PRECISION | 可 |  |
| 10 | `寸法2左最小` | DOUBLE | `dim2_left_min` | DOUBLE PRECISION | 可 |  |
| 11 | `寸法2中最大` | DOUBLE | `dim2_center_max` | DOUBLE PRECISION | 可 |  |
| 12 | `寸法2中最小` | DOUBLE | `dim2_center_min` | DOUBLE PRECISION | 可 |  |
| 13 | `寸法2右最大` | DOUBLE | `dim2_right_max` | DOUBLE PRECISION | 可 |  |
| 14 | `寸法2右最小` | DOUBLE | `dim2_right_min` | DOUBLE PRECISION | 可 |  |
| 15 | `判定結果` | VARCHAR | `judgment_result` | VARCHAR(3) | 可 |  |
| 16 | `曲がり` | VARCHAR | `bending` | VARCHAR(2) | 可 |  |
| 17 | `キズ` | VARCHAR | `scratch` | VARCHAR(2) | 可 |  |
| 18 | `汚れ` | VARCHAR | `dirt` | VARCHAR(2) | 可 |  |
| 19 | `検査員名` | VARCHAR | `inspector_name` | VARCHAR(8) | 可 |  |
| 20 | `確認` | BIT | `confirmed` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 21 | `内容` | VARCHAR | `content` | VARCHAR(10) | 可 |  |

### `t_検査員` → `inspectors`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `コード` | VARCHAR | `code` | VARCHAR(2) | 可 |  |
| 2 | `検査員名` | VARCHAR | `inspector_name` | VARCHAR(8) | 可 |  |

### `t_納入業者` → `suppliers`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `納入業者コード` | VARCHAR | `supplier_code` | VARCHAR(2) | 可 |  |
| 2 | `納入業者名` | VARCHAR | `supplier_name` | VARCHAR(20) | 可 |  |
| 3 | `締日` | VARCHAR | `closing_day` | VARCHAR(2) | 可 |  |
| 4 | `計算方法` | VARCHAR | `calculation_method` | VARCHAR(1) | 可 |  |

## 4. 型変換ルール

| Access型 | PostgreSQL型 | 備考 |
|---|---|---|
| VARCHAR | varchar(n) | Accessのサイズを維持 |
| COUNTER | bigint | 採番値を忠実に移行 |
| INTEGER | integer | 整数 |
| DOUBLE | double precision | 浮動小数 |
| DATETIME | timestamp | 日付/時刻 |
| BIT | boolean | Yes/No |
| CURRENCY | numeric | 金額 |

## 5. 注意事項

- 本移行は `材料入庫管理台帳兼ミルシート管理表DB.accdb` の11テーブルを対象としています。
- AccessのFKメタデータはODBCで取得できなかったため、外部キー制約は作成していません。
- `t_材料納入履歴 変更前` はスキーマ変更前のバックアップテーブルです。金額列はINTEGER型です。
- `t_材料納入Tmp` は一時登録用テーブルです（0件でも構造を再現）。
- `t_旧検査データ` は旧形式の検査データです。現行は `t_検査データ` を使用しています。
- `購入ID` は材料納入履歴のIDを参照する論理FKですが、制約は未設定です。
- 0件テーブルも構造再現のため作成しています: `t_材料納入Tmp`
