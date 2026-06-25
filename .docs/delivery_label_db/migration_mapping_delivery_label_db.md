# Access → PostgreSQL 移行対応表

## 1. 移行概要

- 対象Access DB：\\192.168.1.200\共有\QRシステム\Access\現品票DB.accdb
- 移行先PostgreSQL DB：delivery_label_db
- 接続情報：
  - `.env` の DATABASE_URL を参照
- 移行日：2026-06-25 13:44:49
- 作成者：Codex
- 備考：現品票DBの15テーブルを忠実に移行。日本語名はPostgreSQL用に英語/ローマ字のスネークケースへ変換し、元名はコメントと本対応表で追跡可能。

## 2. 移行対象テーブル一覧

| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | t_ExcelQR履歴 | excel_qr_history | TABLE | 0 | 0 | 成功 |
| 2 | t_Excel現品票履歴 | excel_delivery_label_history | TABLE | 35817 | 35817 | 成功 |
| 3 | t_ID番号 | id_number | TABLE | 1 | 1 | 成功 |
| 4 | t_QR履歴 | qr_history | TABLE | 115803 | 115803 | 成功 |
| 5 | t_エラーログ | error_logs | TABLE | 16622 | 16622 | 成功 |
| 6 | t_ロット完了理由 | lot_completion_reasons | TABLE | 6 | 6 | 成功 |
| 7 | t_作業履歴 | work_history | TABLE | 1 | 1 | 成功 |
| 8 | t_修正ログ | correction_logs | TABLE | 9992 | 9992 | 成功 |
| 9 | t_分割ロット | split_lots | TABLE | 7630 | 7630 | 成功 |
| 10 | t_工程マスタ | process_master | TABLE | 5 | 5 | 成功 |
| 11 | t_数量差異 | quantity_differences | TABLE | 78357 | 78357 | 成功 |
| 12 | t_現品票不具合内容 | delivery_label_defect_details | TABLE | 165 | 165 | 成功 |
| 13 | t_現品票履歴 | delivery_label_history | TABLE | 136615 | 136615 | 成功 |

## 3. テーブル別カラム対応表

### Accessテーブル名：t_ExcelQR履歴
### PostgreSQLテーブル名：excel_qr_history

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 日付時刻 | DATETIME | date_time | TIMESTAMP | 可 |  |
| 2 | QRコード | VARCHAR | qr_code | VARCHAR(22) | 可 |  |
| 3 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 4 | 日付 | DATETIME | date_value | TIMESTAMP | 可 |  |
| 5 | 工程 | VARCHAR | process | VARCHAR(2) | 可 |  |
| 6 | 位置 | VARCHAR | position | VARCHAR(2) | 可 |  |
| 7 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 8 | 工程名 | VARCHAR | process_name | VARCHAR(30) | 可 |  |

### Accessテーブル名：t_Excel現品票履歴
### PostgreSQLテーブル名：excel_delivery_label_history

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 2 | 号機 | VARCHAR | machine_no | VARCHAR(5) | 可 |  |
| 3 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 4 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 5 | 客先 | VARCHAR | customer | VARCHAR(30) | 可 |  |
| 6 | 材質 | VARCHAR | material | VARCHAR(50) | 可 |  |
| 7 | 材料ロットNO | VARCHAR | material_lot_no | VARCHAR(30) | 可 |  |
| 8 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 9 | 備考 | VARCHAR | remarks | VARCHAR(50) | 可 |  |
| 10 | 指示日 | DATETIME | instruction_date | TIMESTAMP | 可 |  |
| 11 | 完了フラグ | VARCHAR | completion_flag | VARCHAR(1) | 可 |  |

### Accessテーブル名：t_ID番号
### PostgreSQLテーブル名：id_number

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | P番号 | INTEGER | p_number | INTEGER | 可 |  |
| 3 | E番号 | INTEGER | e_number | INTEGER | 可 |  |

### Accessテーブル名：t_QR履歴
### PostgreSQLテーブル名：qr_history

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 日付時刻 | DATETIME | date_time | TIMESTAMP | 可 |  |
| 2 | QRコード | VARCHAR | qr_code | VARCHAR(22) | 可 |  |
| 3 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 4 | 日付 | DATETIME | date_value | TIMESTAMP | 可 |  |
| 5 | 工程 | VARCHAR | process | VARCHAR(2) | 可 |  |
| 6 | 位置 | VARCHAR | position | VARCHAR(2) | 可 |  |
| 7 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 8 | 工程コード | VARCHAR | process_code | VARCHAR(2) | 可 |  |
| 9 | 工程名 | VARCHAR | process_name | VARCHAR(30) | 可 |  |
| 10 | 更新フラグ | VARCHAR | update_flag | VARCHAR(1) | 可 |  |
| 11 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |

### Accessテーブル名：t_エラーログ
### PostgreSQLテーブル名：error_logs

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 日付 | DATETIME | date_value | TIMESTAMP | 可 |  |
| 3 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 4 | エラー内容 | VARCHAR | error_detail | VARCHAR(20) | 可 |  |

### Accessテーブル名：t_ロット完了理由
### PostgreSQLテーブル名：lot_completion_reasons

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 理由コード | VARCHAR | reason_code | VARCHAR(1) | 可 |  |
| 2 | 理由 | VARCHAR | reason | VARCHAR(5) | 可 |  |

### Accessテーブル名：t_作業履歴
### PostgreSQLテーブル名：work_history

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | ロット数数値検査 | INTEGER | lot_count_numeric_inspection | INTEGER | 可 |  |
| 3 | ロット数外観検査 | INTEGER | lot_count_appearance_inspection | INTEGER | 可 |  |
| 4 | ロット数梱包 | INTEGER | lot_count_packaging | INTEGER | 可 |  |
| 5 | ロット数洗浄 | INTEGER | lot_count_washing | INTEGER | 可 |  |
| 6 | ロット数二次作業 | INTEGER | lot_count_secondary_work | INTEGER | 可 |  |
| 7 | 個数数値検査 | INTEGER | quantity_numeric_inspection | INTEGER | 可 |  |
| 8 | 個数外観検査 | INTEGER | quantity_appearance_inspection | INTEGER | 可 |  |
| 9 | 個数梱包 | INTEGER | quantity_packaging | INTEGER | 可 |  |
| 10 | 個数洗浄 | INTEGER | quantity_washing | INTEGER | 可 |  |
| 11 | 個数二次作業 | INTEGER | quantity_secondary_work | INTEGER | 可 |  |
| 12 | 金額数値検査 | DOUBLE | amount_numeric_inspection | DOUBLE PRECISION | 可 |  |
| 13 | 金額外観検査 | DOUBLE | amount_appearance_inspection | DOUBLE PRECISION | 可 |  |
| 14 | 金額梱包 | DOUBLE | amount_packaging | DOUBLE PRECISION | 可 |  |
| 15 | 金額洗浄 | DOUBLE | amount_washing | DOUBLE PRECISION | 可 |  |
| 16 | 金額二次作業 | DOUBLE | amount_secondary_work | DOUBLE PRECISION | 可 |  |
| 17 | 稼働日数 | INTEGER | operating_days | INTEGER | 可 |  |

### Accessテーブル名：t_修正ログ
### PostgreSQLテーブル名：correction_logs

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 日付 | DATETIME | date_value | TIMESTAMP | 可 |  |
| 3 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 4 | 項目 | VARCHAR | item | VARCHAR(5) | 可 |  |
| 5 | 内容 | VARCHAR | content | VARCHAR(15) | 可 |  |

### Accessテーブル名：t_分割ロット
### PostgreSQLテーブル名：split_lots

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 元ロットID | VARCHAR | source_lot_id | VARCHAR(7) | 可 |  |
| 3 | 新ロットID | VARCHAR | new_lot_id | VARCHAR(7) | 可 |  |
| 4 | 元数量 | INTEGER | source_quantity | INTEGER | 可 |  |
| 5 | 区分 | VARCHAR | category | VARCHAR(1) | 可 |  |
| 6 | 作成日 | DATETIME | created_date | TIMESTAMP | 可 |  |

### Accessテーブル名：t_工程マスタ
### PostgreSQLテーブル名：process_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 工程コード | VARCHAR | process_code | VARCHAR(2) | 可 |  |
| 2 | 工程名 | VARCHAR | process_name | VARCHAR(5) | 可 |  |

### Accessテーブル名：t_数量差異
### PostgreSQLテーブル名：quantity_differences

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 計量日 | DATETIME | weighing_date | TIMESTAMP | 可 |  |
| 3 | 出荷日 | DATETIME | shipping_date | TIMESTAMP | 可 |  |
| 4 | 号機 | VARCHAR | machine_no | VARCHAR(4) | 可 |  |
| 5 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 6 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 7 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 8 | 出荷数 | INTEGER | shipped_quantity | INTEGER | 可 |  |
| 9 | 計量数 | INTEGER | weighed_quantity | INTEGER | 可 |  |
| 10 | 差異 | DOUBLE | difference | DOUBLE PRECISION | 可 |  |

