# 更新履歴

## 2026-06-25

- `--drop-table` の挙動を変更。`DROP SCHEMA public CASCADE` ではなく **Access 移行対象テーブルのみ** `DROP TABLE ... CASCADE` するよう `migration_common.run_pre_migration_refresh` を修正。移行後に手動追加したテーブル・索引は保持される。
- 全移行スクリプト・`purchase_summary_migrate.py`・`production_progress/migrate_access_to_pg.py` から移行対象テーブル名を `run_pre_migration_refresh` に渡すよう更新。

- `.docs/material_millsheet_manager` に `schema_app_patches.sql` / `schema_pg_english_v1.sql` を追加。Access 移行・データ投入後に incoming_material_inspection 向けの主キー（3本）・索引（3本）・BOOLEAN デフォルトを idempotent に適用する。
- `migrate_access_to_postgres_material_millsheet_manager_db.py` が `--drop-table` / `--drop-database` / `--truncate` / `--append-missing` 実行後に上記パッチを自動適用するよう変更。incoming_material_inspection 側で `001_initial_schema.sql` を実行しなくてもアプリが動作する。

- `.docs/order_management` に `schema_app_patches.sql` を追加。Access 移行・データ投入後に jucyu_manager 向けの索引（17本）・ID シーケンス（8本）を idempotent に適用する。
- `migrate_access_to_postgres_order_management_db.py` が `--drop-table` / `--drop-database` / `--truncate` / `--append-missing` 実行後に上記パッチを自動適用するよう変更。jucyu_manager 側で `001_schema.sql` を実行しなくてもアプリが動作する。

- `.docs/material_scheduling` に `schema_app_patches.sql` を追加。Access 移行・データ投入後に material_management_system 向けの列拡張（`management_sheet_master` の VARCHAR(255)）、ID シーケンス、主キー、索引、BOOLEAN デフォルトを idempotent に適用する。
- `migrate_access_to_postgres_material_scheduling_db.py` が `--drop-table` / `--drop-database` / `--truncate` / `--append-missing` 実行後に上記パッチを自動適用するよう変更。
- `schema_pg_english_v1.sql` の `management_sheet_master.material_diameter` / `next_process` を VARCHAR(255) に更新（参照 DDL をアプリ運用定義に合わせる）。

- 移行スクリプトの実行方法・CLI・ログ形式を統一。共通モジュール `src/access_migration/migration_common.py` を追加。
- 更新モードを全スクリプトで共通化: `--drop-database`（DB 削除後に再作成）/ `--drop-table`（テーブル削除後に再作成）/ `--truncate`（データのみ更新）。
- **一括更新**: プロジェクトルートで `python db_all_recreate.py` を実行し、`db_all_recreate.env` を参照。省略時は `--drop-table`。
- **個別更新**: 各 `.docs/<target>/` 内の移行スクリプトを実行し、同フォルダ内 `.env` を参照。
- ログ形式を `%(asctime)s [%(levelname)s] %(message)s` に統一（`db_all_recreate.py`・各移行スクリプト・`logger.py`）。
- 旧 CLI を置換: `--replace` → `--drop-table`、`--truncate-pg` → `--truncate`、`purchase_summary` の `--apply-schema --migrate-data` → 更新モードに統合。
- `production_progress` は `--drop-table` / `--drop-database` 時に `schema_pg_english_v1.sql` を自動適用するよう修正（一括実行時の `reservations_backup` 未存在エラーを解消）。
- `README.md` に一括・個別の実行手順を追記。
- `.docs/arai_masters` に `material_category` / `outsource_master` / `machine_master` 投入スクリプトと `arai_masters_common.py` / `update_arai_masters.py` を追加。4テーブル一括更新に対応し、`db_all_recreate.py` の arai_masters 対象を `update_arai_masters.py` に変更。
- `delivery_label_db` の移行対象から `t_QR履歴(backup_260521)` / `t_QR履歴Tmp` を除外（バックアップ・一時テーブルのため移行不要）。
- `delivery_label_defect_details` / `delivery_label_history` に `production_lot_id` の PRIMARY KEY 制約（NOT NULL・重複なし）を追加。
- COUNTER 列（BIGSERIAL）の PRIMARY KEY 化を未対応だった5 DB に拡張: `material_scheduling` / `material_millsheet_manager` / `order_management` / `order_performance_db` / `subcon_manager`（`serial_columns.py` 共通処理）。
- `serial_columns.sync_counter_sequences` を修正。0件テーブルで `setval(0)` となり失敗していた問題を解消（空テーブルは `setval(seq, 1, false)`）。

