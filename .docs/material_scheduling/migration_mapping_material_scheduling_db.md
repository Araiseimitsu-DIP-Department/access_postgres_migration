# Access → PostgreSQL 移行対応表（material_scheduling）

## 1. 移行概要

- 対象Access DB：`C:\Users\seizo\my_projects\1\access_postgres_migration\.docs\material_scheduling\セット予定材料管理DB.accdb`
- 移行先PostgreSQL DB：`material_scheduling`
- 接続情報：`.env` の `DATABASE_URL` / `ACCESS_DB_PATH` を参照
- 移行日：2026-06-25 09:35:44
- 方針：セット予定材料管理DB.accdb の全23テーブル・全カラムを英語スネークケースへ変換し忠実に移行

## 2. 移行対象テーブル一覧

| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | `t_コントロール` | `app_control` | TABLE | 1 | 1 | 成功 |
| 2 | `t_セット予定` | `set_schedules` | TABLE | 5199 | 5199 | 成功 |
| 3 | `t_チャックマスタ` | `chuck_master` | TABLE | 467 | 467 | 成功 |
| 4 | `t_一時停止` | `production_pauses` | TABLE | 0 | 0 | 成功 |
| 5 | `t_受信メールマスタ` | `inbound_email_master` | TABLE | 7 | 7 | 成功 |
| 6 | `t_営業担当マスタ` | `sales_rep_master` | TABLE | 4 | 4 | 成功 |
| 7 | `t_旧機械ID` | `legacy_machine_ids` | TABLE | 96 | 96 | 成功 |
| 8 | `t_材料管理` | `material_orders` | TABLE | 115 | 115 | 成功 |
| 9 | `t_材料納入履歴` | `material_delivery_history` | TABLE | 144 | 144 | 成功 |
| 10 | `t_材質` | `material_types` | TABLE | 85 | 85 | 成功 |
| 11 | `t_機械マスタ` | `machine_master` | TABLE | 57 | 57 | 成功 |
| 12 | `t_段取り者マスタ` | `setup_operator_master` | TABLE | 15 | 15 | 成功 |
| 13 | `t_汎用材料マスタ` | `general_material_master` | TABLE | 0 | 0 | 成功 |
| 14 | `t_汎用材料発注実績` | `general_material_order_results` | TABLE | 0 | 0 | 成功 |
| 15 | `t_注文書データ` | `purchase_order_documents` | TABLE | 2 | 2 | 成功 |
| 16 | `t_生産リリース` | `production_releases` | TABLE | 30336 | 30336 | 成功 |
| 17 | `t_生産リリース のコピー` | `production_releases_backup` | TABLE | 30193 | 30193 | 成功 |
| 18 | `t_生産発注` | `production_orders` | TABLE | 6375 | 6375 | 成功 |
| 19 | `t_発注者マスタ` | `orderer_master` | TABLE | 7 | 7 | 成功 |
| 20 | `t_管理表マスタ` | `management_sheet_master` | TABLE | 1525 | 1525 | 成功 |
| 21 | `t_納入業者` | `suppliers` | TABLE | 13 | 13 | 成功 |
| 22 | `t_送信メールマスタ` | `outbound_email_master` | TABLE | 3 | 3 | 成功 |
| 23 | `t_部品別チャックマスタ` | `part_chuck_master` | TABLE | 1469 | 1469 | 成功 |

## 3. テーブル別カラム対応表

### `t_コントロール` → `app_control`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `管理表更新日時` | DATETIME | `management_sheet_updated_at` | TIMESTAMP | 可 |  |
| 3 | `セット予定表更新日時` | DATETIME | `set_schedule_sheet_updated_at` | TIMESTAMP | 可 |  |
| 4 | `保存フォルダ` | VARCHAR | `save_folder` | VARCHAR(100) | 可 |  |

