# Access → PostgreSQL 移行対応表

## 1. 移行概要

- 対象Access DB：\\192.168.1.200\共有\生産管理課\AccessDB\外観検査記録DB.accdb
- 移行先PostgreSQL DB：appearance_inspection_db
- 接続情報：
  - `.env` の DATABASE_URL を参照
- 移行日：2026-06-25 08:52:02
- 作成者：Codex
- 備考：外観検査記録DBの13テーブルを忠実に移行。日本語名はPostgreSQL用に英語/ローマ字のスネークケースへ変換し、元名はコメントと本対応表で追跡可能。

## 2. 移行対象テーブル一覧

| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | t_Excel現品票履歴 | excel_product_slip_history | TABLE | 33987 | 33987 | 成功 |
| 2 | t_チェックシートリスト | check_sheet_list | TABLE | 119 | 119 | 成功 |
| 3 | t_不具合情報 | defect_information | TABLE | 156396 | 156396 | 成功 |
| 4 | t_外観検査記録 | appearance_inspection_records | TABLE | 70654 | 70654 | 成功 |
| 5 | t_外観検査記録保存 | appearance_inspection_record_archives | TABLE | 225171 | 225171 | 成功 |
| 6 | t_外観検査集計 | appearance_inspection_summaries | TABLE | 52885 | 52885 | 成功 |
| 7 | t_外観検査集計保存 | appearance_inspection_summary_archives | TABLE | 171580 | 171580 | 成功 |
| 8 | t_工程マスタ | process_master | TABLE | 10 | 10 | 成功 |
| 9 | t_数値検査員マスタ | numeric_inspector_master | TABLE | 14 | 14 | 成功 |
| 10 | t_数値検査記録 | numeric_inspection_records | TABLE | 26660 | 26660 | 成功 |
| 11 | t_検査中 | inspection_in_progress | TABLE | 60 | 60 | 成功 |
| 12 | t_検査員マスタ | inspector_master | TABLE | 77 | 77 | 成功 |
| 13 | t_検査者マスタ | inspection_person_master | TABLE | 72 | 72 | 成功 |

## 3. テーブル別カラム対応表

### Accessテーブル名：t_Excel現品票履歴
### PostgreSQLテーブル名：excel_product_slip_history

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

### Accessテーブル名：t_チェックシートリスト
### PostgreSQLテーブル名：check_sheet_list

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | No | INTEGER | no | INTEGER | 可 |  |
| 2 | 客先 | VARCHAR | customer | VARCHAR(25) | 可 |  |
| 3 | ファイルNo | VARCHAR | file_no | VARCHAR(10) | 可 |  |

