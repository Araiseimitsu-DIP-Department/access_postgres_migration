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

各SQLは `00_require_dev.sql` を読み込み、開発DB（192.168.1.120）以外では実行を中止する。

戻す場合は `03_reference_indexes_down.sql`、`02_order_management_down.sql`、`01_arai_masters_down.sql` の順に実行する。修復した値は `normalization_backup.product_master_before_repair` から復元できる。

## テスト

```powershell
python -m pytest access_postgres_normalization/tests
```
