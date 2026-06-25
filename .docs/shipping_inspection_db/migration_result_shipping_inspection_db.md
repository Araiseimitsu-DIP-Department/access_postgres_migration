# Access → PostgreSQL 移行結果（shipping_inspection_db）

- 実行日時: 2026-06-25 11:11:01
- Access DB: C:\Users\seika\Desktop\収集ファイル\出荷検査一覧DB.accdb

| Accessテーブル名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 投入済み件数 | 状態 | エラー |
|---|---|---:|---:|---:|---|---|
| T_先行検査一覧 | advance_inspection_list | 10 | 10 | 10 | 成功 |  |
| T_出荷データ | shipping_data | 4 | 4 | 4 | 成功 |  |
| T_出荷検査残 | shipping_inspection_remaining | 843 | 843 | 843 | 成功 |  |
| T_出荷検査残（前日） | shipping_inspection_remaining_prev_day | 843 | 843 | 843 | 成功 |  |
| T_品番別検査担当者 | product_inspection_staff | 10 | 10 | 10 | 成功 |  |
| T_工程別仕掛数 | process_wip_quantities | 166 | 166 | 166 | 成功 |  |
| T_更新日時 | db_updated_at | 1 | 1 | 1 | 成功 |  |
| T_梱包担 | packaging_staff | 9 | 9 | 9 | 成功 |  |
| T_検査時間 | inspection_duration | 1348 | 1348 | 1348 | 成功 |  |

- 合計 Access件数: 3234
- 合計 PostgreSQL件数: 3234
- 全体結果: 全テーブル件数一致