### Accessテーブル名：t_不具合情報
### PostgreSQLテーブル名：defect_information

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 3 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 4 | 指示日 | DATETIME | instruction_date | TIMESTAMP | 可 |  |
| 5 | 号機 | VARCHAR | machine_no | VARCHAR(5) | 可 |  |
| 6 | 検査者1 | VARCHAR | inspector_1 | VARCHAR(6) | 可 |  |
| 7 | 検査者2 | VARCHAR | inspector_2 | VARCHAR(6) | 可 |  |
| 8 | 検査者3 | VARCHAR | inspector_3 | VARCHAR(6) | 可 |  |
| 9 | 検査者4 | VARCHAR | inspector_4 | VARCHAR(6) | 可 |  |
| 10 | 検査者5 | VARCHAR | inspector_5 | VARCHAR(20) | 可 |  |
| 11 | 時間 | INTEGER | time_value | INTEGER | 可 |  |
| 12 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 13 | 総不具合数 | INTEGER | total_defect_count | INTEGER | 可 |  |
| 14 | 不良率 | DOUBLE | defect_rate | DOUBLE PRECISION | 可 |  |
| 15 | 外観キズ | INTEGER | appearance_scratch | INTEGER | 可 |  |
| 16 | 圧痕 | INTEGER | dent | INTEGER | 可 |  |
| 17 | 切粉 | INTEGER | cutting_chip | INTEGER | 可 |  |
| 18 | 毟れ | INTEGER | mushire | INTEGER | 可 |  |
| 19 | 穴大 | INTEGER | oversized_hole | INTEGER | 可 |  |
| 20 | 穴小 | INTEGER | undersized_hole | INTEGER | 可 |  |
| 21 | 穴キズ | INTEGER | hole_scratch | INTEGER | 可 |  |
| 22 | バリ | INTEGER | burr | INTEGER | 可 |  |
| 23 | 短寸 | INTEGER | short_length | INTEGER | 可 |  |
| 24 | 面粗 | INTEGER | rough_surface | INTEGER | 可 |  |
| 25 | サビ | INTEGER | rust | INTEGER | 可 |  |
| 26 | ボケ | INTEGER | blur | INTEGER | 可 |  |
| 27 | 挽目 | INTEGER | turning_mark | INTEGER | 可 |  |
| 28 | 汚れ | INTEGER | stain | INTEGER | 可 |  |
| 29 | メッキ | INTEGER | plating | INTEGER | 可 |  |
| 30 | 落下 | INTEGER | dropped | INTEGER | 可 |  |
| 31 | フクレ | INTEGER | swelling | INTEGER | 可 |  |
| 32 | ツブレ | INTEGER | crush | INTEGER | 可 |  |
| 33 | ボッチ | INTEGER | bump | INTEGER | 可 |  |
| 34 | 段差 | INTEGER | step | INTEGER | 可 |  |
| 35 | バレル石 | INTEGER | barrel_stone | INTEGER | 可 |  |
| 36 | 径プラス | INTEGER | diameter_plus | INTEGER | 可 |  |
| 37 | 径マイナス | INTEGER | diameter_minus | INTEGER | 可 |  |
| 38 | ゲージ | INTEGER | gauge | INTEGER | 可 |  |
| 39 | 異物混入 | INTEGER | foreign_matter | INTEGER | 可 |  |
| 40 | 形状不良 | INTEGER | shape_defect | INTEGER | 可 |  |
| 41 | こすれ | INTEGER | abrasion | INTEGER | 可 |  |
| 42 | 変色シミ | INTEGER | discoloration_stain | INTEGER | 可 |  |
| 43 | 材料キズ | INTEGER | material_scratch | INTEGER | 可 |  |
| 44 | ゴミ | INTEGER | dust | INTEGER | 可 |  |
| 45 | その他 | INTEGER | other | INTEGER | 可 |  |
| 46 | その他内容 | VARCHAR | other_detail | VARCHAR(10) | 可 |  |

### Accessテーブル名：t_外観検査記録
### PostgreSQLテーブル名：appearance_inspection_records

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 検査員ID | VARCHAR | inspector_id | VARCHAR(4) | 可 |  |
| 3 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 4 | 工程NO | VARCHAR | process_no | VARCHAR(2) | 可 |  |
| 5 | 日付 | DATETIME | inspection_date | TIMESTAMP | 可 |  |
| 6 | 時刻 | DATETIME | time_at | TIMESTAMP | 可 |  |
| 7 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 8 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 9 | 客先 | VARCHAR | customer | VARCHAR(25) | 可 |  |
| 10 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 11 | 更新フラグ | VARCHAR | update_flag | VARCHAR(1) | 可 |  |
| 12 | 集計除外フラグ | BIT | aggregation_exclusion_flag | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |

### Accessテーブル名：t_外観検査記録保存
### PostgreSQLテーブル名：appearance_inspection_record_archives

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 検査員ID | VARCHAR | inspector_id | VARCHAR(4) | 可 |  |
| 3 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 4 | 工程NO | VARCHAR | process_no | VARCHAR(2) | 可 |  |
| 5 | 日付 | DATETIME | inspection_date | TIMESTAMP | 可 |  |
| 6 | 時刻 | DATETIME | time_at | TIMESTAMP | 可 |  |
| 7 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 8 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 9 | 客先 | VARCHAR | customer | VARCHAR(25) | 可 |  |
| 10 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 11 | 更新フラグ | VARCHAR | update_flag | VARCHAR(1) | 可 |  |
| 12 | 集計除外フラグ | BIT | aggregation_exclusion_flag | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |

### Accessテーブル名：t_外観検査集計
### PostgreSQLテーブル名：appearance_inspection_summaries

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 検査員ID | VARCHAR | inspector_id | VARCHAR(4) | 可 |  |
| 3 | 日付 | DATETIME | inspection_date | TIMESTAMP | 可 |  |
| 4 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 5 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 6 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 7 | 工程NO | VARCHAR | process_no | VARCHAR(2) | 可 |  |
| 8 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 9 | 作業時間 | INTEGER | work_time | INTEGER | 可 |  |
| 10 | 集計除外フラグ | BIT | aggregation_exclusion_flag | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |

### Accessテーブル名：t_外観検査集計保存
### PostgreSQLテーブル名：appearance_inspection_summary_archives

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 検査員ID | VARCHAR | inspector_id | VARCHAR(4) | 可 |  |
| 3 | 日付 | DATETIME | inspection_date | TIMESTAMP | 可 |  |
| 4 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 5 | 品番 | VARCHAR | product_code | VARCHAR(30) | 可 |  |
| 6 | 品名 | VARCHAR | product_name | VARCHAR(30) | 可 |  |
| 7 | 工程NO | VARCHAR | process_no | VARCHAR(2) | 可 |  |
| 8 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 9 | 作業時間 | INTEGER | work_time | INTEGER | 可 |  |
| 10 | 集計除外フラグ | BIT | aggregation_exclusion_flag | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |

### Accessテーブル名：t_工程マスタ
### PostgreSQLテーブル名：process_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 工程NO | INTEGER | process_no | INTEGER | 可 |  |
| 2 | 工程名 | VARCHAR | process_name | VARCHAR(10) | 可 |  |

### Accessテーブル名：t_数値検査員マスタ
### PostgreSQLテーブル名：numeric_inspector_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 検査員ID | VARCHAR | inspector_id | VARCHAR(4) | 可 |  |
| 2 | 検査員名 | VARCHAR | inspector_name | VARCHAR(5) | 可 |  |
| 3 | 区別 | VARCHAR | category | VARCHAR(5) | 可 |  |
| 4 | 表示フラグ | BIT | display_flag | BOOLEAN | 不可 | AccessのYes/Noをbooleanへ変換 |

### Accessテーブル名：t_数値検査記録
### PostgreSQLテーブル名：numeric_inspection_records

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 日付時刻 | DATETIME | inspected_at | TIMESTAMP | 可 |  |
| 3 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 4 | 検査員ID | VARCHAR | inspector_id | VARCHAR(4) | 可 |  |
| 5 | 工程名 | VARCHAR | process_name | VARCHAR(30) | 可 |  |
| 6 | 号機 | VARCHAR | machine_no | VARCHAR(5) | 可 |  |

### Accessテーブル名：t_検査中
### PostgreSQLテーブル名：inspection_in_progress

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 検査員ID | VARCHAR | inspector_id | VARCHAR(4) | 可 |  |
| 2 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 3 | 時刻 | DATETIME | time_at | TIMESTAMP | 可 |  |
| 4 | 表示フラグ | VARCHAR | display_flag | VARCHAR(1) | 可 |  |

### Accessテーブル名：t_検査員マスタ
### PostgreSQLテーブル名：inspector_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 検査員ID | VARCHAR | inspector_id | VARCHAR(4) | 可 |  |
| 2 | 検査員名 | VARCHAR | inspector_name | VARCHAR(10) | 可 |  |
| 3 | 表示位置 | VARCHAR | display_position | VARCHAR(3) | 可 |  |
| 4 | チーム | VARCHAR | team | VARCHAR(1) | 可 |  |
| 5 | ふりがな | VARCHAR | furigana | VARCHAR(1) | 可 |  |

### Accessテーブル名：t_検査者マスタ
### PostgreSQLテーブル名：inspection_person_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | 検査者 | VARCHAR | inspector_name | VARCHAR(6) | 可 |  |
| 3 | ふりがな | VARCHAR | furigana | VARCHAR(1) | 可 |  |

## 4. 主キー・インデックス情報

