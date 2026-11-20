# PostgreSQL 正規化計画

Access由来の複数DBについて、開発環境で重複や参照関係を検証し、正規化後のテーブルとアプリの接続先を段階的に設計する。調査記録、作業手順、切替条件は [計画書](docs/plan.md)、アプリとDBの対応は [NASアプリとDBの対応](docs/app-db-inventory.md) にまとめる。

作業は開発環境 `192.168.1.120` だけで行う。スクリプトとSQLは開発ホスト以外では実行を中止する。

## セットアップ

このリポジトリの Python 3.12 以上の環境を使う。未セットアップの場合は、リポジトリ直下で既存の `requirements.txt` をインストールする。DB接続には既存依存の `psycopg2-binary`、SQLの適用には `psql` を使う。

| 環境変数 | 用途 |
|---|---|
| `NORMALIZATION_DEV_HOST` | 開発PostgreSQLのホスト。省略時は `192.168.1.120`。これ以外を指定すると接続しない。 |
| `NORMALIZATION_DEV_USER` | 対象DBに接続するロール。必須。 |
| `NORMALIZATION_DEV_PASSWORD` | 接続用パスワード。認証に必要な場合に設定する。 |

ポートは5432。接続設定は実行プロセスの環境変数から取得する。認証情報はリポジトリや実行記録に保存しない。

## 実行方法

リポジトリ直下でモジュールとして実行する。

### 一括適用（開発DB専用）

製品マスタの修復と、下記の各節のSQL（12本）を README の順に一括で実行する。失敗した時点で中止し、以降の手順は実行しない。各手順は再実行しても結果が変わらない。

```powershell
$env:NORMALIZATION_DEV_USER = "postgres"
# 一覧の表示のみ（何も変更しない）
python -m access_postgres_normalization.apply_all_dev --password-file <パスワードを1行で書いたファイル>
# 適用する
python -m access_postgres_normalization.apply_all_dev --password-file <ファイル> --execute
# 戻す（*_down.sql を逆順に実行。製品マスタの修復値は戻さない）
python -m access_postgres_normalization.apply_all_dev --password-file <ファイル> --execute --down
```

- パスワードは `--password-file` か `NORMALIZATION_DEV_PASSWORD` で渡す。画面表示とログでは `***` に置き換える。
- 接続先は `NORMALIZATION_DEV_HOST` が開発ホスト（192.168.1.120）のときだけ実行する。本番（121）への適用には使えない。
- `psql` が PATH にない場合は `--psql <psql.exe のパス>` か環境変数 `PSQL` で指定する。

### 本番の内容で開発DBを作り直して正規化する（開発DB専用）

本番 `192.168.1.121` の最新の内容を開発 `192.168.1.120` に複製し、正規化済みの状態にする。毎日、最新のデータで開発DBを操作したいときに手動で実行する。

```powershell
$env:NORMALIZATION_DEV_USER = "postgres"
# 対象の一覧表示のみ（何も変更しない）
python -m access_postgres_normalization.refresh_dev_from_prod
# 複製して正規化する
python -m access_postgres_normalization.refresh_dev_from_prod --execute
```

開発DB・本番DBのパスワードは、実行時に画面で入力を求める（入力した文字は表示しない）。自動実行などで入力できない場合は、`--dev-password-file`・`--prod-password-file`（パスワードを1行で書いたファイル）か、環境変数 `NORMALIZATION_DEV_PASSWORD`・`NORMALIZATION_PROD_PASSWORD` で渡せる。その場合は入力を求めない。

| 環境変数 | 用途 |
|---|---|
| `NORMALIZATION_PROD_USER` | 本番に接続するロール。省略時は `NORMALIZATION_DEV_USER` と同じ。 |
| `NORMALIZATION_PROD_PASSWORD` | 本番のパスワード。設定すると入力を求めない（`--prod-password-file` でも可）。 |
| `PG_BIN` | `pg_dump`・`pg_restore`・`psql` のフォルダ。PATH にない場合に指定する（`--pg-bin` と同じ）。 |

- 対象は本番と開発の両方にあるDB（`postgres` を除く）。片方にしかないDBには触らない。
- **開発の対象DBは毎回削除して作り直すため、開発で入力したデータや手作業の変更は消える。** 事前のバックアップは取らない。
- 本番へは `pg_dump` とDB一覧の参照だけを、読み取り専用の接続で行う。全DBの取得に成功してから開発の作り直しを始めるため、取得に失敗した場合は開発DBは変わらない。
- 開発のDBは開発側のロケール（C）で作り直す。本番のロールは開発にないため、所有者と権限は復元しない。
- 本番の認証情報を含むユーザーマッピングは復元しない。DBごとに、本番を向く外部サーバーを開発に切り替えてから、開発の認証情報でユーザーマッピングを作り直す。
- 復元のあとに一括適用（`apply_all_dev` と同じ13手順）を実行する。最後に、本番を向く外部サーバーが残っていないことを確認する。
- 途中で失敗した場合は、失敗したDBと未処理のDBを表示して中止する。原因を直して再実行すれば、全体を最初からやり直す。

### 現品票履歴の照合（読み取りのみ）

```powershell
python -m access_postgres_normalization.audit_delivery_labels
```

外観検査・現品票の両DBを読み取り専用で照合し、全11項目が一致する行数と双方にしかない行数を出力する。元データの値をログに出力せず、テーブルへの更新も行わない。失敗時は終了コード1を返す。照合は接続ごとに行うため、厳密な同時点比較が必要な場合は更新の止まった開発スナップショットを使用する。

### 製品マスタの一本化

