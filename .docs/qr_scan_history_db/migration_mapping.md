# Access → PostgreSQL 移行対応表

## 1. 移行概要

- 対象Access DB：\\192.168.1.200\共有\QRシステム\Access\QR履歴保存DB.accdb
- 移行先PostgreSQL DB：qr_scan_history_db
- 接続情報：
  - `.env` の DATABASE_URL を参照
- 移行日：2026-06-25 11:10:48
- 作成者：Codex
- 備考：Accessの1テーブルを削除・統合せずPostgreSQLへ移行。日本語名は英語スネークケースへ変換し、元名は本対応表とDBコメントで追跡可能。

## 2. 移行対象テーブル一覧

| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | t_QR履歴保存 | qr_scan_history | TABLE | 346689 | 346689 | 成功 |

## 3. テーブル別カラム対応表

### Accessテーブル名：t_QR履歴保存
### PostgreSQLテーブル名：qr_scan_history

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | 日付時刻 | DATETIME | scanned_at | TIMESTAMP | 可 | AccessのDate/Timeをtimestampで保持 |
| 2 | QRコード | VARCHAR | qr_code | VARCHAR(22) | 可 |  |
| 3 | 生産ロットID | VARCHAR | production_lot_id | VARCHAR(7) | 可 |  |
| 4 | 日付 | DATETIME | record_date | TIMESTAMP | 可 | AccessのDate/Timeをtimestampで保持 / サンプルでは時刻が00:00:00だが、型はAccessに合わせtimestamp |
| 5 | 工程 | VARCHAR | process | VARCHAR(2) | 可 |  |
| 6 | 位置 | VARCHAR | position | VARCHAR(2) | 可 |  |
| 7 | 数量 | INTEGER | quantity | INTEGER | 可 |  |
| 8 | 工程コード | VARCHAR | process_code | VARCHAR(2) | 可 | NULL件数あり |
| 9 | 工程名 | VARCHAR | process_name | VARCHAR(30) | 可 | NULL件数あり |
| 10 | 更新フラグ | VARCHAR | update_flag | VARCHAR(1) | 可 | Access上はVARCHAR(1)のためboolean化せず文字列で保持 |

## 4. 主キー・インデックス情報

| Accessテーブル名 | PostgreSQLテーブル名 | 主キー | インデックス | 備考 |
|---|---|---|---|---|
| t_QR履歴保存 | qr_scan_history | 検出なし | 検出なし | Accessメタ情報上は主キー・インデックスなし |

## 5. 型変換ルール

| Access型 | PostgreSQL型 | 備考 |
|---|---|---|
| VARCHAR | varchar(n) | Accessの文字数を維持 |
| INTEGER | integer | 整数。NULLはNULLのまま保持 |
| DATETIME | timestamp | AccessのDate/Timeを保持 |
| BIT | boolean | 今回は該当なし |
| CURRENCY / NUMERIC | numeric | 今回は該当なし |

## 6. アプリ接続時の参照情報

### 接続先

```text
.env の DATABASE_URL を使用
```

### 主に参照するテーブル

| 用途 | PostgreSQLテーブル名 | 主なキー | 備考 |
| -- | --------------- | ---- | -- |
| QR読み取り履歴 | qr_scan_history | qr_code, production_lot_id, scanned_at | 元Access: t_QR履歴保存 |

### 主要カラム

| 用途 | PostgreSQLテーブル名 | PostgreSQLカラム名 | 元Accessカラム名 | 備考 |
| -- | --------------- | -------------- | ----------- | -- |
| QR読み取り日時 | qr_scan_history | scanned_at | 日付時刻 | Accessの値を加工せず保持 |
| QRコード | qr_scan_history | qr_code | QRコード | Accessの値を加工せず保持 |
| 生産ロットID | qr_scan_history | production_lot_id | 生産ロットID | Accessの値を加工せず保持 |
| 記録日付 | qr_scan_history | record_date | 日付 | Accessの値を加工せず保持 |
| 工程 | qr_scan_history | process | 工程 | Accessの値を加工せず保持 |
| 位置 | qr_scan_history | position | 位置 | Accessの値を加工せず保持 |
| 数量 | qr_scan_history | quantity | 数量 | Accessの値を加工せず保持 |
| 工程コード | qr_scan_history | process_code | 工程コード | Accessの値を加工せず保持 |
| 工程名 | qr_scan_history | process_name | 工程名 | Accessの値を加工せず保持 |
| 更新フラグ | qr_scan_history | update_flag | 更新フラグ | Accessの値を加工せず保持 |

## 7. 注意事項・要確認事項

- 対象フォルダ内の `.env` の `ACCESS_DB_PATH` はプレースホルダだったため、`meta.json` の `database_path` を使用。
- Accessメタ情報上、リンクテーブルは0件。移行対象は実テーブルとして扱う。
- Accessメタ情報上、主キー・インデックス・リレーションは検出なし。推測で追加していない。
- `日付` はサンプル上は日付のみだがAccess型はDATETIMEのため、PostgreSQLでは `timestamp` として保持。
- `更新フラグ` は値が `1` などの文字列フラグで、Access型もVARCHAR(1)のためbooleanへ変換していない。
- NULLが確認されたカラム: 工程コード, 工程名。NULLは空文字へ置換せず保持。
- メタ抽出警告: FK 取得スキップ: t_QR履歴保存 — ('IM001', '[IM001] [Microsoft][ODBC Driver Manager] ドライバーはこの関数をサポートしていません。 (0) (SQLForeignKeys)')
- メタ抽出警告: VBA 抽出失敗: (-2147352567, '例外が発生しました。', (0, None, '指定した式に、Visible プロパティに対する正しくない参照が含まれます。', 'dao360.chm', 2015567, -2146825833), None)