### Accessテーブル名：t_現品票不具合内容
### PostgreSQLテーブル名：delivery_label_defect_details

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 不可 | PRIMARY KEY |
| 2 | 不具合内容 | VARCHAR | defect_detail | VARCHAR(15) | 可 |  |
| 3 | 処置内容 | VARCHAR | action_detail | VARCHAR(15) | 可 |  |
| 4 | 処置済 | VARCHAR | action_completed | VARCHAR(1) | 可 |  |

### Accessテーブル名：t_現品票履歴
### PostgreSQLテーブル名：delivery_label_history

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 不可 | PRIMARY KEY |
| 2 | 号機 | VARCHAR | machine_no | VARCHAR(5) | 可 |  |
| 3 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 4 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 5 | 客先 | VARCHAR | customer | VARCHAR(30) | 可 |  |
| 6 | 材質 | VARCHAR | material | VARCHAR(50) | 可 |  |
| 7 | 材料ロットNO | VARCHAR | material_lot_no | VARCHAR(30) | 可 |  |
| 8 | 機械担当者 | VARCHAR | machine_operator | VARCHAR(10) | 可 |  |
| 9 | 営業担当者 | VARCHAR | sales_representative | VARCHAR(5) | 可 |  |
| 10 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 11 | 現在工程名 | VARCHAR | current_process_name | VARCHAR(30) | 可 |  |
| 12 | 現在工程コード | VARCHAR | current_process_code | VARCHAR(2) | 可 |  |
| 13 | 工程2 | VARCHAR | process_2 | VARCHAR(30) | 可 |  |
| 14 | 工程3 | VARCHAR | process_3 | VARCHAR(30) | 可 |  |
| 15 | 工程4 | VARCHAR | process_4 | VARCHAR(30) | 可 |  |
| 16 | 工程5 | VARCHAR | process_5 | VARCHAR(30) | 可 |  |
| 17 | 工程6 | VARCHAR | process_6 | VARCHAR(30) | 可 |  |
| 18 | 工程7 | VARCHAR | process_7 | VARCHAR(30) | 可 |  |
| 19 | 工程8 | VARCHAR | process_8 | VARCHAR(30) | 可 |  |
| 20 | 工程9 | VARCHAR | process_9 | VARCHAR(30) | 可 |  |
| 21 | 現在工程番号 | INTEGER | current_process_number | INTEGER | 可 |  |
| 22 | 表面処理工程番号 | INTEGER | surface_treatment_process_number | INTEGER | 可 |  |
| 23 | 位置 | VARCHAR | position | VARCHAR(2) | 可 |  |
| 24 | 品番ID | VARCHAR | product_code_id | VARCHAR(6) | 可 |  |
| 25 | QRコード | VARCHAR | qr_code | VARCHAR(30) | 可 |  |
| 26 | 備考 | VARCHAR | remarks | VARCHAR(30) | 可 |  |
| 27 | 指示日 | DATETIME | instruction_date | TIMESTAMP | 可 |  |
| 28 | 印刷日 | DATETIME | printed_date | TIMESTAMP | 可 |  |
| 29 | 完了日 | DATETIME | completed_date | TIMESTAMP | 可 |  |
| 30 | 発行フラグ | VARCHAR | issue_flag | VARCHAR(1) | 可 |  |
| 31 | 不適合品フラグ | VARCHAR | nonconforming_product_flag | VARCHAR(1) | 可 |  |
| 32 | 不適合品数量 | INTEGER | nonconforming_product_quantity | INTEGER | 可 |  |
| 33 | 処理済フラグ | VARCHAR | processed_flag | VARCHAR(1) | 可 |  |
| 34 | 完了フラグ | VARCHAR | completion_flag | VARCHAR(1) | 可 |  |
| 35 | 工程2備考 | VARCHAR | process_2_remarks | VARCHAR(20) | 可 |  |
| 36 | 工程3備考 | VARCHAR | process_3_remarks | VARCHAR(20) | 可 |  |
| 37 | 工程4備考 | VARCHAR | process_4_remarks | VARCHAR(20) | 可 |  |
| 38 | 工程5備考 | VARCHAR | process_5_remarks | VARCHAR(20) | 可 |  |
| 39 | 工程6備考 | VARCHAR | process_6_remarks | VARCHAR(20) | 可 |  |
| 40 | 工程7備考 | VARCHAR | process_7_remarks | VARCHAR(20) | 可 |  |
| 41 | 工程8備考 | VARCHAR | process_8_remarks | VARCHAR(20) | 可 |  |
| 42 | 工程9備考 | VARCHAR | process_9_remarks | VARCHAR(20) | 可 |  |
| 43 | 材料識別 | INTEGER | material_identification | INTEGER | 可 |  |

