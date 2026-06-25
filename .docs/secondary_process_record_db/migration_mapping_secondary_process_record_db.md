# Access → PostgreSQL 移行対応表

## 1. 移行概要

- 対象Access DB：\\192.168.1.200\共有\生産管理課\AccessDB\社内二次工程記録DB.accdb
- 移行先PostgreSQL DB：secondary_process_record_db
- 接続情報：
  - `.env` の DATABASE_URL を参照
- 移行日：2026-06-25 08:52:47
- 作成者：Codex
- 備考：社内二次工程記録DBの15テーブルを統合・削除せず個別に移行。元Access名は本対応表とPostgreSQLコメントで追跡可能。

## 2. 移行対象テーブル一覧

| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | t_カゴマスタ | basket_master | TABLE | 4 | 4 | 成功 |
| 2 | t_バフ記録 | buffing_records | TABLE | 530 | 530 | 成功 |
| 3 | t_ブラスト記録 | blasting_records | TABLE | 4670 | 4670 | 成功 |
| 4 | t_作業マスタ | work_master | TABLE | 15 | 15 | 成功 |
| 5 | t_作業者マスタ | worker_master | TABLE | 24 | 24 | 成功 |
| 6 | t_使用ピンマスタ | pin_master | TABLE | 3 | 3 | 成功 |
| 7 | t_回転方向マスタ | rotation_direction_master | TABLE | 10 | 10 | 成功 |
| 8 | t_圧力マスタ | pressure_master | TABLE | 2 | 2 | 成功 |
| 9 | t_機番マスタ | machine_master | TABLE | 94 | 94 | 成功 |
| 10 | t_次工程マスタ | next_process_master | TABLE | 4 | 4 | 成功 |
| 11 | t_洗浄工程日報 | washing_process_daily_reports | TABLE | 5297 | 5297 | 成功 |
| 12 | t_研磨石マスタ | polishing_stone_master | TABLE | 17 | 17 | 成功 |
| 13 | t_磁気バレル記録 | magnetic_barrel_records | TABLE | 16177 | 16177 | 成功 |
| 14 | t_製品マスタ | product_master | TABLE | 4543 | 4543 | 成功 |
| 15 | t_遠心バレル記録 | centrifugal_barrel_records | TABLE | 4473 | 4473 | 成功 |

## 3. テーブル別カラム対応表

### Accessテーブル名：t_カゴマスタ
### PostgreSQLテーブル名：basket_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | コード | VARCHAR | code | VARCHAR(2) | 可 |  |
| 2 | カゴ | VARCHAR | basket | VARCHAR(4) | 可 |  |

### Accessテーブル名：t_バフ記録
### PostgreSQLテーブル名：buffing_records

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 作業日 | DATETIME | work_date | TIMESTAMP | 可 |  |
| 3 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 4 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 5 | 客先 | VARCHAR | customer | VARCHAR(30) | 可 |  |
| 6 | 材質 | VARCHAR | material | VARCHAR(35) | 可 |  |
| 7 | 製造日 | DATETIME | manufacturing_date | TIMESTAMP | 可 |  |
| 8 | 製造日2 | VARCHAR | manufacturing_date_text | VARCHAR(30) | 可 | Access上で文字列型のため日付変換せず保持 |
| 9 | 号機 | VARCHAR | machine_no | VARCHAR(5) | 可 |  |
| 10 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 11 | 作業者 | VARCHAR | worker | VARCHAR(6) | 可 |  |
| 12 | 作業者2 | VARCHAR | worker_2 | VARCHAR(6) | 可 |  |
| 13 | 時間 | INTEGER | time_minutes | INTEGER | 可 |  |
| 14 | 作業終了日 | DATETIME | work_completed_date | TIMESTAMP | 可 |  |
| 15 | 備考 | VARCHAR | remarks | VARCHAR(20) | 可 |  |

