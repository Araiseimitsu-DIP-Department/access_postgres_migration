# Access → PostgreSQL 移行結果

- 実行日時: 2026-06-25 09:35:10
- Access DB: C:\Users\seika\Desktop\収集ファイル\現品票DB.accdb

| Accessテーブル名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 投入済み件数 | 状態 | エラー |
|---|---|---:|---:|---:|---|---|
| t_ExcelQR履歴 | excel_qr_history | 0 | 0 | 0 | 成功 |  |
| t_Excel現品票履歴 | excel_delivery_label_history | 35817 | 35817 | 35817 | 成功 |  |
| t_ID番号 | id_number | 1 | 1 | 1 | 成功 |  |
| t_QR履歴 | qr_history | 115803 | 115803 | 115803 | 成功 |  |
| t_QR履歴(backup_260521) | qr_history_backup_260521 | 106967 | 106967 | 106967 | 成功 |  |
| t_QR履歴Tmp | qr_history_tmp | 46232 | 46232 | 46232 | 成功 |  |
| t_エラーログ | error_logs | 16622 | 16622 | 16622 | 成功 |  |
| t_ロット完了理由 | lot_completion_reasons | 6 | 6 | 6 | 成功 |  |
| t_作業履歴 | work_history | 1 | 1 | 1 | 成功 |  |
| t_修正ログ | correction_logs | 9992 | 9992 | 9992 | 成功 |  |
| t_分割ロット | split_lots | 7630 | 7630 | 7630 | 成功 |  |
| t_工程マスタ | process_master | 5 | 5 | 5 | 成功 |  |
| t_数量差異 | quantity_differences | 78357 | 78357 | 78357 | 成功 |  |
| t_現品票不具合内容 | delivery_label_defect_details | 165 | 165 | 165 | 成功 |  |
| t_現品票履歴 | delivery_label_history | 136615 | 136615 | 136615 | 成功 |  |