### `t_セット予定` → `set_schedules`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `セット予定日` | DATETIME | `set_schedule_date` | TIMESTAMP | 可 |  |
| 3 | `機械NO` | VARCHAR | `machine_no` | VARCHAR(4) | 可 |  |
| 4 | `シリアルNO` | VARCHAR | `serial_no` | VARCHAR(10) | 可 |  |
| 5 | `品番` | VARCHAR | `part_no` | VARCHAR(30) | 可 |  |
| 6 | `数量` | INTEGER | `quantity` | INTEGER | 可 |  |
| 7 | `必要最低数` | INTEGER | `minimum_required_qty` | INTEGER | 可 |  |
| 8 | `生産発注数` | INTEGER | `production_order_qty` | INTEGER | 可 |  |
| 9 | `材質材料径` | VARCHAR | `material_diameter` | VARCHAR(40) | 可 |  |
| 10 | `材料使用本数` | INTEGER | `material_bars_used` | INTEGER | 可 |  |
| 11 | `前回秒数` | INTEGER | `previous_cycle_seconds` | INTEGER | 可 |  |
| 12 | `前回日産` | DOUBLE | `previous_daily_output` | DOUBLE PRECISION | 可 |  |
| 13 | `加工予定日数` | DOUBLE | `planned_process_days` | DOUBLE PRECISION | 可 |  |
| 14 | `加工終了日` | DATETIME | `process_end_date` | TIMESTAMP | 可 |  |
| 15 | `管理No` | VARCHAR | `management_no` | VARCHAR(10) | 可 |  |
| 16 | `納期情報` | DATETIME | `delivery_info` | TIMESTAMP | 可 |  |
| 17 | `セット者` | VARCHAR | `setup_operator` | VARCHAR(8) | 可 |  |
| 18 | `備考` | VARCHAR | `remarks` | VARCHAR(50) | 可 |  |

### `t_チャックマスタ` → `chuck_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `型` | VARCHAR | `model_type` | VARCHAR(2) | 可 |  |
| 3 | `種別` | VARCHAR | `category` | VARCHAR(1) | 可 |  |
| 4 | `サイズ` | VARCHAR | `size` | VARCHAR(20) | 可 |  |
| 5 | `数量` | INTEGER | `quantity` | INTEGER | 可 |  |
| 6 | `使用中` | INTEGER | `in_use_count` | INTEGER | 可 |  |

### `t_一時停止` → `production_pauses`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | INTEGER | `id` | INTEGER | 可 |  |
| 2 | `機械NO` | VARCHAR | `machine_no` | VARCHAR(4) | 可 |  |
| 3 | `品番` | VARCHAR | `part_no` | VARCHAR(30) | 可 |  |
| 4 | `停止日` | DATETIME | `pause_date` | TIMESTAMP | 可 |  |

### `t_受信メールマスタ` → `inbound_email_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `納入業者コード` | VARCHAR | `supplier_code` | VARCHAR(2) | 可 |  |
| 2 | `納入業者名` | VARCHAR | `supplier_name` | VARCHAR(20) | 可 |  |
| 3 | `担当者To` | VARCHAR | `contact_to` | VARCHAR(8) | 可 |  |
| 4 | `アドレスTo` | VARCHAR | `address_to` | VARCHAR(50) | 可 |  |
| 5 | `担当者Cc` | VARCHAR | `contact_cc` | VARCHAR(8) | 可 |  |
| 6 | `アドレスCc` | VARCHAR | `address_cc` | VARCHAR(50) | 可 |  |

### `t_営業担当マスタ` → `sales_rep_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | VARCHAR | `id` | VARCHAR(2) | 可 |  |
| 2 | `担当者名` | VARCHAR | `staff_name` | VARCHAR(5) | 可 |  |
| 3 | `表示フラグ` | VARCHAR | `display_flag` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |

### `t_旧機械ID` → `legacy_machine_ids`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `号機` | VARCHAR | `machine_unit` | VARCHAR(4) | 可 |  |
| 2 | `機械ID` | VARCHAR | `machine_id` | VARCHAR(4) | 可 |  |

