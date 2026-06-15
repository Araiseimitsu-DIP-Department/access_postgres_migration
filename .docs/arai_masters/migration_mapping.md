# 製品マスター → PostgreSQL 移行対応表

## 1. 移行概要

- 対象データ：製品マスター Excel（`config.env` の `PRODUCT_MASTERS_COPY` で指定）
- 対象シート：`config.env` の `PRODUCT_MASTER_SHEET_NAME` で指定
- 移行先PostgreSQL DB：`config.env` の `POSTGRES_DB`（推奨名: `arai_masters`）
- 移行先スキーマ：`config.env` の `POSTGRES_SCHEMA`（未指定時は `public`）
- 接続情報：
  - `config.env` の `POSTGRES_CONNECTION_URL` を優先
  - 未設定時は `POSTGRES_HOST` / `POSTGRES_PORT` / `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` から接続
- 投入スクリプト：`.docs/arai_masters/create_product_master.py`
- DDL：`.docs/arai_masters/arai_masters_ddl.sql`
- 移行日：2026-06-15
- 作成者：Codex
- 備考：
  - 本対象は Access `.accdb` ファイルではなく、**製品マスター Excel** を正とするマスターデータ移行である。
  - Excel の列ヘッダ（日本語名）が従来 Access 連携マスターと同一の業務項目名であり、PostgreSQL では英語スネークケースへ変換した。
  - 社内二次工程記録DB（`secondary_process_record_db`）内の `t_製品マスタ`（5列の簡易版）とは**別テーブル**である。本 `product_master` は全64項目の拡張マスター。
  - 数値列は投入時に小数点以下2桁へ四捨五入して `NUMERIC(15, 2)` へ格納する。
  - 文字列は定義長を超える場合、投入スクリプト側で切り詰める。

## 2. 移行対象テーブル一覧

| No | 元データ（Excel） | PostgreSQLテーブル名 | 種別 | 備考 |
|---:|---|---|---|---|
| 1 | 製品マスターシート（`PRODUCT_MASTER_SHEET_NAME`） | product_master | TABLE | Excel 2行目以降を投入。`id` が NULL の行はスキップ |

## 3. テーブル別カラム対応表

### 元データ：製品マスター Excel
### PostgreSQLテーブル名：product_master

