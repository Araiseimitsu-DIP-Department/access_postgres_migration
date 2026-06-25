# Access → PostgreSQL 移行結果（order_management）

- 実行日時: 2026-06-25 09:35:57
- Access DB: C:\Users\seika\Desktop\収集ファイル\受注データDB.accdb

| Accessオブジェクト名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 投入済み件数 | 状態 | エラー |
|---|---|---:|---:|---:|---|---|
| imp管理表 | import_management_sheet | 4540 | 4540 | 4540 | 成功 |  |
| t_かんばんマスタ | kanban_master | 1 | 1 | 1 | 成功 |  |
| t_コントロール | app_control | 1 | 1 | 1 | 成功 |  |
| t_プリンタ名 | printer_names | 1 | 1 | 1 | 成功 |  |
| t_受注 | orders | 38409 | 38409 | 38409 | 成功 |  |
| t_営業マスタ | sales_rep_master | 6 | 6 | 6 | 成功 |  |
| t_客先マスタ | customer_master | 117 | 117 | 117 | 成功 |  |
| t_納品 | deliveries | 42630 | 42630 | 42630 | 成功 |  |
| t_納品書 | delivery_notes | 0 | 0 | 0 | 成功 |  |
| t_納品書データ | delivery_note_data | 0 | 0 | 0 | 成功 |  |
| t_製品マスタ | product_master | 1525 | 1525 | 1525 | 成功 |  |
| t_請求書 | invoices | 229 | 229 | 229 | 成功 |  |
| t_請求書Tmp | invoices_temp | 0 | 0 | 0 | 成功 |  |
| t_請求金額 | billing_amounts | 2072 | 2072 | 2072 | 成功 |  |
| t_請求金額決算 | billing_amounts_settlement | 44 | 44 | 44 | 成功 |  |
| t_重複客先 | duplicate_customers | 11 | 11 | 11 | 成功 |  |