`arai_masters.product_master` を共通の管理元とし、`order_management.product_master` をその互換ビューに置き換える。次の順で実行する。

1. 共通製品マスタの形式崩れを修復する。既定は件数の集計のみで、`--apply` で `normalization_backup.product_master_before_repair` にバックアップしてから更新する。再実行しても変更は増えない。

   ```powershell
   python -m access_postgres_normalization.repair_arai_product_master
   python -m access_postgres_normalization.repair_arai_product_master --apply
   ```

2. 共通製品マスタに品番一意制約・変更履歴・使用中品番の変更防止を追加する。

   ```powershell
   psql -h 192.168.1.120 -U postgres -d arai_masters -v devpw=<開発DBパスワード> -f access_postgres_normalization/sql/product_master/01_arai_masters_up.sql
   ```

3. 受注管理DBの製品マスタを互換ビューへ切り替える。元の表は `normalization_backup.product_master_before_fdw` に残る。

   ```powershell
   psql -h 192.168.1.120 -U postgres -d order_management -v devpw=<開発DBパスワード> -f access_postgres_normalization/sql/product_master/02_order_management_up.sql
   ```

4. 「使用中の品番」判定で照会する列（現品票の `product_code`、委託加工の発注・納入の `product_no`）に索引を追加する。

   ```powershell
   psql -h 192.168.1.120 -U postgres -d delivery_label_db -f access_postgres_normalization/sql/product_master/03_reference_indexes_up.sql
   ```

5. 委託加工DBの製品マスタ（arai からの同期コピー）を互換ビューへ切り替える。元の表は `normalization_backup.product_master_before_fdw` に残る。切替後、委託加工の同期ツールは自動で何もしない。

   ```powershell
   psql -h 192.168.1.120 -U postgres -d subcon_manager -v devpw=<開発DBパスワード> -f access_postgres_normalization/sql/product_master/04_subcon_manager_up.sql
   ```

6. 二次工程DBの未使用の製品マスタ・機械マスタを `normalization_backup.*_unused` へ退避する（削除はしない）。

   ```powershell
   psql -h 192.168.1.120 -U postgres -d secondary_process_record_db -f access_postgres_normalization/sql/product_master/05_secondary_process_up.sql
   ```

7. 材料手配DBの機械マスタを arai_masters の互換ビューへ切り替え、未使用の仕入先表を退避する。旧表は `normalization_backup.machine_master_before_fdw`・`suppliers_unused` に残る。

   ```powershell
   psql -h 192.168.1.120 -U postgres -d material_scheduling -v devpw=<開発DBパスワード> -f access_postgres_normalization/sql/product_master/06_material_scheduling_up.sql
   ```

8. 委託加工DBの空の表 `product_master_full`（Access「製品マスター」の移行対象外の写し）を `normalization_backup.product_master_full_unused` へ退避する。委託加工アプリは起動時に `create_all` を実行するため、先にアプリのモデル `SeihinMasterFull` を外しておく。

   ```powershell
   psql -h 192.168.1.120 -U postgres -d subcon_manager -f access_postgres_normalization/sql/product_master/07_subcon_product_master_full_up.sql
   ```

各SQLは `00_require_dev.sql` を読み込み、開発DB（192.168.1.120）以外では実行を中止する。

戻す場合は番号の大きい順に `*_down.sql` を実行する（07 → 06 → 05 → 04 → 03 → 02 → 01）。修復した値は `normalization_backup.product_master_before_repair` から復元できる。

外観検査の不具合記録には、検査者・不具合種別を1行ずつ読める集計用ビューを追加する（読み取り専用、アプリの動作は変わらない）。戻す場合は同じフォルダの `01_aggregate_views_down.sql`。

```powershell
psql -h 192.168.1.120 -U postgres -d appearance_inspection_db -f access_postgres_normalization/sql/defect_information/01_aggregate_views_up.sql
```

受注・納品・委託加工の食い違いを確認する照合用ビューを追加する（読み取り専用、データとアプリの動作は変わらない）。戻す場合は同じフォルダの `*_down.sql`。

```powershell
psql -h 192.168.1.120 -U postgres -d order_performance_db -v devpw=<開発DBパスワード> -f access_postgres_normalization/sql/transactions/01_order_reconciliation_up.sql
psql -h 192.168.1.120 -U postgres -d order_management -f access_postgres_normalization/sql/transactions/02_delivery_checks_up.sql
```

材料入庫・生産リリースの未使用のバックアップ表を `normalization_backup.*_unused` へ退避し（削除はしない）、入庫が見つからない材料検査の照合用ビューと、材質マスタと一致しない入庫の材質の照合用ビュー（表記揺れの対応表 `material_kind_aliases` つき）を追加し、入庫の材質欄の表記揺れを材質マスタの材質名に寄せる（変更前の値は `normalization_backup.material_kind_fix_before` に控える）。さらに未登録の材質を材質マスタへ登録し、入庫の区分記号をそろえる（`normalization_backup.material_category_fix_before`・`material_types_added` に控える）。戻す場合は番号の大きい順に `*_down.sql`（05 → 04 → 03 → 02 → 01）。

```powershell
psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f access_postgres_normalization/sql/materials/01_unused_backups_up.sql
psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f access_postgres_normalization/sql/materials/02_inspection_checks_up.sql
psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f access_postgres_normalization/sql/materials/03_material_kind_checks_up.sql
psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f access_postgres_normalization/sql/materials/04_material_kind_fix_up.sql
psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f access_postgres_normalization/sql/materials/05_material_types_register_up.sql
```

## テスト

```powershell
python -m pytest access_postgres_normalization/tests
```