| Accessテーブル名 | PostgreSQLテーブル名 | 主キー | インデックス | 備考 |
|---|---|---|---|---|
| t_Excel現品票履歴 | excel_product_slip_history | 検出なし | 検出なし | FKは未検出 |
| t_チェックシートリスト | check_sheet_list | 検出なし | 検出なし | FKは未検出 |
| t_不具合情報 | defect_information | 検出なし | 検出なし | FKは未検出 |
| t_外観検査記録 | appearance_inspection_records | 検出なし | 検出なし | FKは未検出 |
| t_外観検査記録保存 | appearance_inspection_record_archives | 検出なし | 検出なし | FKは未検出 |
| t_外観検査集計 | appearance_inspection_summaries | 検出なし | 検出なし | FKは未検出 |
| t_外観検査集計保存 | appearance_inspection_summary_archives | 検出なし | 検出なし | FKは未検出 |
| t_工程マスタ | process_master | 検出なし | 検出なし | FKは未検出 |
| t_数値検査員マスタ | numeric_inspector_master | 検出なし | 検出なし | FKは未検出 |
| t_数値検査記録 | numeric_inspection_records | 検出なし | 検出なし | FKは未検出 |
| t_検査中 | inspection_in_progress | 検出なし | 検出なし | FKは未検出 |
| t_検査員マスタ | inspector_master | 検出なし | 検出なし | FKは未検出 |
| t_検査者マスタ | inspection_person_master | 検出なし | 検出なし | FKは未検出 |

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
| 現品票履歴 | excel_product_slip_history | production_lot_id, product_code | 元 t_Excel現品票履歴 |
| 参照テーブル | check_sheet_list | no | 元 t_チェックシートリスト |
| 不具合情報 | defect_information | id, production_lot_id, product_code | 元 t_不具合情報 |
| 外観検査記録 | appearance_inspection_records | id, production_lot_id, product_code, inspector_id, process_no | 元 t_外観検査記録 |
| 外観検査記録 | appearance_inspection_record_archives | id, production_lot_id, product_code, inspector_id, process_no | 元 t_外観検査記録保存 |
| 外観検査集計 | appearance_inspection_summaries | id, production_lot_id, product_code, inspector_id, process_no | 元 t_外観検査集計 |
| 外観検査集計 | appearance_inspection_summary_archives | id, production_lot_id, product_code, inspector_id, process_no | 元 t_外観検査集計保存 |
| マスタ | process_master | process_no | 元 t_工程マスタ |
| マスタ | numeric_inspector_master | inspector_id | 元 t_数値検査員マスタ |
| 参照テーブル | numeric_inspection_records | id, production_lot_id, inspector_id | 元 t_数値検査記録 |
| 参照テーブル | inspection_in_progress | production_lot_id, inspector_id | 元 t_検査中 |
| マスタ | inspector_master | inspector_id | 元 t_検査員マスタ |
| マスタ | inspection_person_master | id | 元 t_検査者マスタ |

### 主要カラム