| No | 元カラム名（Excelヘッダ） | Excel列 | 元型（Excel相当） | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|:---:|---|---|---|:---:|---|
| 1 | ID | BU | 文字列 | id | VARCHAR(7) | 不可 | 主キー。空の行は投入対象外 |
| 2 | 製品番号 | A | 文字列 | product_no | VARCHAR(30) | 可 | 品番として参照される主要キー候補 |
| 3 | 別管理番号 | B | 文字列 | alt_management_no | VARCHAR(30) | 可 |  |
| 4 | 製品名 | C | 文字列 | product_name | VARCHAR(30) | 可 |  |
| 5 | 客先名 | D | 文字列 | customer_name | VARCHAR(30) | 可 |  |
| 6 | 次工程 | E | 文字列 | next_process | VARCHAR(10) | 可 |  |
| 7 | コード | F | 文字列 | process_code | VARCHAR(4) | 可 |  |
| 8 | 締日 | G | 文字列 | closing_day | VARCHAR(2) | 可 |  |
| 9 | 営業　　　担当 | H | 文字列 | sales_staff | VARCHAR(6) | 可 | ヘッダに全角スペースを含む |
| 10 | 材質＆材料径 | I | 文字列 | material_and_diameter | VARCHAR(80) | 可 |  |
| 11 | 製品全長 | J | 数値 | product_length | NUMERIC(15, 2) | 可 | 投入時に小数点以下2桁で四捨五入 |
| 12 | 突切 | K | 数値 | cutoff | NUMERIC(15, 2) | 可 | 同上 |
| 13 | 全長＋突切り幅 | L | 数値 | total_length_with_cutoff | NUMERIC(15, 2) | 可 | 同上 |
| 14 | 前回　　　加工秒数 | M | 数値 | previous_machining_seconds | NUMERIC(15, 2) | 可 | 同上 |
| 15 | 日産 | N | 数値 | daily_output | NUMERIC(15, 2) | 可 | 同上 |
| 16 | 取り数 | O | 数値 | pickup_qty | NUMERIC(15, 2) | 可 | 同上 |
| 17 | 単価 | P | 数値 | unit_price | NUMERIC(15, 2) | 可 | 同上 |
| 18 | 材料費 | Q | 数値 | material_cost | NUMERIC(15, 2) | 可 | 同上 |
| 19 | 加工費 | R | 数値 | machining_cost | NUMERIC(15, 2) | 可 | 同上 |
| 20 | 処理費 | S | 数値 | processing_cost | NUMERIC(15, 2) | 可 | 同上 |
| 21 | 製品取扱注意事項 | T | 文字列 | handling_precautions | VARCHAR(20) | 可 |  |
| 22 | 指示書　有無 | U | 文字列 | instruction_sheet_flag | VARCHAR(1) | 可 |  |
| 23 | 備考　、条件　等　 | V | 文字列 | remarks_and_conditions | VARCHAR(50) | 可 |  |
| 24 | 前検 | W | 文字列 | pre_inspection | VARCHAR(1) | 可 |  |
| 25 | 二次工程先 | X | 文字列 | secondary_process_dest | VARCHAR(20) | 可 |  |
| 26 | L/T | AI | 整数 | lead_time | INTEGER | 可 |  |
| 27 | 洗浄① | AJ | 文字列 | wash_step_1 | VARCHAR(10) | 可 |  |
| 28 | 工程② | AK | 文字列 | process_2 | VARCHAR(30) | 可 |  |
| 29 | 処理先 | AL | 文字列 | process_2_vendor | VARCHAR(20) | 可 | ヘッダ名は「処理先」。工程②用 |
| 30 | 工程②集計 | AM | 文字列 | process_2_total | VARCHAR(2) | 可 |  |
| 31 | 工程③ | AO | 文字列 | process_3 | VARCHAR(30) | 可 |  |
| 32 | 処理先 | AP | 文字列 | process_3_vendor | VARCHAR(20) | 可 | 工程③用 |
| 33 | 工程③集計 | AQ | 文字列 | process_3_total | VARCHAR(2) | 可 |  |
| 34 | 工程④ | AS | 文字列 | process_4 | VARCHAR(30) | 可 |  |
| 35 | 処理先 | AT | 文字列 | process_4_vendor | VARCHAR(20) | 可 | 工程④用 |
| 36 | 工程④集計 | AU | 文字列 | process_4_total | VARCHAR(2) | 可 |  |
| 37 | 工程⑤ | AW | 文字列 | process_5 | VARCHAR(30) | 可 |  |
| 38 | 処理先 | AX | 文字列 | process_5_vendor | VARCHAR(20) | 可 | 工程⑤用 |
| 39 | 工程⑤集計 | AY | 文字列 | process_5_total | VARCHAR(2) | 可 |  |
| 40 | 工程⑥ | BA | 文字列 | process_6 | VARCHAR(30) | 可 |  |
| 41 | 処理先 | BB | 文字列 | process_6_vendor | VARCHAR(20) | 可 | 工程⑥用 |
| 42 | 工程⑥集計 | BC | 文字列 | process_6_total | VARCHAR(2) | 可 |  |
| 43 | 工程⑦ | BE | 文字列 | process_7 | VARCHAR(30) | 可 |  |
| 44 | 処理先 | BF | 文字列 | process_7_vendor | VARCHAR(20) | 可 | 工程⑦用 |
| 45 | 工程⑦集計 | BG | 文字列 | process_7_total | VARCHAR(2) | 可 |  |
| 46 | 工程⑧ | BI | 文字列 | process_8 | VARCHAR(30) | 可 |  |
| 47 | 処理先 | BJ | 文字列 | process_8_vendor | VARCHAR(20) | 可 | 工程⑧用 |
| 48 | 工程⑧集計 | BK | 文字列 | process_8_total | VARCHAR(2) | 可 |  |
| 49 | 工程⑨ | BM | 文字列 | process_9 | VARCHAR(30) | 可 |  |
| 50 | 処理先 | BN | 文字列 | process_9_vendor | VARCHAR(20) | 可 | 工程⑨用 |
| 51 | 工程⑨集計 | BO | 文字列 | process_9_total | VARCHAR(2) | 可 |  |
| 52 | 梱包形態 | BQ | 文字列 | packing_style | VARCHAR(30) | 可 |  |
| 53 | 梱包仕様 | BR | 文字列 | packing_spec | VARCHAR(30) | 可 |  |
| 54 | 送り先指定 | BS | 文字列 | destination_spec | VARCHAR(30) | 可 |  |
| 55 | 外部委託加工費 | BT | 数値 | external_machining_cost | NUMERIC(15, 2) | 可 | 投入時に小数点以下2桁で四捨五入 |
| 56 | 納期　　　担当 | BV | 文字列 | delivery_staff | VARCHAR(6) | 可 |  |
| 57 | 材料　　　　識別 | BX | 文字列 | material_identification | VARCHAR(2) | 可 |  |
| 58 | 区分 | BY | 文字列 | category | VARCHAR(5) | 可 |  |
| 59 | 用途　情報 | BZ | 文字列 | usage_info | VARCHAR(255) | 可 |  |
| 60 | 備考 | CA | 文字列 | remarks | VARCHAR(255) | 可 |  |
| 61 | IATF   対象 | CB | 文字列 | iatf_target | VARCHAR(1) | 可 |  |
| 62 | 指示書　有無BU | CC | 文字列 | instruction_sheet_flag_bu | VARCHAR(1) | 可 |  |
| 63 | 呼出ｺｰﾄﾞ | CD | 文字列 | call_code | VARCHAR(7) | 可 |  |
| 64 | 製品単重　　(g) | CE | 数値 | unit_weight | NUMERIC(15, 2) | 可 | 投入時に小数点以下2桁で四捨五入 |

