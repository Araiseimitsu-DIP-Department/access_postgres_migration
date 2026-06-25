# access_postgres_migration

Accessデータベース（`.accdb` / `.mdb`）をPostgreSQLへ移行するためのPythonプロジェクトです。
複数のAccessシステムをこの1つのプロジェクトで順次移行できるように、移行対象ごとの資料・設定・出力を分けて管理します。

## 目的

- Access DBの構造とデータをPostgreSQLへ安全に移行する
- 移行対象ごとの設定を分離し、再利用しやすい移行基盤にする
- 解析資料、移行対応表、実行ログ、結果レポートを追跡しやすくする

## 前提環境

- Windows
- Python 3.12
- PostgreSQL
- Access Database Engine または Access ODBCドライバ

Access DBを `pyodbc` で読み込む場合、業務PCにAccess Database Engine / ODBCドライバの追加インストールが必要になることがあります。

## フォルダ構成

```text
access_postgres_migration/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ .env.example
├─ pyproject.toml
├─ .docs/
│  ├─ appearance_inspection_db/
│  ├─ prompts/
│  ├─ migration_targets/
│  ├─ templates/
│  └─ update.md
├─ src/
│  └─ access_migration/
├─ scripts/
├─ logs/
├─ output/
└─ tests/
```

## 主なフォルダの役割

- `.docs/`: 移行対象ごとの資料、AIエージェント用プロンプト、移行対応表テンプレート、変更履歴を管理します。
- `.docs/migration_targets/`: 今後追加するAccess DBごとの解析資料や `.env` を配置します。
- `src/access_migration/`: 移行処理の本体コードを配置します。
- `scripts/`: 手動実行する補助スクリプトを配置します。
- `logs/`: 実行ログ、エラーログを出力します。
- `output/`: 移行結果や生成されたMarkdown資料を出力します。
- `tests/`: 将来的なテストコードを配置します。

## セットアップ手順

PowerShellでプロジェクトルートに移動してから実行してください。

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/check_environment.py
```

`python --version` は `3.12.x` であることを確認してください。

## .env の作成方法

### 個別移行（各 `.docs/<target>/` フォルダ）

PostgreSQL 接続情報と Access DB のパスは、**移行対象フォルダ内の `.env`** に記載します。
`.env.example` を参考に、対象フォルダへ `.env` を配置してください。

```powershell
Copy-Item .docs\appearance_inspection_db\.env.example .docs\appearance_inspection_db\.env
```

`.env` の例:

```text
DATABASE_URL=postgresql://user:password@localhost:5432/database_name
ACCESS_DB_PATH=C:/path/to/access_database.accdb
LOG_LEVEL=INFO
```

### 一括移行（プロジェクトルート）

全 DB をまとめて更新する場合は、プロジェクトルートの **`db_all_recreate.env`** を使用します。
テンプレート `db_all_recreate.env.example` をコピーして編集してください。

```powershell
Copy-Item db_all_recreate.env.example db_all_recreate.env
```

`.env` はGit管理しません。パスワードや社内DB情報を含むため、共有やコミットに注意してください。

## 移行の実行方法

すべての移行スクリプトは、次の **3つの更新モード** のいずれかを指定して実行します（`--verify-only` 等の確認専用オプション時を除く）。

| モード | 説明 |
|--------|------|
| `--drop-database` | PostgreSQL データベースを DROP 後に再作成してから移行 |
| `--drop-table` | 移行対象テーブル（public スキーマ）を DROP 後に再作成してから移行 |
| `--truncate` | テーブル構造を維持し、データのみ TRUNCATE して再投入 |

ログ形式は全スクリプト共通です: `%(asctime)s [%(levelname)s] %(message)s`

### 全 DB を一括更新

プロジェクトルートで `db_all_recreate.py` を実行します。設定は **`db_all_recreate.env`** を参照します。
実行前に各 `.docs/<target>/.env` が自動生成されます。

```powershell
# 対象一覧
python db_all_recreate.py --list

# 確認のみ（既定: --drop-table）
python db_all_recreate.py --dry-run

# 全 DB をテーブル再作成モードで更新
python db_all_recreate.py --drop-table --yes

# データのみ更新
python db_all_recreate.py --truncate --yes

# 1件だけ実行
python db_all_recreate.py --target shipping_inspection_db --drop-table --yes
```

### 個別 DB を更新

各フォルダ内の移行スクリプトを実行します。設定は **同フォルダ内の `.env`** を参照します。

```powershell
# 例: 外観検査記録DB
python .docs\appearance_inspection_db\migrate_access_to_postgres_appearance_inspection_db.py --drop-table

# 例: 出荷検査一覧DB（データのみ更新）
python .docs\shipping_inspection_db\migrate_access_to_postgres_shipping_inspection_db.py --truncate

# 例: 製品マスター（Excel 投入・4テーブル一括）
python .docs\arai_masters\update_arai_masters.py --drop-table

# 例: 個別テーブルのみ
python .docs\arai_masters\create_material_category.py --truncate
```

差分追記のみ行う場合（既存の `--append-missing` 等）は、更新モードを指定せずに実行できます。

```powershell
python .docs\delivery_label_db\migrate_access_to_postgres_delivery_label_db.py --append-missing
```

## 環境確認コマンド

プロジェクト直下の `.env` または `.env.example` を使って確認する場合:

```powershell
python scripts/check_environment.py
```

移行対象フォルダ内の `.env` を指定する場合:

```powershell
python scripts/check_environment.py --env-file .docs\migration_targets\sample_target\.env
```

この確認では実DB接続は行いません。Python 3.12、必要ライブラリ、設定値の読み込みだけを確認します。

## 注意事項

- `.env`、Access DB（`.accdb` / `.mdb`）はGit管理しないでください。
- `logs/` には実行ログ、`output/` には生成された移行資料や結果レポートを出力します。
- DBの削除、初期化、リセットなどの破壊的操作は、事前承認なしでは実行しません。
- 移行対象ごとの解析資料は `.docs/migration_targets/` 配下にまとめてください。
- 重要な変更履歴は `.docs/update.md` に記録します。