## 4. 主キー・インデックス情報

| Accessテーブル名 | PostgreSQLテーブル名 | 主キー | インデックス | 備考 |
|---|---|---|---|---|
| t_ExcelQR履歴 | excel_qr_history | 検出なし | 検出なし | FKは未検出 |
| t_Excel現品票履歴 | excel_delivery_label_history | 検出なし | 検出なし | FKは未検出 |
| t_ID番号 | id_number | 検出なし | 検出なし | FKは未検出 |
| t_QR履歴 | qr_history | 検出なし | 検出なし | FKは未検出 |
| t_エラーログ | error_logs | 検出なし | 検出なし | FKは未検出 |
| t_ロット完了理由 | lot_completion_reasons | 検出なし | 検出なし | FKは未検出 |
| t_作業履歴 | work_history | 検出なし | 検出なし | FKは未検出 |
| t_修正ログ | correction_logs | 検出なし | 検出なし | FKは未検出 |
| t_分割ロット | split_lots | 検出なし | 検出なし | FKは未検出 |
| t_工程マスタ | process_master | 検出なし | 検出なし | FKは未検出 |
| t_数量差異 | quantity_differences | 検出なし | 検出なし | FKは未検出 |
| t_現品票不具合内容 | delivery_label_defect_details | production_lot_id | 検出なし | FKは未検出 |
| t_現品票履歴 | delivery_label_history | production_lot_id | 検出なし | FKは未検出 |

## 5. 型変換ルール

| Access型 | PostgreSQL型 | 備考 |
|---|---|---|
| VARCHAR | varchar(n) | Accessのサイズを維持 |
| COUNTER | bigserial | AccessのID値を投入後、setvalで次採番をMAX(id)+1に同期。PRIMARY KEY付与 |
| INTEGER | integer | 整数 |
| DOUBLE | double precision | 浮動小数 |
| DATETIME | timestamp | Accessの日付/時刻を保持 |
| BIT | boolean | Yes/No型 |

## 6. アプリ接続時の参照情報

### 接続先

```text
.env の DATABASE_URL を使用
```

### 主に参照するテーブル

| 用途 | PostgreSQLテーブル名 | 主なキー | 備考 |
| -- | --------------- | ---- | -- |
| QR履歴 | excel_qr_history | qr_code, production_lot_id, date_time | 元 t_ExcelQR履歴 |
| 現品票履歴 | excel_delivery_label_history | production_lot_id, product_code | 元 t_Excel現品票履歴 |
| 参照テーブル | id_number | id | 元 t_ID番号 |
| QR履歴 | qr_history | id, qr_code, production_lot_id, process_code, date_time | 元 t_QR履歴 |
| ログ | error_logs | id, production_lot_id | 元 t_エラーログ |
| 参照テーブル | lot_completion_reasons | 要確認 | 元 t_ロット完了理由 |
| 参照テーブル | work_history | id | 元 t_作業履歴 |
| ログ | correction_logs | id, production_lot_id | 元 t_修正ログ |
| 参照テーブル | split_lots | id | 元 t_分割ロット |
| 工程マスタ | process_master | process_code | 元 t_工程マスタ |
| 数量差異 | quantity_differences | id, production_lot_id, product_code | 元 t_数量差異 |
| 現品票不具合 | delivery_label_defect_details | production_lot_id | 元 t_現品票不具合内容 |
| 現品票履歴 | delivery_label_history | qr_code, production_lot_id, product_code | 元 t_現品票履歴 |

### 主要カラム