### 投入対象外の Excel 列

スクリプトは `A`〜`CE` 列のうち、上表の64列のみを読み込む。`Y`〜`AH`、`AN`、`AR`、`AV`、`AZ`、`BD`、`BH`、`BL`、`BN` 以外の中間列など、未定義列は PostgreSQL へ移行しない。

## 4. 主キー・インデックス情報

| 元データ | PostgreSQLテーブル名 | 主キー | インデックス | 備考 |
|---|---|---|---|---|
| 製品マスター Excel | product_master | id | なし（PKのみ） | 外部キー制約は未定義 |

## 5. 型変換ルール

| 元型（Excel相当） | PostgreSQL型 | 備考 |
|---|---|---|
| 文字列 | VARCHAR(n) | `create_product_master.py` の `varchar_len` を維持 |
| 数値（小数あり） | NUMERIC(15, 2) | 四捨五入（ROUND_HALF_UP）後に格納。NaN・空・不正値は NULL |
| 整数 | INTEGER | 小数入力は `int(float(value))` で変換。不正値は NULL |
| 空セル | NULL | 文字列の空・空白のみも NULL 扱い |

## 6. アプリ接続時の参照情報

### 接続先

```text
# 推奨: config.env（.docs/config.env）を参照

POSTGRES_CONNECTION_URL=postgresql://<user>:<password>@<host>:<port>/<database>
# または個別指定
POSTGRES_HOST=<host>
POSTGRES_PORT=5432
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=arai_masters
POSTGRES_SCHEMA=public
```

Python（psycopg）での接続例:

```python
import psycopg

conn = psycopg.connect("postgresql://user:password@host:5432/arai_masters")
# スキーマが public 以外の場合
# conn.execute("SET search_path TO your_schema")
```

### 主に参照するテーブル

| 用途 | PostgreSQLテーブル名 | 主なキー | 備考 |
| -- | --------------- | ---- | -- |
| 製品マスタ（全項目） | product_master | id | 元: 製品マスター Excel。`product_no`（製品番号）でも検索可能 |
| 品番検索 | product_master | product_no | 他DBの `product_code` / 品番と突合する際に使用 |
| 呼出コード検索 | product_master | call_code | 元ヘッダ: 呼出ｺｰﾄﾞ |

