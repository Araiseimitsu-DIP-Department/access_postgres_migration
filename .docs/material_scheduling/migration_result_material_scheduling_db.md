# Access → PostgreSQL 移行結果（material_scheduling）

- 実行日時: 2026-06-25 09:35:44
- Access DB: C:\Users\seika\Desktop\収集ファイル\セット予定材料管理DB.accdb

| Accessテーブル名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 投入済み件数 | 状態 | エラー |
|---|---|---:|---:|---:|---|---|
| t_コントロール | app_control | 1 | 1 | 1 | 成功 |  |
| t_セット予定 | set_schedules | 5199 | 5199 | 5199 | 成功 |  |
| t_チャックマスタ | chuck_master | 467 | 467 | 467 | 成功 |  |
| t_一時停止 | production_pauses | 0 | 0 | 0 | 成功 |  |
| t_受信メールマスタ | inbound_email_master | 7 | 7 | 7 | 成功 |  |
| t_営業担当マスタ | sales_rep_master | 4 | 4 | 4 | 成功 |  |
| t_旧機械ID | legacy_machine_ids | 96 | 96 | 96 | 成功 |  |
| t_材料管理 | material_orders | 115 | 115 | 115 | 成功 |  |
| t_材料納入履歴 | material_delivery_history | 144 | 144 | 144 | 成功 |  |
| t_材質 | material_types | 85 | 85 | 85 | 成功 |  |
| t_機械マスタ | machine_master | 57 | 57 | 57 | 成功 |  |
| t_段取り者マスタ | setup_operator_master | 15 | 15 | 15 | 成功 |  |
| t_汎用材料マスタ | general_material_master | 0 | 0 | 0 | 成功 |  |
| t_汎用材料発注実績 | general_material_order_results | 0 | 0 | 0 | 成功 |  |
| t_注文書データ | purchase_order_documents | 2 | 2 | 2 | 成功 |  |
| t_生産リリース | production_releases | 30336 | 30336 | 30336 | 成功 |  |
| t_生産リリース のコピー | production_releases_backup | 30193 | 30193 | 30193 | 成功 |  |
| t_生産発注 | production_orders | 6375 | 6375 | 6375 | 成功 |  |
| t_発注者マスタ | orderer_master | 7 | 7 | 7 | 成功 |  |
| t_管理表マスタ | management_sheet_master | 1525 | 1525 | 1525 | 成功 |  |
| t_納入業者 | suppliers | 13 | 13 | 13 | 成功 |  |
| t_送信メールマスタ | outbound_email_master | 3 | 3 | 3 | 成功 |  |
| t_部品別チャックマスタ | part_chuck_master | 1469 | 1469 | 1469 | 成功 |  |
