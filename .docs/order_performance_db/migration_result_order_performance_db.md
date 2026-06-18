# Access → PostgreSQL 移行結果（order_performance_db）

- 実行日時: 2026-06-18 11:39:26
- Access DB: C:\Users\seizo\Desktop\受注実績データ集計DB.accdb

| Accessオブジェクト名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 投入済み件数 | 状態 | エラー |
|---|---|---:|---:|---:|---|---|
| t_コントロール | app_control | 1 | 1 | 1 | 成功 |  |
| t_受注キャンセル | order_cancellations | 602 | 602 | 602 | 成功 |  |
| t_受注実績 | order_performance | 60492 | 60492 | 60492 | 成功 |  |
| t_売月 | sales_months | 156 | 156 | 156 | 成功 |  |