### 主要カラム（アプリ開発でよく使う項目）

| 用途 | PostgreSQLテーブル名 | PostgreSQLカラム名 | 元Excelヘッダ | 備考 |
| -- | --------------- | -------------- | ----------- | -- |
| 主キー | product_master | id | ID | 7桁文字列。必須 |
| 品番 | product_master | product_no | 製品番号 | 製品識別の第一候補 |
| 別管理番号 | product_master | alt_management_no | 別管理番号 |  |
| 品名 | product_master | product_name | 製品名 |  |
| 客先 | product_master | customer_name | 客先名 |  |
| 次工程 | product_master | next_process | 次工程 |  |
| 材質・材料径 | product_master | material_and_diameter | 材質＆材料径 |  |
| 単価 | product_master | unit_price | 単価 | NUMERIC(15,2) |
| 材料費 | product_master | material_cost | 材料費 | NUMERIC(15,2) |
| 加工費 | product_master | machining_cost | 加工費 | NUMERIC(15,2) |
| 処理費 | product_master | processing_cost | 処理費 | NUMERIC(15,2) |
| L/T | product_master | lead_time | L/T | INTEGER |
| 梱包形態 | product_master | packing_style | 梱包形態 |  |
| 梱包仕様 | product_master | packing_spec | 梱包仕様 |  |
| 送り先 | product_master | destination_spec | 送り先指定 |  |
| 区分 | product_master | category | 区分 |  |
| IATF対象 | product_master | iatf_target | IATF   対象 |  |
| 呼出コード | product_master | call_code | 呼出ｺｰﾄﾞ |  |
| 製品単重 | product_master | unit_weight | 製品単重　　(g) | NUMERIC(15,2)、単位はグラム |

### 工程②〜⑨のカラム命名規則

Excel では「処理先」が工程ごとに重複するため、PostgreSQL では次の規則で区別する。

| 工程 | 工程名カラム | 処理先カラム | 集計カラム |
| -- | ------- | ------ | ----- |
| ② | process_2 | process_2_vendor | process_2_total |
| ③ | process_3 | process_3_vendor | process_3_total |
| ④ | process_4 | process_4_vendor | process_4_total |
| ⑤ | process_5 | process_5_vendor | process_5_total |
| ⑥ | process_6 | process_6_vendor | process_6_total |
| ⑦ | process_7 | process_7_vendor | process_7_total |
| ⑧ | process_8 | process_8_vendor | process_8_total |
| ⑨ | process_9 | process_9_vendor | process_9_total |

### 他PostgreSQL DBとの品番突合

| 他DB | 他テーブル | 他カラム | 本DBの突合カラム |
| -- | ----- | ---- | --------- |
| appearance_inspection_db | appearance_inspection_records 等 | product_code | product_master.product_no |
| delivery_label_db | 各テーブル | product_code 相当 | product_master.product_no |
| secondary_process_record_db | product_master（簡易版） | product_code | product_master.product_no |

※ `secondary_process_record_db.product_master` は列数が少ない別定義のため、詳細マスター参照時は本 `arai_masters.product_master` を使用すること。

## 7. 注意事項・要確認事項

- `create_product_master.py` 実行時は **DROP TABLE IF EXISTS** 後に再作成する。本番運用で再投入する場合はデータ消失に注意。
- Excel ファイルは実行時にスクリプト配下へ `_update_copy` 付きでコピーしてから読み込む。
- データ行は Excel 2行目（`DATA_START_ROW = 2`）から読み込む。1行目はヘッダ。
- `id`（BU列）が空の行は投入されない。
- ヘッダ名は Excel 上の全角スペースを含む文字列と完全一致が期待値。不一致時は警告ログを出すが処理は継続する。
- 本テーブルと `secondary_process_record_db` の `product_master` は**同名だが別DB・別スキーマ定義**である。接続先 DB 名で区別すること。
- 定期更新は `create_product_master.py` の手動実行、または同等ロジックのバッチで行う想定。