### Accessテーブル名：t_ブラスト記録
### PostgreSQLテーブル名：blasting_records

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 作業日 | DATETIME | work_date | TIMESTAMP | 可 |  |
| 3 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 4 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 5 | 客先 | VARCHAR | customer | VARCHAR(30) | 可 |  |
| 6 | 材質 | VARCHAR | material | VARCHAR(35) | 可 |  |
| 7 | 製造日 | DATETIME | manufacturing_date | TIMESTAMP | 可 |  |
| 8 | 製造日2 | VARCHAR | manufacturing_date_text | VARCHAR(30) | 可 | Access上で文字列型のため日付変換せず保持 |
| 9 | 号機 | VARCHAR | machine_no | VARCHAR(5) | 可 |  |
| 10 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 11 | 作業者 | VARCHAR | worker | VARCHAR(6) | 可 |  |
| 12 | 処理時間 | INTEGER | processing_time | INTEGER | 可 |  |
| 13 | 圧力 | VARCHAR | pressure | VARCHAR(8) | 可 |  |
| 14 | 次工程 | VARCHAR | next_process | VARCHAR(8) | 可 |  |
| 15 | カゴ | VARCHAR | basket | VARCHAR(4) | 可 |  |
| 16 | 備考 | VARCHAR | remarks | VARCHAR(20) | 可 |  |

### Accessテーブル名：t_作業マスタ
### PostgreSQLテーブル名：work_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 作業コード | VARCHAR | work_code | VARCHAR(2) | 可 |  |
| 2 | 作業名 | VARCHAR | work_name | VARCHAR(15) | 可 |  |

### Accessテーブル名：t_作業者マスタ
### PostgreSQLテーブル名：worker_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | コード | VARCHAR | code | VARCHAR(2) | 可 |  |
| 2 | 作業者名 | VARCHAR | worker_name | VARCHAR(6) | 可 |  |
| 3 | 退職 | VARCHAR | retired | VARCHAR(1) | 可 |  |

### Accessテーブル名：t_使用ピンマスタ
### PostgreSQLテーブル名：pin_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | コード | VARCHAR | code | VARCHAR(2) | 可 |  |
| 2 | ピン | VARCHAR | pin | VARCHAR(5) | 可 |  |

### Accessテーブル名：t_回転方向マスタ
### PostgreSQLテーブル名：rotation_direction_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | コード | VARCHAR | code | VARCHAR(2) | 可 |  |
| 2 | 回転方向 | VARCHAR | rotation_direction | VARCHAR(8) | 可 |  |

### Accessテーブル名：t_圧力マスタ
### PostgreSQLテーブル名：pressure_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | コード | VARCHAR | code | VARCHAR(2) | 可 |  |
| 2 | 圧力 | VARCHAR | pressure | VARCHAR(8) | 可 |  |

### Accessテーブル名：t_機番マスタ
### PostgreSQLテーブル名：machine_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 機械ID | VARCHAR | machine_id | VARCHAR(3) | 可 |  |
| 2 | 機番 | VARCHAR | machine_number | VARCHAR(5) | 可 |  |

### Accessテーブル名：t_次工程マスタ
### PostgreSQLテーブル名：next_process_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | コード | VARCHAR | code | VARCHAR(2) | 可 |  |
| 2 | 次工程 | VARCHAR | next_process | VARCHAR(10) | 可 |  |

### Accessテーブル名：t_洗浄工程日報
### PostgreSQLテーブル名：washing_process_daily_reports

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 日付 | DATETIME | date_value | TIMESTAMP | 可 |  |
| 3 | 曜日 | VARCHAR | day_of_week | VARCHAR(1) | 可 |  |
| 4 | 作業者コード | VARCHAR | worker_code | VARCHAR(2) | 可 |  |
| 5 | 作業コード1 | VARCHAR | work_code_1 | VARCHAR(2) | 可 |  |
| 6 | 作業コード2 | VARCHAR | work_code_2 | VARCHAR(2) | 可 |  |
| 7 | 作業コード3 | VARCHAR | work_code_3 | VARCHAR(2) | 可 |  |
| 8 | 作業コード4 | VARCHAR | work_code_4 | VARCHAR(2) | 可 |  |
| 9 | 作業コード5 | VARCHAR | work_code_5 | VARCHAR(2) | 可 |  |
| 10 | 作業コード6 | VARCHAR | work_code_6 | VARCHAR(2) | 可 |  |
| 11 | 作業コード7 | VARCHAR | work_code_7 | VARCHAR(2) | 可 |  |
| 12 | 作業コード8 | VARCHAR | work_code_8 | VARCHAR(2) | 可 |  |
| 13 | 作業コード9 | VARCHAR | work_code_9 | VARCHAR(2) | 可 |  |
| 14 | 作業コード10 | VARCHAR | work_code_10 | VARCHAR(2) | 可 |  |
| 15 | 作業コード11 | VARCHAR | work_code_11 | VARCHAR(2) | 可 |  |
| 16 | 作業コード12 | VARCHAR | work_code_12 | VARCHAR(2) | 可 |  |
| 17 | 作業コード13 | VARCHAR | work_code_13 | VARCHAR(2) | 可 |  |
| 18 | 作業コード14 | VARCHAR | work_code_14 | VARCHAR(2) | 可 |  |
| 19 | 作業コード15 | VARCHAR | work_code_15 | VARCHAR(2) | 可 |  |
| 20 | 作業コード16 | VARCHAR | work_code_16 | VARCHAR(2) | 可 |  |
| 21 | 作業コード17 | VARCHAR | work_code_17 | VARCHAR(2) | 可 |  |
| 22 | 作業コード18 | VARCHAR | work_code_18 | VARCHAR(2) | 可 |  |

