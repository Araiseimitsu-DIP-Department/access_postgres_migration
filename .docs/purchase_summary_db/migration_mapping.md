# Access → PostgreSQL 移行対応表

## 1. 移行概要

- 対象Access DB：`\\192.168.1.200\共有\生産管理課\AccessDB\購入品集計DB.accdb`
- 移行先PostgreSQL DB：`purchase_summary_db`
- 接続情報：
  - `.env` の `DATABASE_URL` を参照
- 移行日：2026-06-25 09:38:48 東京 (標準時)
- 作成者：Codex
- 備考：Access実ファイルに接続できない場合、件数は解析済みメタデータを元に記載しています。

## 2. 移行対象テーブル一覧

| No | Accessテーブル名 | PostgreSQLテーブル名 | 種別 | Access件数 | PostgreSQL件数 | 備考 |
|---:|---|---|---|---:|---:|---|
| 1 | `t_クロス集計用` | `purchase_cross_summary` | TABLE | 25 | 25 | リンクテーブルではなく実テーブル |
| 2 | `t_コントロール` | `migration_control` | TABLE | 1 | 1 | リンクテーブルではなく実テーブル |
| 3 | `t_科目名マスタ` | `account_subject_master` | TABLE | 19 | 19 | リンクテーブルではなく実テーブル |
| 4 | `t_購入先マスタ` | `supplier_master` | TABLE | 84 | 84 | リンクテーブルではなく実テーブル |
| 5 | `t_購入品明細` | `purchase_detail` | TABLE | 45,582 | 45,632 | リンクテーブルではなく実テーブル |
| 6 | `t_購入者マスタ` | `purchaser_master` | TABLE | 44 | 44 | リンクテーブルではなく実テーブル |

## 3. テーブル別カラム対応表

### Accessテーブル名：t_クロス集計用
### PostgreSQLテーブル名：purchase_cross_summary

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | `費目コード` | VARCHAR | `expense_item_code` | VARCHAR(2) | 可 |  |
| 3 | `費目名` | VARCHAR | `expense_item_name` | VARCHAR(30) | 可 |  |
| 4 | `購入先コード` | VARCHAR | `supplier_code` | VARCHAR(3) | 可 |  |
| 5 | `購入先名` | VARCHAR | `supplier_name` | VARCHAR(30) | 可 |  |
| 6 | `購入月` | VARCHAR | `purchase_month` | VARCHAR(4) | 可 |  |
| 7 | `金額` | CURRENCY | `amount` | NUMERIC(19,4) | 可 |  |

### Accessテーブル名：t_コントロール
### PostgreSQLテーブル名：migration_control

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | `購入月From` | VARCHAR | `purchase_month_from` | VARCHAR(4) | 可 |  |
| 3 | `購入月To` | VARCHAR | `purchase_month_to` | VARCHAR(4) | 可 |  |
| 4 | `集計方法` | INTEGER | `aggregation_method` | INTEGER | 可 |  |

### Accessテーブル名：t_科目名マスタ
### PostgreSQLテーブル名：account_subject_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `科目コード` | VARCHAR | `account_subject_code` | VARCHAR(2) | 可 |  |
| 2 | `科目名` | VARCHAR | `account_subject_name` | VARCHAR(6) | 可 |  |

### Accessテーブル名：t_購入先マスタ
### PostgreSQLテーブル名：supplier_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `購入先コード` | VARCHAR | `supplier_code` | VARCHAR(3) | 可 |  |
| 2 | `購入先名` | VARCHAR | `supplier_name` | VARCHAR(20) | 可 |  |
| 3 | `費目コード` | VARCHAR | `expense_item_code` | VARCHAR(2) | 可 |  |
| 4 | `費目名` | VARCHAR | `expense_item_name` | VARCHAR(10) | 可 |  |
| 5 | `締日` | VARCHAR | `closing_day` | VARCHAR(2) | 可 |  |
| 6 | `かな` | VARCHAR | `kana` | VARCHAR(1) | 可 |  |
| 7 | `表示フラグ` | VARCHAR | `display_flag` | VARCHAR(1) | 可 |  |

### Accessテーブル名：t_購入品明細
### PostgreSQLテーブル名：purchase_detail

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `ID` | COUNTER | `id` | BIGSERIAL | 不可 | AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期 |
| 2 | `納入日` | DATETIME | `delivery_date` | TIMESTAMP | 可 |  |
| 3 | `購入先コード` | VARCHAR | `supplier_code` | VARCHAR(3) | 可 |  |
| 4 | `購入先名` | VARCHAR | `supplier_name` | VARCHAR(30) | 可 |  |
| 5 | `購入者コード` | VARCHAR | `purchaser_code` | VARCHAR(3) | 可 |  |
| 6 | `購入者名` | VARCHAR | `purchaser_name` | VARCHAR(30) | 可 |  |
| 7 | `費目コード` | VARCHAR | `expense_item_code` | VARCHAR(2) | 可 |  |
| 8 | `費目名` | VARCHAR | `expense_item_name` | VARCHAR(10) | 可 |  |
| 9 | `購入月` | VARCHAR | `purchase_month` | VARCHAR(4) | 可 |  |
| 10 | `納品書番号` | VARCHAR | `delivery_note_number` | VARCHAR(15) | 可 |  |
| 11 | `品名` | VARCHAR | `product_name` | VARCHAR(60) | 可 |  |
| 12 | `数量` | INTEGER | `quantity` | INTEGER | 可 |  |
| 13 | `単価` | DOUBLE | `unit_price` | DOUBLE PRECISION | 可 |  |
| 14 | `金額` | CURRENCY | `amount` | NUMERIC(19,4) | 可 |  |
| 15 | `単位` | VARCHAR | `unit` | VARCHAR(5) | 可 |  |
| 16 | `備考` | VARCHAR | `remarks` | VARCHAR(30) | 可 |  |
| 17 | `入力日` | DATETIME | `input_date` | TIMESTAMP | 可 |  |
| 18 | `科目名` | VARCHAR | `account_subject_name` | VARCHAR(6) | 可 |  |

