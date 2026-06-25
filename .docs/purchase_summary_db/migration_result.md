# Access → PostgreSQL 移行結果

- 実行日時：2026-06-25 11:14:05 東京 (標準時)
- 対象Access DB：`\\192.168.1.200\共有\生産管理課\AccessDB\購入品集計DB.accdb`
- 移行先PostgreSQL DB：`purchase_summary_db`
- スキーマ作成：実行
- データ移行：実行

## 件数確認

| Accessテーブル名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 差異 |
|---|---|---:|---:|---:|
| `t_クロス集計用` | `purchase_cross_summary` | 25 | 25 | 0 |
| `t_コントロール` | `migration_control` | 1 | 1 | 0 |
| `t_科目名マスタ` | `account_subject_master` | 19 | 19 | 0 |
| `t_購入先マスタ` | `supplier_master` | 84 | 84 | 0 |
| `t_購入品明細` | `purchase_detail` | 45,582 | 45,632 | 50 |
| `t_購入者マスタ` | `purchaser_master` | 44 | 44 | 0 |

## エラー

- なし

## 注意事項

- Access側のテーブル削除・統合・列削除は行っていません。
- Access ODBCメタデータ上、主キー・インデックス・リレーションは未検出です。後続でAccess画面または業務資料による確認が必要です。
- リンクテーブル相当（ODBC: SYNONYM）は0件です。
- `購入月`はサンプル上`2304`のような値のため、日付型へ変換せずVARCHAR(4)として保持しています。
- `表示フラグ`、`かな`、`締日`はAccess定義どおりVARCHARで保持しています。意味づけは要確認です。
- Access解析時警告が6件あります。主に外部キー取得スキップです。