### Accessテーブル名：t_研磨石マスタ
### PostgreSQLテーブル名：polishing_stone_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | コード | VARCHAR | code | VARCHAR(2) | 可 |  |
| 2 | 研磨石 | VARCHAR | polishing_stone | VARCHAR(10) | 可 |  |

### Accessテーブル名：t_磁気バレル記録
### PostgreSQLテーブル名：magnetic_barrel_records

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 作業日 | DATETIME | work_date | TIMESTAMP | 可 |  |
| 3 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 4 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 5 | 客先 | VARCHAR | customer | VARCHAR(30) | 可 |  |
| 6 | 材質 | VARCHAR | material | VARCHAR(35) | 可 |  |
| 7 | 製造日 | DATETIME | manufacturing_date | TIMESTAMP | 可 |  |
| 8 | 製造日2 | VARCHAR | manufacturing_date_text | VARCHAR(30) | 可 | Access上で文字列型のため日付変換せず保持 |
| 9 | 号機 | VARCHAR | machine_no | VARCHAR(5) | 可 |  |
| 10 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 11 | 作業者 | VARCHAR | worker | VARCHAR(6) | 可 |  |
| 12 | 使用ピン | VARCHAR | used_pin | VARCHAR(5) | 可 |  |
| 13 | 回転方向 | VARCHAR | rotation_direction | VARCHAR(8) | 可 |  |
| 14 | 回転数 | INTEGER | rotation_count | INTEGER | 可 |  |
| 15 | 時間 | INTEGER | time_minutes | INTEGER | 可 |  |
| 16 | 作業LOT | INTEGER | work_lot | INTEGER | 可 |  |
| 17 | 備考 | VARCHAR | remarks | VARCHAR(20) | 可 |  |

### Accessテーブル名：t_製品マスタ
### PostgreSQLテーブル名：product_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 2 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 3 | 客先 | VARCHAR | customer | VARCHAR(30) | 可 |  |
| 4 | 材質材料径 | VARCHAR | material_diameter | VARCHAR(30) | 可 |  |
| 5 | ID | VARCHAR | id | VARCHAR(6) | 可 |  |

### Accessテーブル名：t_遠心バレル記録
### PostgreSQLテーブル名：centrifugal_barrel_records

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 作業日 | DATETIME | work_date | TIMESTAMP | 可 |  |
| 3 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 4 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 5 | 客先 | VARCHAR | customer | VARCHAR(30) | 可 |  |
| 6 | 材質 | VARCHAR | material | VARCHAR(35) | 可 |  |
| 7 | 製造日 | DATETIME | manufacturing_date | TIMESTAMP | 可 |  |
| 8 | 製造日2 | VARCHAR | manufacturing_date_text | VARCHAR(30) | 可 | Access上で文字列型のため日付変換せず保持 |
| 9 | 号機 | VARCHAR | machine_no | VARCHAR(5) | 可 |  |
| 10 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 11 | 作業者 | VARCHAR | worker | VARCHAR(6) | 可 |  |
| 12 | 研磨石1 | VARCHAR | polishing_stone_1 | VARCHAR(10) | 可 |  |
| 13 | 時間1 | INTEGER | time_1 | INTEGER | 可 |  |
| 14 | 研磨石2 | VARCHAR | polishing_stone_2 | VARCHAR(10) | 可 |  |
| 15 | 時間2 | INTEGER | time_2 | INTEGER | 可 |  |
| 16 | 備考 | VARCHAR | remarks | VARCHAR(20) | 可 |  |

## 4. 主キー・インデックス情報