| 用途 | PostgreSQLテーブル名 | PostgreSQLカラム名 | 元Accessカラム名 | 備考 |
| -- | --------------- | -------------- | ----------- | -- |
| 日時 | excel_qr_history | date_time | 日付時刻 | Accessの値をそのまま保持 |
| QRコード | excel_qr_history | qr_code | QRコード | Accessの値をそのまま保持 |
| 生産ロット | excel_qr_history | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 日付 | excel_qr_history | date_value | 日付 | Accessの値をそのまま保持 |
| 工程 | excel_qr_history | process | 工程 | Accessの値をそのまま保持 |
| 位置 | excel_qr_history | position | 位置 | Accessの値をそのまま保持 |
| 数量 | excel_qr_history | quantity | 数量 | Accessの値をそのまま保持 |
| 工程名 | excel_qr_history | process_name | 工程名 | Accessの値をそのまま保持 |
| 生産ロット | excel_delivery_label_history | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 品番 | excel_delivery_label_history | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | excel_delivery_label_history | product_name | 品名 | Accessの値をそのまま保持 |
| 客先 | excel_delivery_label_history | customer | 客先 | Accessの値をそのまま保持 |
| 数量 | excel_delivery_label_history | quantity | 数量 | Accessの値をそのまま保持 |
| 指示日 | excel_delivery_label_history | instruction_date | 指示日 | Accessの値をそのまま保持 |
| ID | id_number | id | ID | Accessの値をそのまま保持 |
| 日時 | qr_history | date_time | 日付時刻 | Accessの値をそのまま保持 |
| QRコード | qr_history | qr_code | QRコード | Accessの値をそのまま保持 |
| 生産ロット | qr_history | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 日付 | qr_history | date_value | 日付 | Accessの値をそのまま保持 |
| 工程 | qr_history | process | 工程 | Accessの値をそのまま保持 |
| 位置 | qr_history | position | 位置 | Accessの値をそのまま保持 |
| 数量 | qr_history | quantity | 数量 | Accessの値をそのまま保持 |
| 工程コード | qr_history | process_code | 工程コード | Accessの値をそのまま保持 |
| 工程名 | qr_history | process_name | 工程名 | Accessの値をそのまま保持 |
| ID | qr_history | id | ID | Accessの値をそのまま保持 |
| ID | error_logs | id | ID | Accessの値をそのまま保持 |
| 日付 | error_logs | date_value | 日付 | Accessの値をそのまま保持 |
| 生産ロット | error_logs | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| ID | work_history | id | ID | Accessの値をそのまま保持 |
| ID | correction_logs | id | ID | Accessの値をそのまま保持 |
| 日付 | correction_logs | date_value | 日付 | Accessの値をそのまま保持 |
| 生産ロット | correction_logs | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| ID | split_lots | id | ID | Accessの値をそのまま保持 |
| 工程コード | process_master | process_code | 工程コード | Accessの値をそのまま保持 |
| 工程名 | process_master | process_name | 工程名 | Accessの値をそのまま保持 |
| ID | quantity_differences | id | ID | Accessの値をそのまま保持 |
| 生産ロット | quantity_differences | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 品番 | quantity_differences | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | quantity_differences | product_name | 品名 | Accessの値をそのまま保持 |
| 生産ロット | delivery_label_defect_details | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 生産ロット | delivery_label_history | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 品番 | delivery_label_history | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | delivery_label_history | product_name | 品名 | Accessの値をそのまま保持 |
| 客先 | delivery_label_history | customer | 客先 | Accessの値をそのまま保持 |
| 数量 | delivery_label_history | quantity | 数量 | Accessの値をそのまま保持 |
| 現在工程名 | delivery_label_history | current_process_name | 現在工程名 | Accessの値をそのまま保持 |
| 現在工程コード | delivery_label_history | current_process_code | 現在工程コード | Accessの値をそのまま保持 |
| 位置 | delivery_label_history | position | 位置 | Accessの値をそのまま保持 |
| QRコード | delivery_label_history | qr_code | QRコード | Accessの値をそのまま保持 |
| 指示日 | delivery_label_history | instruction_date | 指示日 | Accessの値をそのまま保持 |

## 7. 注意事項・要確認事項

- AccessのFKメタデータはODBCドライバが返さなかったため、外部キー制約は作成していません。
- COUNTER列はBIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期しています。
- 移行対象外: `t_QR履歴(backup_260521)` / `t_QR履歴Tmp`（バックアップ・一時テーブルのため PostgreSQL へは移行しません）。
- `delivery_label_defect_details` / `delivery_label_history` は `production_lot_id` を PRIMARY KEY（NOT NULL・重複なし）としています。
- `.env` の `ACCESS_DB_PATH` が実ファイルを指していない場合は、メタJSONの `database_path` を使用しています。
- 0件テーブルも構造再現のため作成しています: t_ExcelQR履歴
- メタ抽出警告：FK 取得スキップ: t_ExcelQR履歴 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_Excel現品票履歴 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_ID番号 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_QR履歴 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_QR履歴(backup_260521) — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_QR履歴Tmp — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_エラーログ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_ロット完了理由 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_作業履歴 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_修正ログ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_分割ロット — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_工程マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_数量差異 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_現品票不具合内容 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_現品票履歴 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