| 用途 | PostgreSQLテーブル名 | PostgreSQLカラム名 | 元Accessカラム名 | 備考 |
| -- | --------------- | -------------- | ----------- | -- |
| 生産ロット | excel_product_slip_history | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 号機 | excel_product_slip_history | machine_no | 号機 | Accessの値をそのまま保持 |
| 品番 | excel_product_slip_history | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | excel_product_slip_history | product_name | 品名 | Accessの値をそのまま保持 |
| 客先 | excel_product_slip_history | customer | 客先 | Accessの値をそのまま保持 |
| 数量 | excel_product_slip_history | quantity | 数量 | Accessの値をそのまま保持 |
| 指示日 | excel_product_slip_history | instruction_date | 指示日 | Accessの値をそのまま保持 |
| 番号 | check_sheet_list | no | No | Accessの値をそのまま保持 |
| 客先 | check_sheet_list | customer | 客先 | Accessの値をそのまま保持 |
| ID | defect_information | id | ID | Accessの値をそのまま保持 |
| 生産ロット | defect_information | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 品番 | defect_information | product_code | 品番 | Accessの値をそのまま保持 |
| 指示日 | defect_information | instruction_date | 指示日 | Accessの値をそのまま保持 |
| 号機 | defect_information | machine_no | 号機 | Accessの値をそのまま保持 |
| 数量 | defect_information | quantity | 数量 | Accessの値をそのまま保持 |
| ID | appearance_inspection_records | id | ID | Accessの値をそのまま保持 |
| 検査員 | appearance_inspection_records | inspector_id | 検査員ID | Accessの値をそのまま保持 |
| 生産ロット | appearance_inspection_records | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 工程 | appearance_inspection_records | process_no | 工程NO | Accessの値をそのまま保持 |
| 検査日 | appearance_inspection_records | inspection_date | 日付 | Accessの値をそのまま保持 |
| 品番 | appearance_inspection_records | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | appearance_inspection_records | product_name | 品名 | Accessの値をそのまま保持 |
| 客先 | appearance_inspection_records | customer | 客先 | Accessの値をそのまま保持 |
| 数量 | appearance_inspection_records | quantity | 数量 | Accessの値をそのまま保持 |
| ID | appearance_inspection_record_archives | id | ID | Accessの値をそのまま保持 |
| 検査員 | appearance_inspection_record_archives | inspector_id | 検査員ID | Accessの値をそのまま保持 |
| 生産ロット | appearance_inspection_record_archives | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 工程 | appearance_inspection_record_archives | process_no | 工程NO | Accessの値をそのまま保持 |
| 検査日 | appearance_inspection_record_archives | inspection_date | 日付 | Accessの値をそのまま保持 |
| 品番 | appearance_inspection_record_archives | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | appearance_inspection_record_archives | product_name | 品名 | Accessの値をそのまま保持 |
| 客先 | appearance_inspection_record_archives | customer | 客先 | Accessの値をそのまま保持 |
| 数量 | appearance_inspection_record_archives | quantity | 数量 | Accessの値をそのまま保持 |
| ID | appearance_inspection_summaries | id | ID | Accessの値をそのまま保持 |
| 検査員 | appearance_inspection_summaries | inspector_id | 検査員ID | Accessの値をそのまま保持 |
| 検査日 | appearance_inspection_summaries | inspection_date | 日付 | Accessの値をそのまま保持 |
| 生産ロット | appearance_inspection_summaries | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 品番 | appearance_inspection_summaries | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | appearance_inspection_summaries | product_name | 品名 | Accessの値をそのまま保持 |
| 工程 | appearance_inspection_summaries | process_no | 工程NO | Accessの値をそのまま保持 |
| 数量 | appearance_inspection_summaries | quantity | 数量 | Accessの値をそのまま保持 |
| ID | appearance_inspection_summary_archives | id | ID | Accessの値をそのまま保持 |
| 検査員 | appearance_inspection_summary_archives | inspector_id | 検査員ID | Accessの値をそのまま保持 |
| 検査日 | appearance_inspection_summary_archives | inspection_date | 日付 | Accessの値をそのまま保持 |
| 生産ロット | appearance_inspection_summary_archives | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 品番 | appearance_inspection_summary_archives | product_code | 品番 | Accessの値をそのまま保持 |
| 品名 | appearance_inspection_summary_archives | product_name | 品名 | Accessの値をそのまま保持 |
| 工程 | appearance_inspection_summary_archives | process_no | 工程NO | Accessの値をそのまま保持 |
| 数量 | appearance_inspection_summary_archives | quantity | 数量 | Accessの値をそのまま保持 |
| 工程 | process_master | process_no | 工程NO | Accessの値をそのまま保持 |
| 工程名 | process_master | process_name | 工程名 | Accessの値をそのまま保持 |
| 検査員 | numeric_inspector_master | inspector_id | 検査員ID | Accessの値をそのまま保持 |
| ID | numeric_inspection_records | id | ID | Accessの値をそのまま保持 |
| 検査日時 | numeric_inspection_records | inspected_at | 日付時刻 | Accessの値をそのまま保持 |
| 生産ロット | numeric_inspection_records | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 検査員 | numeric_inspection_records | inspector_id | 検査員ID | Accessの値をそのまま保持 |
| 工程名 | numeric_inspection_records | process_name | 工程名 | Accessの値をそのまま保持 |
| 号機 | numeric_inspection_records | machine_no | 号機 | Accessの値をそのまま保持 |
| 検査員 | inspection_in_progress | inspector_id | 検査員ID | Accessの値をそのまま保持 |
| 生産ロット | inspection_in_progress | production_lot_id | 生産ロットID | Accessの値をそのまま保持 |
| 検査員 | inspector_master | inspector_id | 検査員ID | Accessの値をそのまま保持 |
| ID | inspection_person_master | id | ID | Accessの値をそのまま保持 |

## 7. 注意事項・要確認事項

- AccessのFKメタデータはODBCドライバが返さなかったため、外部キー制約は作成していません。
- COUNTER列はBIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期しています。
- `時刻` はAccess上で `1899-12-30 HH:MM:SS` のtimestampとして保持されている場合、そのままtimestampで移行します。
- `.env` の `ACCESS_DB_PATH` が実ファイルを指していない場合は、メタJSONの `database_path` を使用しています。
- メタ抽出警告：FK 取得スキップ: t_Excel現品票履歴 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_チェックシートリスト — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_不具合情報 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_外観検査記録 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_外観検査記録保存 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_外観検査集計 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_外観検査集計保存 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_工程マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_数値検査員マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_数値検査記録 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_検査中 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_検査員マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_検査者マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
