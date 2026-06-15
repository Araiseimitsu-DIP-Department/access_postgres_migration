# Access → PostgreSQL 移行結果

- 実行日時：2026-06-15 13:15:52
- Access DB：\\192.168.1.200\共有\QRシステム\Access\QR履歴保存DB.accdb

| Accessテーブル名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 投入済み件数 | 状態 | エラー |
|---|---|---:|---:|---:|---|---|
| t_QR履歴保存 | qr_scan_history | 346689 | 346689 | 346689 | 成功 |  |

## チェック結果

- Access側件数とPostgreSQL側件数をテーブル単位で比較。
- 移行失敗時の詳細は `migration_error.log` を参照。
- NULLや空文字はAccessから取得した値を加工せず投入。