| Accessテーブル名 | PostgreSQLテーブル名 | 主キー | インデックス | 備考 |
|---|---|---|---|---|
| t_カゴマスタ | basket_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_バフ記録 | buffing_records | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_ブラスト記録 | blasting_records | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_作業マスタ | work_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_作業者マスタ | worker_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_使用ピンマスタ | pin_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_回転方向マスタ | rotation_direction_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_圧力マスタ | pressure_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_機番マスタ | machine_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_次工程マスタ | next_process_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_洗浄工程日報 | washing_process_daily_reports | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_研磨石マスタ | polishing_stone_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_磁気バレル記録 | magnetic_barrel_records | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_製品マスタ | product_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_遠心バレル記録 | centrifugal_barrel_records | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |

## 5. 型変換ルール

| Access型 | PostgreSQL型 | 備考 |
|---|---|---|
| VARCHAR | varchar(n) | Accessのサイズを維持 |
| COUNTER | bigserial | AccessのID値を投入後、setvalで次採番をMAX(id)+1に同期。PRIMARY KEY付与 |
| INTEGER | integer | 整数 |
| DOUBLE | double precision | 浮動小数 |
| DATETIME | timestamp | Accessの日付/時刻を保持 |
| BIT | boolean | Yes/No型 |
| CURRENCY / NUMERIC | numeric | 金額・数値 |

## 6. アプリ接続時の参照情報

### 接続先

```text
.env の DATABASE_URL を使用
```

### 主に参照するテーブル

| 用途 | PostgreSQLテーブル名 | 主なキー | 備考 |
| -- | --------------- | ---- | -- |
| マスタ | basket_master | code | 元Access: t_カゴマスタ |
| 工程作業記録 | buffing_records | id, product_code, work_date | 元Access: t_バフ記録 |
| 工程作業記録 | blasting_records | id, product_code, work_date | 元Access: t_ブラスト記録 |
| マスタ | work_master | 要確認 | 元Access: t_作業マスタ |
| マスタ | worker_master | code | 元Access: t_作業者マスタ |
| マスタ | pin_master | code | 元Access: t_使用ピンマスタ |
| マスタ | rotation_direction_master | code | 元Access: t_回転方向マスタ |
| マスタ | pressure_master | code | 元Access: t_圧力マスタ |
| マスタ | machine_master | machine_id | 元Access: t_機番マスタ |
| マスタ | next_process_master | code | 元Access: t_次工程マスタ |
| 工程日報 | washing_process_daily_reports | id, worker_code, date_value | 元Access: t_洗浄工程日報 |
| マスタ | polishing_stone_master | code | 元Access: t_研磨石マスタ |
| 工程作業記録 | magnetic_barrel_records | id, product_code, work_date | 元Access: t_磁気バレル記録 |
| 製品マスタ | product_master | id, product_code | 元Access: t_製品マスタ |
| 工程作業記録 | centrifugal_barrel_records | id, product_code, work_date | 元Access: t_遠心バレル記録 |

### 主要カラム