### `t_材料管理` → `material_orders`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `管理NO` | VARCHAR | `management_no` | VARCHAR(10) | 可 |  |
| 3 | `品番` | VARCHAR | `part_no` | VARCHAR(30) | 可 |  |
| 4 | `製品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 5 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 6 | `数量` | INTEGER | `quantity` | INTEGER | 可 |  |
| 7 | `材質材料径` | VARCHAR | `material_diameter` | VARCHAR(40) | 可 |  |
| 8 | `手配日` | DATETIME | `arrangement_date` | TIMESTAMP | 可 |  |
| 9 | `納期` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 10 | `必要本数` | DOUBLE | `required_bars` | DOUBLE PRECISION | 可 |  |
| 11 | `発注本数` | DOUBLE | `ordered_bars` | DOUBLE PRECISION | 可 |  |
| 12 | `単位` | VARCHAR | `unit` | VARCHAR(1) | 可 |  |
| 13 | `引当本数` | DOUBLE | `allocated_bars` | DOUBLE PRECISION | 可 |  |
| 14 | `納入済数` | INTEGER | `delivered_qty` | INTEGER | 可 |  |
| 15 | `入荷残` | INTEGER | `remaining_receipt_qty` | INTEGER | 可 |  |
| 16 | `歩留` | DOUBLE | `yield_rate` | DOUBLE PRECISION | 可 |  |
| 17 | `納期回答` | DATETIME | `delivery_response_date` | TIMESTAMP | 可 |  |
| 18 | `発注先コード` | VARCHAR | `vendor_code` | VARCHAR(2) | 可 |  |
| 19 | `発注先名` | VARCHAR | `vendor_name` | VARCHAR(20) | 可 |  |
| 20 | `手配済フラグ` | VARCHAR | `arranged_flag` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |
| 21 | `注文書印刷済フラグ` | VARCHAR | `purchase_order_printed_flag` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |
| 22 | `材料入荷完了フラグ` | VARCHAR | `material_receipt_completed_flag` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |

### `t_材料納入履歴` → `material_delivery_history`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `管理NO` | VARCHAR | `management_no` | VARCHAR(10) | 可 |  |
| 3 | `入荷日` | DATETIME | `receipt_date` | TIMESTAMP | 可 |  |
| 4 | `伝票日付` | DATETIME | `slip_date` | TIMESTAMP | 可 |  |
| 5 | `区分` | VARCHAR | `category_code` | VARCHAR(1) | 可 |  |
| 6 | `納入業者コード` | VARCHAR | `supplier_code` | VARCHAR(2) | 可 |  |
| 7 | `納入業者名` | VARCHAR | `supplier_name` | VARCHAR(20) | 可 |  |
| 8 | `購入月` | VARCHAR | `purchase_month` | VARCHAR(4) | 可 |  |
| 9 | `品種` | VARCHAR | `material_kind` | VARCHAR(15) | 可 |  |
| 10 | `材質材料径` | VARCHAR | `material_diameter` | VARCHAR(40) | 可 |  |
| 11 | `サイズ` | VARCHAR | `size` | VARCHAR(5) | 可 |  |
| 12 | `本数` | DOUBLE | `bar_count` | DOUBLE PRECISION | 可 |  |
| 13 | `重量` | DOUBLE | `weight` | DOUBLE PRECISION | 可 |  |
| 14 | `単価` | INTEGER | `unit_price` | INTEGER | 可 |  |
| 15 | `金額` | CURRENCY | `amount` | NUMERIC | 可 |  |
| 16 | `ロット番号` | VARCHAR | `lot_no` | VARCHAR(30) | 可 |  |
| 17 | `入荷場所` | VARCHAR | `receipt_location` | VARCHAR(10) | 可 |  |
| 18 | `備考` | VARCHAR | `remarks` | VARCHAR(30) | 可 |  |

### `t_材質` → `material_types`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `材質` | VARCHAR | `material_type` | VARCHAR(20) | 可 |  |
| 2 | `記号` | VARCHAR | `symbol` | VARCHAR(1) | 可 |  |

### `t_機械マスタ` → `machine_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `シリアルNO` | VARCHAR | `serial_no` | VARCHAR(10) | 可 |  |
| 2 | `機械NO` | VARCHAR | `machine_no` | VARCHAR(4) | 可 |  |
| 3 | `機種` | VARCHAR | `machine_model` | VARCHAR(10) | 可 |  |
| 4 | `仕様` | VARCHAR | `specification` | VARCHAR(10) | 可 |  |
| 5 | `型` | VARCHAR | `model_type` | VARCHAR(2) | 可 |  |
| 6 | `ソートキー` | VARCHAR | `sort_key` | VARCHAR(4) | 可 |  |

### `t_段取り者マスタ` → `setup_operator_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | VARCHAR | `id` | VARCHAR(2) | 可 |  |
| 2 | `段取り者` | VARCHAR | `setup_operator_name` | VARCHAR(10) | 可 |  |
| 3 | `表示フラグ` | VARCHAR | `display_flag` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |

### `t_汎用材料マスタ` → `general_material_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `材質材料径` | VARCHAR | `material_diameter` | VARCHAR(40) | 可 |  |
| 3 | `納入業者コード` | VARCHAR | `supplier_code` | VARCHAR(2) | 可 |  |
| 4 | `納入業者名` | VARCHAR | `supplier_name` | VARCHAR(20) | 可 |  |
| 5 | `備考` | VARCHAR | `remarks` | VARCHAR(10) | 可 |  |
| 6 | `使用フラグ` | VARCHAR | `active_flag` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |

### `t_汎用材料発注実績` → `general_material_order_results`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `発注日` | DATETIME | `order_date` | TIMESTAMP | 可 |  |
| 3 | `材質材料径` | VARCHAR | `material_diameter` | VARCHAR(40) | 可 |  |
| 4 | `納入業者コード` | VARCHAR | `supplier_code` | VARCHAR(2) | 可 |  |
| 5 | `数量` | DOUBLE | `quantity` | DOUBLE PRECISION | 可 |  |
| 6 | `単位` | VARCHAR | `unit` | VARCHAR(1) | 可 |  |
| 7 | `納期` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |

### `t_注文書データ` → `purchase_order_documents`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `発注業者コード` | VARCHAR | `order_vendor_code` | VARCHAR(2) | 可 |  |
| 3 | `材料テーブルID` | INTEGER | `material_table_id` | INTEGER | 可 |  |
| 4 | `材料名` | VARCHAR | `material_name` | VARCHAR(40) | 可 |  |
| 5 | `管理NO` | VARCHAR | `management_no` | VARCHAR(10) | 可 |  |
| 6 | `数量` | DOUBLE | `quantity` | DOUBLE PRECISION | 可 |  |
| 7 | `単位` | VARCHAR | `unit` | VARCHAR(1) | 可 |  |
| 8 | `納期` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |

### `t_生産リリース` → `production_releases`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `セット日` | DATETIME | `setup_date` | TIMESTAMP | 可 |  |
| 3 | `加工終了日` | DATETIME | `process_end_date` | TIMESTAMP | 可 |  |
| 4 | `機械NO` | VARCHAR | `machine_no` | VARCHAR(4) | 可 |  |
| 5 | `機種` | VARCHAR | `machine_model` | VARCHAR(10) | 可 |  |
| 6 | `仕様` | VARCHAR | `specification` | VARCHAR(10) | 可 |  |
| 7 | `シリアルNO` | VARCHAR | `serial_no` | VARCHAR(10) | 可 |  |
| 8 | `品番` | VARCHAR | `part_no` | VARCHAR(30) | 可 |  |
| 9 | `製品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 10 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 11 | `数量` | INTEGER | `quantity` | INTEGER | 可 |  |
| 12 | `材質材料径` | VARCHAR | `material_diameter` | VARCHAR(40) | 可 |  |
| 13 | `製品全長` | DOUBLE | `product_total_length` | DOUBLE PRECISION | 可 |  |
| 14 | `突切り幅` | DOUBLE | `cutoff_width` | DOUBLE PRECISION | 可 |  |
| 15 | `加工秒数` | INTEGER | `process_seconds` | INTEGER | 可 |  |
| 16 | `日産数` | DOUBLE | `daily_output_qty` | DOUBLE PRECISION | 可 |  |
| 17 | `寸法出しH` | DOUBLE | `dimension_setup_h` | DOUBLE PRECISION | 可 |  |
| 18 | `加工予定日数` | DOUBLE | `planned_process_days` | DOUBLE PRECISION | 可 |  |
| 19 | `必要最低数` | INTEGER | `minimum_required_qty` | INTEGER | 可 |  |
| 20 | `管理NO` | VARCHAR | `management_no` | VARCHAR(10) | 可 |  |
| 21 | `納期情報` | DATETIME | `delivery_info` | TIMESTAMP | 可 |  |
| 22 | `セット者` | VARCHAR | `setup_operator` | VARCHAR(8) | 可 |  |
| 23 | `加工完了日` | DATETIME | `process_completed_date` | TIMESTAMP | 可 |  |
| 24 | `完了フラグ` | VARCHAR | `completion_flag` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |

### `t_生産リリース のコピー` → `production_releases_backup`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `セット日` | DATETIME | `setup_date` | TIMESTAMP | 可 |  |
| 3 | `加工終了日` | DATETIME | `process_end_date` | TIMESTAMP | 可 |  |
| 4 | `機械NO` | VARCHAR | `machine_no` | VARCHAR(4) | 可 |  |
| 5 | `機種` | VARCHAR | `machine_model` | VARCHAR(10) | 可 |  |
| 6 | `仕様` | VARCHAR | `specification` | VARCHAR(10) | 可 |  |
| 7 | `シリアルNO` | VARCHAR | `serial_no` | VARCHAR(10) | 可 |  |
| 8 | `品番` | VARCHAR | `part_no` | VARCHAR(30) | 可 |  |
| 9 | `製品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 10 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 11 | `数量` | INTEGER | `quantity` | INTEGER | 可 |  |
| 12 | `材質材料径` | VARCHAR | `material_diameter` | VARCHAR(40) | 可 |  |
| 13 | `製品全長` | DOUBLE | `product_total_length` | DOUBLE PRECISION | 可 |  |
| 14 | `突切り幅` | DOUBLE | `cutoff_width` | DOUBLE PRECISION | 可 |  |
| 15 | `加工秒数` | INTEGER | `process_seconds` | INTEGER | 可 |  |
| 16 | `日産数` | DOUBLE | `daily_output_qty` | DOUBLE PRECISION | 可 |  |
| 17 | `寸法出しH` | DOUBLE | `dimension_setup_h` | DOUBLE PRECISION | 可 |  |
| 18 | `加工予定日数` | DOUBLE | `planned_process_days` | DOUBLE PRECISION | 可 |  |
| 19 | `必要最低数` | INTEGER | `minimum_required_qty` | INTEGER | 可 |  |
| 20 | `管理NO` | VARCHAR | `management_no` | VARCHAR(10) | 可 |  |
| 21 | `納期情報` | DATETIME | `delivery_info` | TIMESTAMP | 可 |  |
| 22 | `セット者` | VARCHAR | `setup_operator` | VARCHAR(8) | 可 |  |
| 23 | `加工完了日` | DATETIME | `process_completed_date` | TIMESTAMP | 可 |  |
| 24 | `完了フラグ` | VARCHAR | `completion_flag` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |

### `t_生産発注` → `production_orders`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `発注日` | DATETIME | `order_date` | TIMESTAMP | 可 |  |
| 3 | `出力日` | DATETIME | `export_date` | TIMESTAMP | 可 |  |
| 4 | `品番` | VARCHAR | `part_no` | VARCHAR(30) | 可 |  |
| 5 | `製品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 6 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 7 | `受注残数` | INTEGER | `backorder_qty` | INTEGER | 可 |  |
| 8 | `在庫` | INTEGER | `stock_qty` | INTEGER | 可 |  |
| 9 | `受注数` | INTEGER | `order_qty` | INTEGER | 可 |  |
| 10 | `注文数` | INTEGER | `purchase_qty` | INTEGER | 可 |  |
| 11 | `適正在庫` | INTEGER | `optimal_stock_qty` | INTEGER | 可 |  |
| 12 | `納期` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 13 | `発注者` | VARCHAR | `orderer` | VARCHAR(5) | 可 |  |
| 14 | `営業担当` | VARCHAR | `sales_rep` | VARCHAR(5) | 可 |  |
| 15 | `区分` | VARCHAR | `category_code` | VARCHAR(4) | 可 |  |
| 16 | `備考` | VARCHAR | `remarks` | VARCHAR(15) | 可 |  |
| 17 | `Expフラグ` | BIT | `exp_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 18 | `営業承認` | BIT | `sales_approved` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 19 | `Impフラグ` | BIT | `imp_flag` | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |
| 20 | `Imp日` | DATETIME | `imp_date` | TIMESTAMP | 可 |  |

### `t_発注者マスタ` → `orderer_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | VARCHAR | `id` | VARCHAR(2) | 可 |  |
| 2 | `発注者名` | VARCHAR | `orderer_name` | VARCHAR(5) | 可 |  |
| 3 | `表示フラグ` | VARCHAR | `display_flag` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |

### `t_管理表マスタ` → `management_sheet_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `製品番号` | VARCHAR | `product_code` | VARCHAR(30) | 可 |  |
| 2 | `製品名` | VARCHAR | `product_name` | VARCHAR(30) | 可 |  |
| 3 | `客先名` | VARCHAR | `customer_name` | VARCHAR(30) | 可 |  |
| 4 | `営業担当` | VARCHAR | `sales_rep` | VARCHAR(5) | 可 |  |
| 5 | `材質材料径` | VARCHAR | `material_diameter` | VARCHAR(40) | 可 |  |
| 6 | `次工程` | VARCHAR | `next_process` | VARCHAR(25) | 可 |  |
| 7 | `条件他` | VARCHAR | `other_conditions` | VARCHAR(50) | 可 |  |
| 8 | `前回秒数` | INTEGER | `previous_cycle_seconds` | INTEGER | 可 |  |
| 9 | `前回日産` | DOUBLE | `previous_daily_output` | DOUBLE PRECISION | 可 |  |
| 10 | `前回加工機` | VARCHAR | `previous_machine_no` | VARCHAR(4) | 可 |  |
| 11 | `前回加工日` | DATETIME | `previous_process_date` | TIMESTAMP | 可 |  |
| 12 | `取り数` | DOUBLE | `pieces_per_set` | DOUBLE PRECISION | 可 |  |
| 13 | `在庫保管場所` | VARCHAR | `stock_location` | VARCHAR(10) | 可 |  |
| 14 | `納期` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 15 | `受注残数` | INTEGER | `backorder_qty` | INTEGER | 可 |  |
| 16 | `在庫` | INTEGER | `stock_qty` | INTEGER | 可 |  |
| 17 | `仕掛在庫` | INTEGER | `wip_stock_qty` | INTEGER | 可 |  |
| 18 | `指示書有無` | VARCHAR | `has_work_order` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |
| 19 | `材料識別` | INTEGER | `material_identification` | INTEGER | 可 |  |

### `t_納入業者` → `suppliers`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `納入業者コード` | VARCHAR | `supplier_code` | VARCHAR(2) | 可 |  |
| 2 | `納入業者名` | VARCHAR | `supplier_name` | VARCHAR(20) | 可 |  |
| 3 | `締日` | VARCHAR | `closing_day` | VARCHAR(2) | 可 |  |
| 4 | `計算方法` | VARCHAR | `calculation_method` | VARCHAR(1) | 可 |  |
| 5 | `宛名` | VARCHAR | `addressee` | VARCHAR(20) | 可 |  |

### `t_送信メールマスタ` → `outbound_email_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `担当者名` | VARCHAR | `staff_name` | VARCHAR(8) | 可 |  |
| 3 | `アドレス` | VARCHAR | `email_address` | VARCHAR(50) | 可 |  |
| 4 | `パスワード` | VARCHAR | `password` | VARCHAR(20) | 可 |  |
| 5 | `主担当フラグ` | VARCHAR | `primary_contact_flag` | VARCHAR(1) | 可 | Access上でVARCHAR(1)相当のため文字列で保持 |

### `t_部品別チャックマスタ` → `part_chuck_master`

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | `品番` | VARCHAR | `part_no` | VARCHAR(30) | 可 |  |
| 3 | `型` | VARCHAR | `model_type` | VARCHAR(2) | 可 |  |
| 4 | `種別` | VARCHAR | `category` | VARCHAR(1) | 可 |  |
| 5 | `サイズ` | VARCHAR | `size` | VARCHAR(20) | 可 |  |

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

- 本移行はバックエンド実体 `セット予定材料管理DB.accdb` の23テーブルを対象としています。
- フロント .accdb にリンクされる `t_受注`・`管理表マスター`（Excel）等は別DBのため本移行対象外です。
- AccessのFKメタデータはODBCで取得できなかったため、外部キー制約は作成していません。
- フラグ列の多くはAccess上でVARCHAR(1)のため、booleanへ変換せず文字列で保持しています。
- `t_生産リリース のコピー` はバックアップ用途のスナップショットテーブルです。
- 0件テーブルも構造再現のため作成しています: `t_一時停止`, `t_汎用材料マスタ`, `t_汎用材料発注実績`