### Accessテーブル名：t_購入者マスタ
### PostgreSQLテーブル名：purchaser_master

| No | Accessカラム名 | Access型 | PostgreSQLカラム名 | PostgreSQL型 | NULL許可 | 備考 |
|---:|---|---|---|---|---|---|
| 1 | `購入者コード` | VARCHAR | `purchaser_code` | VARCHAR(3) | 可 |  |
| 2 | `購入者名` | VARCHAR | `purchaser_name` | VARCHAR(10) | 可 |  |
| 3 | `かな` | VARCHAR | `kana` | VARCHAR(1) | 可 |  |
| 4 | `表示フラグ` | VARCHAR | `display_flag` | VARCHAR(1) | 可 |  |

## 4. 主キー・インデックス情報

| Accessテーブル名 | PostgreSQLテーブル名 | 主キー | インデックス | 備考 |
|---|---|---|---|---|
| `t_クロス集計用` | `purchase_cross_summary` | 未検出 | 未検出 | Access ODBCメタデータ上はPK/Index未検出。業務上の一意性は要確認。 |
| `t_コントロール` | `migration_control` | 未検出 | 未検出 | Access ODBCメタデータ上はPK/Index未検出。業務上の一意性は要確認。 |
| `t_科目名マスタ` | `account_subject_master` | 未検出 | 未検出 | Access ODBCメタデータ上はPK/Index未検出。業務上の一意性は要確認。 |
| `t_購入先マスタ` | `supplier_master` | 未検出 | 未検出 | Access ODBCメタデータ上はPK/Index未検出。業務上の一意性は要確認。 |
| `t_購入品明細` | `purchase_detail` | 未検出 | 未検出 | Access ODBCメタデータ上はPK/Index未検出。業務上の一意性は要確認。 |
| `t_購入者マスタ` | `purchaser_master` | 未検出 | 未検出 | Access ODBCメタデータ上はPK/Index未検出。業務上の一意性は要確認。 |

## 5. 型変換ルール

| Access型 | PostgreSQL型 | 備考 |
|---|---|---|
| COUNTER | bigserial | AccessのID値を投入後、setvalで次採番をMAX(id)+1に同期。PRIMARY KEY付与 |
| VARCHAR | VARCHAR(n) | Accessのcolumn_sizeを反映。 |
| DATETIME | TIMESTAMP | Accessの日付時刻を保持。日付のみかは要確認。 |
| INTEGER | INTEGER | 整数。 |
| DOUBLE | DOUBLE PRECISION | 浮動小数。 |
| CURRENCY | NUMERIC(19,4) | 金額。小数4桁を保持。 |
| YES/NO | BOOLEAN | 今回の対象列には未検出。 |

## 6. アプリ接続時の参照情報

### 接続先

```text
.env の DATABASE_URL を使用
```

### 主に参照するテーブル

| 用途 | PostgreSQLテーブル名 | 主なキー | 備考 |
| -- | --------------- | ---- | -- |
| 購入品明細 | `purchase_detail` | `id`, `purchase_month`, `supplier_code`, `purchaser_code` | 主データ。Access `t_購入品明細`。 |
| 購入先マスタ | `supplier_master` | `supplier_code` | 購入先名・費目情報。業務上一意か要確認。 |
| 購入者マスタ | `purchaser_master` | `purchaser_code` | 購入者名。業務上一意か要確認。 |
| 科目名マスタ | `account_subject_master` | `account_subject_code` | 科目コードと科目名。 |
| クロス集計用 | `purchase_cross_summary` | `id`, `purchase_month` | Access側の集計用テーブル。 |
| コントロール | `migration_control` | `id` | 集計範囲・集計方法の制御値。 |

### 主要カラム

| 用途 | PostgreSQLテーブル名 | PostgreSQLカラム名 | 元Accessカラム名 | 備考 |
| -- | --------------- | -------------- | ----------- | -- |
| 購入月 | `purchase_detail` | `purchase_month` | `購入月` | `YYMM`形式と見られるため文字列保持。 |
| 納入日 | `purchase_detail` | `delivery_date` | `納入日` | TIMESTAMP。 |
| 購入先 | `purchase_detail` | `supplier_code`, `supplier_name` | `購入先コード`, `購入先名` | マスタと併用。 |
| 購入者 | `purchase_detail` | `purchaser_code`, `purchaser_name` | `購入者コード`, `購入者名` | マスタと併用。 |
| 金額 | `purchase_detail` | `amount` | `金額` | NUMERIC(19,4)。 |
| 品名 | `purchase_detail` | `product_name` | `品名` | VARCHAR(60)。 |

## 7. 注意事項・要確認事項

- Access側のテーブル削除・統合・列削除は行っていません。
- Access ODBCメタデータ上、主キー・インデックス・リレーションは未検出です。後続でAccess画面または業務資料による確認が必要です。
- リンクテーブル相当（ODBC: SYNONYM）は0件です。
- `購入月`はサンプル上`2304`のような値のため、日付型へ変換せずVARCHAR(4)として保持しています。
- `表示フラグ`、`かな`、`締日`はAccess定義どおりVARCHARで保持しています。意味づけは要確認です。
- Access解析時警告が6件あります。主に外部キー取得スキップです。