| 用途 | PostgreSQLテーブル名 | PostgreSQLカラム名 | 元Accessカラム名 | 備考 |
| -- | --------------- | -------------- | ----------- | -- |
| コード | basket_master | code | コード | Accessの値をそのまま保持 |
| ID | buffing_records | id | ID | Accessの値をそのまま保持 |
| 作業日 | buffing_records | work_date | 作業日 | Accessの値をそのまま保持 |
| 品番 | buffing_records | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | buffing_records | product_name | 品名 | Accessの値をそのまま保持 |
| 客先 | buffing_records | customer | 客先 | Accessの値をそのまま保持 |
| 材質 | buffing_records | material | 材質 | Accessの値をそのまま保持 |
| 製造日 | buffing_records | manufacturing_date | 製造日 | Accessの値をそのまま保持 |
| 号機 | buffing_records | machine_no | 号機 | Accessの値をそのまま保持 |
| 数量 | buffing_records | quantity | 数量 | Accessの値をそのまま保持 |
| 作業者 | buffing_records | worker | 作業者 | Accessの値をそのまま保持 |
| ID | blasting_records | id | ID | Accessの値をそのまま保持 |
| 作業日 | blasting_records | work_date | 作業日 | Accessの値をそのまま保持 |
| 品番 | blasting_records | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | blasting_records | product_name | 品名 | Accessの値をそのまま保持 |
| 客先 | blasting_records | customer | 客先 | Accessの値をそのまま保持 |
| 材質 | blasting_records | material | 材質 | Accessの値をそのまま保持 |
| 製造日 | blasting_records | manufacturing_date | 製造日 | Accessの値をそのまま保持 |
| 号機 | blasting_records | machine_no | 号機 | Accessの値をそのまま保持 |
| 数量 | blasting_records | quantity | 数量 | Accessの値をそのまま保持 |
| 作業者 | blasting_records | worker | 作業者 | Accessの値をそのまま保持 |
| 処理時間 | blasting_records | processing_time | 処理時間 | Accessの値をそのまま保持 |
| 次工程 | blasting_records | next_process | 次工程 | Accessの値をそのまま保持 |
| 作業コード | work_master | work_code | 作業コード | Accessの値をそのまま保持 |
| コード | worker_master | code | コード | Accessの値をそのまま保持 |
| コード | pin_master | code | コード | Accessの値をそのまま保持 |
| コード | rotation_direction_master | code | コード | Accessの値をそのまま保持 |
| コード | pressure_master | code | コード | Accessの値をそのまま保持 |
| コード | next_process_master | code | コード | Accessの値をそのまま保持 |
| 次工程 | next_process_master | next_process | 次工程 | Accessの値をそのまま保持 |
| ID | washing_process_daily_reports | id | ID | Accessの値をそのまま保持 |
| 日付 | washing_process_daily_reports | date_value | 日付 | Accessの値をそのまま保持 |
| 作業者コード | washing_process_daily_reports | worker_code | 作業者コード | Accessの値をそのまま保持 |
| コード | polishing_stone_master | code | コード | Accessの値をそのまま保持 |
| ID | magnetic_barrel_records | id | ID | Accessの値をそのまま保持 |
| 作業日 | magnetic_barrel_records | work_date | 作業日 | Accessの値をそのまま保持 |
| 品番 | magnetic_barrel_records | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | magnetic_barrel_records | product_name | 品名 | Accessの値をそのまま保持 |
| 客先 | magnetic_barrel_records | customer | 客先 | Accessの値をそのまま保持 |
| 材質 | magnetic_barrel_records | material | 材質 | Accessの値をそのまま保持 |
| 製造日 | magnetic_barrel_records | manufacturing_date | 製造日 | Accessの値をそのまま保持 |
| 号機 | magnetic_barrel_records | machine_no | 号機 | Accessの値をそのまま保持 |
| 数量 | magnetic_barrel_records | quantity | 数量 | Accessの値をそのまま保持 |
| 作業者 | magnetic_barrel_records | worker | 作業者 | Accessの値をそのまま保持 |
| 品番 | product_master | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | product_master | product_name | 品名 | Accessの値をそのまま保持 |
| 客先 | product_master | customer | 客先 | Accessの値をそのまま保持 |
| ID | product_master | id | ID | Accessの値をそのまま保持 |
| ID | centrifugal_barrel_records | id | ID | Accessの値をそのまま保持 |
| 作業日 | centrifugal_barrel_records | work_date | 作業日 | Accessの値をそのまま保持 |
| 品番 | centrifugal_barrel_records | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | centrifugal_barrel_records | product_name | 品名 | Accessの値をそのまま保持 |
| 客先 | centrifugal_barrel_records | customer | 客先 | Accessの値をそのまま保持 |
| 材質 | centrifugal_barrel_records | material | 材質 | Accessの値をそのまま保持 |
| 製造日 | centrifugal_barrel_records | manufacturing_date | 製造日 | Accessの値をそのまま保持 |
| 号機 | centrifugal_barrel_records | machine_no | 号機 | Accessの値をそのまま保持 |
| 数量 | centrifugal_barrel_records | quantity | 数量 | Accessの値をそのまま保持 |
| 作業者 | centrifugal_barrel_records | worker | 作業者 | Accessの値をそのまま保持 |

## 7. 注意事項・要確認事項

- AccessのFKメタデータはODBCドライバが返さなかったため、外部キー制約は作成していません。要確認。
- COUNTER列はBIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期しています。
- `.env` の `ACCESS_DB_PATH` が実ファイルを指していない場合は、メタJSONの `database_path` を使用します。
- メタ抽出警告：FK 取得スキップ: t_カゴマスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_バフ記録 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_ブラスト記録 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_作業マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_作業者マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_使用ピンマスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_回転方向マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_圧力マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_機番マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_次工程マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_洗浄工程日報 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_研磨石マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_磁気バレル記録 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_製品マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_遠心バレル記録 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：VBA 抽出失敗: (-2147352567, '例外が発生しました。', (0, None, '指定した式に、Visible プロパティに対する正しくない参照が含まれます。', 'dao360.chm', 2015567, -2146825833), None)