## 2026-06-24

- DDL に BIGSERIAL が定義されている5 DB の移行スクリプトで、Access COUNTER 列を **BIGSERIAL + PRIMARY KEY** 化し、投入後に `setval` でシーケンスを `MAX(id)+1` に同期する共通処理（`src/access_migration/serial_columns.py`）を適用。
- 対象: `appearance_inspection_db` / `delivery_label_db` / `pingauge_management_db` / `purchase_summary_db` / `secondary_process_record_db`
- プロジェクトルートに `db_all_recreate.py` / `db_all_recreate.env.example` を追加。`.docs` 内の移行スクリプトを一括実行し、各 DB の public スキーマを DROP 後に再作成できる。

## 2026-06-22

- `.docs/delivery_label_db` の Access DB から PostgreSQL への差分同期を実行し、15テーブルすべてで Access/PostgreSQL 件数一致を確認。
- `.docs/delivery_label_search_db` の Access DB から PostgreSQL への差分同期を実行し、`delivery_label_search` の Access/PostgreSQL 件数一致を確認。
- 既存テーブルを削除・初期化せずに同期できるよう、対象スクリプトへ不足行追記用 `--append-missing` と余剰行削除用 `--delete-extra` を整備。

- 完全切り替え時は、一時移行済みの PostgreSQL データベースにテストデータが含まれる可能性があるため、ユーザー承認のうえで対象 PostgreSQL データベースを削除し、その後 AccessDB の本番データを PostgreSQL へ再移行する。
- `delivery_label_search_db` は `delivery_label_db.delivery_label_history` に統合したため、`.docs/delivery_label_search_db` を削除。

## 2026-06-19

- `.docs/arai_masters/arai_masters_ddl.sql` に `material_category` / `outsource_master` / `machine_master` の定義を再作成。型・制約は PostgreSQL `arai_masters` 実DB、Excel列対応は `製品マスター.xls` を参照。
- `.docs/arai_masters/migration_mapping.md` に上記3テーブルの対応表を追記。
- `.docs/shipping_inspection_db` の移行ファイル消失に伴い、スクリプト・メタJSON・`.env` を再作成し `shipping_inspection_db` を `--replace` で再移行（9テーブル・3,275行一致）。

## 2026-06-18

- `.docs/order_performance_db` に **受注実績データ集計DB.accdb**（4テーブル）の Access → PostgreSQL 完全移行を実施。
- 移行スクリプト `migrate_access_to_postgres_order_performance_db.py`、英語名マッピング `name_maps.py`、対応表・結果・メタ JSON を追加。
- 移行先 PostgreSQL DB 名: `order_performance_db`（全4テーブル件数一致を確認。合計61,251行）。
- 注: ユーザー指定の `.laccdb` はロックファイルのため、本体 `.accdb` を移行元として使用。

## 2026-06-16

- `.docs/purchase_summary_db` の購入品集計DBをPostgreSQL `purchase_summary_db` へ移行。6テーブルのAccess/PostgreSQL件数が一致することを確認。
- `.docs/purchase_summary_db/purchase_summary_migrate.py`、`migration_mapping.md`、`migration_result.md`、`migration_error.log` を追加。
- `.docs/subcon_manager` に **協力会社委託加工処理品DB.accdb**（12テーブル）の Access → PostgreSQL 完全移行を実施。
- 移行スクリプト `migrate_access_to_postgres_subcon_manager_db.py`、英語名マッピング `name_maps.py`、対応表・結果・メタ JSON を追加。
- 移行先 PostgreSQL DB 名: `subcon_manager`（全12テーブル件数一致を確認。合計47,992行）。
- `.docs/order_management` に **受注データDB.accdb**（16テーブル）の Access → PostgreSQL 完全移行を実施（当初誤って `受注データApp.accdb` を移行していたため `--replace` で差し替え）。
- 移行スクリプト `migrate_access_to_postgres_order_management_db.py`、英語名マッピング `name_maps.py`、対応表・結果・メタ JSON を追加/更新。
- 移行先 PostgreSQL DB 名: `order_management`（全16テーブル件数一致を確認。合計89,393行）。
- 新規テーブル: `imp管理表` → `import_management_sheet`（4,540行）。誤移行分（`order_records`, `product_master_extended` 等5テーブル）は削除済み。

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
