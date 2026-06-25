# Access → PostgreSQL 移行結果（material_millsheet_manager）

- 実行日時: 2026-06-25 11:10:52
- Access DB: C:\Users\seika\Desktop\収集ファイル\材料入庫管理台帳兼ミルシート管理表DB.accdb

| Accessテーブル名 | PostgreSQLテーブル名 | Access件数 | PostgreSQL件数 | 投入済み件数 | 状態 | エラー |
|---|---|---:|---:|---:|---|---|
| t_クロス集計用 | cross_aggregation | 8 | 8 | 8 | 成功 |  |
| t_コントロール | app_control | 1 | 1 | 1 | 成功 |  |
| t_備考内容 | remarks_master | 3 | 3 | 3 | 成功 |  |
| t_旧検査データ | legacy_inspection_data | 7993 | 7993 | 7993 | 成功 |  |
| t_材料納入Tmp | material_delivery_temp | 0 | 0 | 0 | 成功 |  |
| t_材料納入履歴 | material_delivery_history | 14633 | 14633 | 14633 | 成功 |  |
| t_材料納入履歴 変更前 | material_delivery_history_before_change | 2677 | 2677 | 2677 | 成功 |  |
| t_材質 | material_types | 92 | 92 | 92 | 成功 |  |
| t_検査データ | inspection_data | 1053 | 1053 | 1053 | 成功 |  |
| t_検査員 | inspectors | 6 | 6 | 6 | 成功 |  |
| t_納入業者 | suppliers | 21 | 21 | 21 | 成功 |  |
