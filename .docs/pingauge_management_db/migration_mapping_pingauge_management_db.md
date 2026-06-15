# Access → PostgreSQL 移行対応表

## 1. 移行概要

- 対象Access DB：\\192.168.1.200\共有\生産管理課\AccessDB\ピンゲージ管理DB.accdb
- 移行先PostgreSQL DB：pingauge_management_db
- 接続情報：
  - `.env` の DATABASE_URL を参照
- 移行日：2026-06-15 09:33:19
- 作成者：Codex
- 備考：ピンゲージ管理DBの3テーブルを統合・削除せず個別に移行。元Access名は本対応表とPostgreSQLコメントで追跡可能。

## 2. 移行対象テーブル一覧

| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | t_PGマスタ | pin_gauge_master | TABLE | 2030 | 2030 | 成功 |
| 2 | t_担当者マスタ | staff_master | TABLE | 29 | 29 | 成功 |
| 3 | t_貸出 | pin_gauge_lending | TABLE | 32229 | 32229 | 成功 |

## 3. テーブル別カラム対応表

### Accessテーブル名：t_PGマスタ
### PostgreSQLテーブル名：pin_gauge_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | サイズ | VARCHAR | size | VARCHAR(20) | 可 |  |
| 2 | 保有数 | INTEGER | owned_quantity | INTEGER | 可 |  |
| 3 | ケースNo | VARCHAR | case_no | VARCHAR(5) | 可 |  |

### Accessテーブル名：t_担当者マスタ
### PostgreSQLテーブル名：staff_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 担当者ID | VARCHAR | staff_id | VARCHAR(2) | 可 |  |
| 2 | 担当者名 | VARCHAR | staff_name | VARCHAR(5) | 可 |  |
| 3 | 部署 | VARCHAR | department | VARCHAR(2) | 可 |  |
| 4 | かな | VARCHAR | kana | VARCHAR(1) | 可 |  |
| 5 | 表示 | VARCHAR | display_flag | VARCHAR(1) | 可 |  |

### Accessテーブル名：t_貸出
### PostgreSQLテーブル名：pin_gauge_lending

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | ID | COUNTER | id | BIGINT | 不可 | AccessのCOUNTER。値を忠実に移行するためBIGINTで保持 |
| 2 | サイズ | VARCHAR | size | VARCHAR(20) | 可 |  |
| 3 | 担当者ID | VARCHAR | staff_id | VARCHAR(2) | 可 |  |
| 4 | 機番 | VARCHAR | machine_no | VARCHAR(4) | 可 |  |
| 5 | 貸出日 | DATETIME | lent_date | TIMESTAMP | 可 |  |
| 6 | 返却日 | DATETIME | returned_date | TIMESTAMP | 可 |  |
| 7 | 完了フラグ | VARCHAR | completion_flag | VARCHAR(1) | 可 | Access上でVARCHAR(1)のためboolean化せず文字列で保持 |

## 4. 主キー・インデックス情報

| Accessテーブル名 | PostgreSQLテーブル名 | 主キー | インデックス | 備考 |
|---|---|---|---|---|
| t_PGマスタ | pin_gauge_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_担当者マスタ | staff_master | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |
| t_貸出 | pin_gauge_lending | 検出なし | 検出なし | 主キー・FKはメタ未検出のため要確認 |

## 5. 型変換ルール

| Access型 | PostgreSQL型 | 備考 |
|---|---|---|
| VARCHAR | varchar(n) | Accessのサイズを維持 |
| COUNTER | bigint | 採番値を忠実に移行するためserial化せず値を保持 |
| INTEGER | integer | 整数 |
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
| ピンゲージマスタ | pin_gauge_master | size, case_no | 元Access: t_PGマスタ |
| 担当者マスタ | staff_master | staff_id | 元Access: t_担当者マスタ |
| ピンゲージ貸出履歴 | pin_gauge_lending | id, size, staff_id, machine_no, lent_date | 元Access: t_貸出 |

### 主要カラム

| 用途 | PostgreSQLテーブル名 | PostgreSQLカラム名 | 元Accessカラム名 | 備考 |
| -- | --------------- | -------------- | ----------- | -- |
| ピンゲージサイズ | pin_gauge_master | size | サイズ | Accessの値をそのまま保持 |
| 保有数 | pin_gauge_master | owned_quantity | 保有数 | Accessの値をそのまま保持 |
| ケース番号 | pin_gauge_master | case_no | ケースNo | Accessの値をそのまま保持 |
| 担当者ID | staff_master | staff_id | 担当者ID | Accessの値をそのまま保持 |
| 担当者名 | staff_master | staff_name | 担当者名 | Accessの値をそのまま保持 |
| 部署 | staff_master | department | 部署 | Accessの値をそのまま保持 |
| ID | pin_gauge_lending | id | ID | Accessの値をそのまま保持 |
| ピンゲージサイズ | pin_gauge_lending | size | サイズ | Accessの値をそのまま保持 |
| 担当者ID | pin_gauge_lending | staff_id | 担当者ID | Accessの値をそのまま保持 |
| 機番 | pin_gauge_lending | machine_no | 機番 | Accessの値をそのまま保持 |
| 貸出日 | pin_gauge_lending | lent_date | 貸出日 | Accessの値をそのまま保持 |
| 返却日 | pin_gauge_lending | returned_date | 返却日 | Accessの値をそのまま保持 |
| 完了フラグ | pin_gauge_lending | completion_flag | 完了フラグ | Accessの値をそのまま保持 |

## 7. 注意事項・要確認事項

- AccessのFKメタデータはODBCドライバが返さなかったため、外部キー制約は作成していません。要確認。
- 主キーはメタデータ上では検出なしです。COUNTER列は値を忠実に保持するためBIGINTで移行しています。
- `完了フラグ` はAccess上で文字列型のため、booleanへ変換せずVARCHAR(1)で保持しています。
- `.env` の `ACCESS_DB_PATH` が実ファイルを指していない場合は、メタJSONの `database_path` を使用します。
- メタ抽出警告：FK 取得スキップ: t_PGマスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_担当者マスタ — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：FK 取得スキップ: t_貸出 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告：VBA 抽出失敗: (-2147352567, '例外が発生しました。', (0, None, '指定した式に、Visible プロパティに対する正しくない参照が含まれます。', 'dao360.chm', 2015567, -2146825833), None)
