# 更新履歴

## 2026-06-16

<<<<<<< HEAD
- `.docs/purchase_summary_db` の購入品集計DBをPostgreSQL `purchase_summary_db` へ移行。6テーブルのAccess/PostgreSQL件数が一致することを確認。
- `.docs/purchase_summary_db/purchase_summary_migrate.py`、`migration_mapping.md`、`migration_result.md`、`migration_error.log` を追加。
=======
- `.docs/order_management` に **受注データDB.accdb**（16テーブル）の Access → PostgreSQL 完全移行を実施（当初誤って `受注データApp.accdb` を移行していたため `--replace` で差し替え）。
- 移行スクリプト `migrate_access_to_postgres_order_management_db.py`、英語名マッピング `name_maps.py`、対応表・結果・メタ JSON を追加/更新。
- 移行先 PostgreSQL DB 名: `order_management`（全16テーブル件数一致を確認。合計89,393行）。
- 新規テーブル: `imp管理表` → `import_management_sheet`（4,540行）。誤移行分（`order_records`, `product_master_extended` 等5テーブル）は削除済み。
>>>>>>> 8fa45cfcc1da3652f471bb835e4dc28e7b87f12a

## 2026-06-15

- `.docs/material_millsheet_manager` に材料入庫管理台帳兼ミルシート管理表DB（11テーブル）の Access → PostgreSQL 完全移行を実施。
- 移行スクリプト `migrate_access_to_postgres_material_millsheet_manager_db.py`、英語名マッピング `name_maps.py`、対応表・結果・メタ JSON を追加。
- 移行先 PostgreSQL DB 名: `material_millsheet_manager`（全テーブル件数一致を確認）。当初誤って `material_milsheet_manager` へ投入したため、正しい DB 名へ再移行済み。誤DB `material_milsheet_manager` は削除済み。
- `.docs/material_scheduling` にセット予定材料管理DB（23テーブル）の Access → PostgreSQL 完全移行を実施。
- 移行スクリプト `migrate_access_to_postgres_material_scheduling_db.py`、英語名マッピング `name_maps.py`、DDL `schema_pg_english_v1.sql`、対応表・結果・メタ JSON を追加。
- 移行先 PostgreSQL DB 名: `material_scheduling`（全テーブル件数一致を確認）。
- `.docs/qr_scan_history_db` のQR履歴保存DBをPostgreSQL `qr_scan_history_db` へ移行。`qr_scan_history` テーブルのAccess/PostgreSQL件数が346,689件で一致することを確認。
- `.docs/qr_scan_history_db/migrate_access_to_postgres_qr_scan_history_db.py`、`migration_mapping.md`、`migration_result.md`、`migration_error.log` を追加。
- `production_progress_sheet` から加工進行表DB（3テーブル）の移行スクリプトを `.docs/production_progress` へコピー。`migrate_access_to_pg.py`、`schema_pg_english_v1.sql`、`apply_pg_schema.ps1`、`migrate_support/`。
- `.docs/production_progress/migration_mapping_production_progress.md` を追加。Access↔PostgreSQL のテーブル・列・型対応を文書化。

## 2026-06-12

- Access → PostgreSQL移行プロジェクトの初期構成を作成。
- 環境確認スクリプト、設定読み込み、ログ初期化、移行入口を追加。
- `.docs/appearance_inspection_db` のAccess DBをPostgreSQLへ移行。
- 移行対応表、移行結果、移行ログ、再実行用スクリプトを追加。
- `.docs/delivery_label_search_db` のAccess DBをPostgreSQLへ移行。
- 汎用移行スクリプトをメタJSON自動検出と対象別対応表生成に対応。
- 移行用Pythonスクリプトを共通配置ではなく各対象フォルダ配下へ保存する運用に変更。
- `.docs/delivery_label_search_db/migrate_access_to_postgres_delivery_label_search_db.py` を現品票検索DB専用の処理に整理。
- `.docs/appearance_inspection_db/migrate_access_to_postgres_appearance_inspection_db.py` を外観検査記録DB専用の処理に整理。
- 外観検査記録DBの再確認で、Access本体更新に伴う3テーブルの件数差異を記録。
- 対象専用の移行スクリプト名に対象フォルダ名を含める命名へ変更。
- 外観検査記録DBの移行成果物名に `appearance_inspection_db` を含める命名へ変更。
- 現品票検索DBの移行成果物名に `delivery_label_search_db` を含める命名へ変更。
- `.docs/delivery_label_db` のAccess DBをPostgreSQLへ移行。
- 現品票DB専用スクリプト `.docs/delivery_label_db/migrate_access_to_postgres_delivery_label_db.py` を追加。
- 現品票DBの移行成果物名に `delivery_label_db` を含める命名で生成。
- 稼働中Access DBとの差分追記用に、削除・初期化を行わない `--append-missing` を追加。
- `.docs/secondary_process_record_db` のAccess DBをPostgreSQLへ移行。
- 社内二次工程記録DB専用スクリプト `.docs/secondary_process_record_db/migrate_access_to_postgres_secondary_process_record_db.py` を追加。
- 社内二次工程記録DBの移行成果物名に `secondary_process_record_db` を含める命名で生成。
- `.docs/pingauge_management_db` のAccess DBをPostgreSQLへ移行。
- ピンゲージ管理DB専用スクリプト `.docs/pingauge_management_db/migrate_access_to_postgres_pingauge_management_db.py` を追加。
- ピンゲージ管理DBの移行成果物名に `pingauge_management_db` を含める命名で生成。
