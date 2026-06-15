# Access → PostgreSQL 移行結果

- 実行日時: 2026-06-15 09:33:19
- Access DB: \\192.168.1.200\共有\生産管理課\AccessDB\ピンゲージ管理DB.accdb

| Accessテーブル名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 投入済み件数 | 状態 | エラー |
|---|---|---:|---:|---:|---|---|
| t_PGマスタ | pin_gauge_master | 2030 | 2030 | 2030 | 成功 |  |
| t_担当者マスタ | staff_master | 29 | 29 | 29 | 成功 |  |
| t_貸出 | pin_gauge_lending | 32229 | 32229 | 32229 | 成功 |  |
