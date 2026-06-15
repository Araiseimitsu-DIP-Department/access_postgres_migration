# Access → PostgreSQL 移行対応表（production_progress）

## 1. 移行概要

| 項目 | 内容 |
|------|------|
| 対象 Access DB | `\\192.168.1.200\共有\生産管理課\AccessDB\加工進行表DB.accdb` |
| 移行先 PostgreSQL DB | `production_progress` |
| スキーマ | `public` |
| 識別子の方針 | PostgreSQL 側は **英語スネークケース**（例: `progress_entries`, `machine_no`） |
| 移行対象テーブル数 | **3 テーブルのみ**（加工進行表DB に存在する業務テーブル） |
| 移行スクリプト | `.docs/production_progress/migrate_access_to_pg.py` |
| DDL | `.docs/production_progress/schema_pg_english_v1.sql` |
| 参照メタデータ | `production_progress_sheet/.docs/加工進行表_meta.md`（2026-05-14 抽出） |

### この DB の役割（Access 側の説明）

| Access テーブル | 業務上の意味 |
|----------------|-------------|
| `t_加工進行表` | 加工の進行状況・日次実績を記録するメインテーブル |
| `t_予約` | 有効な出荷予約データ（当日・将来分の入力先） |
| `t_予約Backup` | 予約データのバックアップ／履歴（過去分の退避先） |

### 移行対象外（別 DB で管理）

加工進行表DB には ODBC 上で他テーブル（`t_機械マスタ`, `MTLINKi` 等）が見える場合がありますが、**本移行では 3 テーブルのみ**を PostgreSQL に再現します。機械マスタ・製品マスタ等は別プロジェクト／別 PostgreSQL DB で作成します。

---

## 2. 移行対象テーブル一覧

| No | Access テーブル名 | PostgreSQL テーブル名 | 種別 | 移行時件数（参考） | 備考 |
|---:|---|---|---|---:|---|
| 1 | `t_加工進行表` | `progress_entries` | TABLE | 78,628 | メインの進行・実績データ |
| 2 | `t_予約` | `reservations` | TABLE | 0 | Access 側が空の場合あり |
| 3 | `t_予約Backup` | `reservations_backup` | TABLE | 34 | 予約の履歴・退避データ |

> **件数について**: 上記は 2026-06-15 時点の移行実行結果です。Access DB は運用中に増減するため、再移行時は `--dry-run` で事前確認してください。

---

## 3. 型変換の共通ルール

誰が読んでも移行ロジックを追えるよう、Access → PostgreSQL の変換方針を先にまとめます。

### 3.1 型の対応（一覧）

| Access / ODBC 型 | PostgreSQL 型 | 変換内容 |
|------------------|---------------|----------|
| `COUNTER`（自動採番） | `BIGSERIAL` / `BIGINT` | Access の `ID` 値を **そのまま INSERT**。移行後に `setval()` でシーケンスを同期 |
| `INTEGER` | `INTEGER` | そのまま。文字列・小数が来た場合は整数へ丸め（`coerce_int_opt`） |
| `VARCHAR` | `VARCHAR(n)` | 最大長 `n` で切り詰め。空文字は `NULL` として格納（`coerce_str_optional`） |
| `DATETIME` | `DATE` | **日付部分のみ**採用（時刻は破棄）。例: `2023-01-02 00:00:00` → `2023-01-02` |

### 3.2 NULL・必須の扱い

| ルール | 説明 |
|--------|------|
| Access で NULL | PostgreSQL でも `NULL` |
| Access で空文字 `""` | 文字列列は `NULL` に正規化（移行スクリプト側） |
| `progress_entries.machine_no` | PostgreSQL は `NOT NULL`。Access で空の行は `""`（空文字）で投入 |
| `reservations` / `reservations_backup` | `shipment_date`, `machine_no` は PostgreSQL で `NOT NULL`。Access で欠ける行は **スキップ** |

### 3.3 ID（主キー）の扱い

```
Access COUNTER (ID)  ──そのまま──►  PostgreSQL BIGINT (id)
                                      │
                                      └── 移行後: setval(seq, MAX(id), true)
```

- Access の自動採番値を維持するため、`BIGSERIAL` のシーケンスは移行後に最大 ID に合わせて更新します。
- `progress_entries` で `ID` が NULL の行は移行しません（警告ログを出力）。

### 3.4 列名のゆらぎ

移行スクリプトは次の別名を同一視します。

| 想定される Access 列名 | 正規化 |
|------------------------|--------|
| `ID` / `id` | 同一 |
| `シリアルNo` / `シリアルNO` | 同一 |

---

## 4. テーブル別カラム対応表

### 4.1 `t_加工進行表` → `progress_entries`

加工の進行・日次実績を保持するメインテーブルです。

| No | Access 列名 | Access 型 | サイズ | PostgreSQL 列名 | PostgreSQL 型 | NULL | PK | 変換・備考 |
|---:|---|---|---:|---|---|---|:---:|---|
| 1 | `ID` | COUNTER | — | `id` | `BIGINT` | 不可 | ○ | Access の値をそのまま保持。欠損行はスキップ |
| 2 | `機番` | VARCHAR | 4 | `machine_no` | `VARCHAR(4)` | 不可※ | | 空の場合は `""` を設定。※PG は NOT NULL |
| 3 | `機番ソート` | VARCHAR | 3 | `machine_sort` | `VARCHAR(3)` | 可 | | 表示・並び替え用コード（例: `A01`） |
| 4 | `シリアルNo` | VARCHAR | 6 | `serial_number` | `VARCHAR(6)` | 可 | | 列名 `シリアルNO` も可 |
| 5 | `生産日` | DATETIME | — | `production_date` | `DATE` | 可 | | 日付のみ（時刻切り捨て） |
| 6 | `段取日` | DATETIME | — | `setup_date` | `DATE` | 可 | | 日付のみ |
| 7 | `客先` | VARCHAR | 30 | `customer` | `VARCHAR(30)` | 可 | | 得意先名 |
| 8 | `品番` | VARCHAR | 30 | `part_no` | `VARCHAR(30)` | 可 | | 製品・部品番号 |
| 9 | `品名` | VARCHAR | 30 | `part_name` | `VARCHAR(30)` | 可 | | 製品名 |
| 10 | `予定数` | INTEGER | — | `planned_qty` | `INTEGER` | 可 | | 生産予定数量 |
| 11 | `納期` | DATETIME | — | `due_date` | `DATE` | 可 | | 納期（日付のみ） |
| 12 | `材料` | VARCHAR | 40 | `material` | `VARCHAR(40)` | 可 | | 材料仕様・材質表記 |
| 13 | `出荷日` | DATETIME | — | `shipment_date` | `DATE` | 可 | | 出荷日（日付のみ） |
| 14 | `材料Lot` | VARCHAR | 20 | `material_lot` | `VARCHAR(20)` | 可 | | 材料ロット番号 |
| 15 | `日産数` | INTEGER | — | `daily_output_qty` | `INTEGER` | 可 | | 当日の生産数 |
| 16 | `出荷数` | INTEGER | — | `shipment_qty` | `INTEGER` | 可 | | 当日の出荷数 |
| 17 | `トラブル品対象数` | INTEGER | — | `trouble_target_qty` | `INTEGER` | 可 | | トラブル品の対象数量 |
| 18 | `トラブル品出荷数` | INTEGER | — | `trouble_shipment_qty` | `INTEGER` | 可 | | トラブル品の出荷数量 |
| 19 | `トラブル` | VARCHAR | 255 | `trouble_note` | `VARCHAR(255)` | 可 | | トラブル内容メモ |
| 20 | `変化点` | VARCHAR | 255 | `change_point` | `VARCHAR(255)` | 可 | | 変化点管理メモ |
| 21 | `備考` | VARCHAR | 255 | `remarks` | `VARCHAR(255)` | 可 | | 自由記述 |

**PostgreSQL インデックス**

| インデックス名 | 列 | 用途 |
|--------------|-----|------|
| `progress_entries_pkey` | `id` | 主キー |
| `idx_progress_entries_shipment_date` | `shipment_date` | 出荷日での検索 |
| `idx_progress_entries_machine_no` | `machine_no` | 機番での検索 |
| `idx_progress_entries_part_no` | `part_no` | 品番での検索 |

**サンプル（Access → PostgreSQL のイメージ）**

| Access `機番` | Access `出荷日` | → PostgreSQL `machine_no` | → PostgreSQL `shipment_date` |
|---------------|-----------------|---------------------------|------------------------------|
| `A-1` | `2023-01-02 00:00:00` | `A-1` | `2023-01-02` |
| `A-3` | `2023-01-02 00:00:00` | `A-3` | `2023-01-02` |

---

### 4.2 `t_予約` → `reservations`

有効な出荷予約を保持します。Access フォーム `f_データ予約入力` から INSERT / UPDATE / DELETE されます。

| No | Access 列名 | Access 型 | サイズ | PostgreSQL 列名 | PostgreSQL 型 | NULL | PK | 変換・備考 |
|---:|---|---|---:|---|---|---|:---:|---|
| 1 | `ID` | COUNTER | — | `id` | `BIGINT` | 不可 | ○ | Access の値をそのまま保持 |
| 2 | `出荷日` | DATETIME | — | `shipment_date` | `DATE` | 不可 | | 日付のみ。**必須**（欠損行はスキップ） |
| 3 | `機番` | VARCHAR | 4 | `machine_no` | `VARCHAR(4)` | 不可 | | **必須**（欠損行はスキップ） |
| 4 | `材料Lot` | VARCHAR | 20 | `material_lot` | `VARCHAR(20)` | 可 | | |
| 5 | `変化点` | VARCHAR | 255 | `change_point` | `VARCHAR(255)` | 可 | | |
| 6 | `備考` | VARCHAR | 255 | `remarks` | `VARCHAR(255)` | 可 | | |
| 7 | `トラブル` | VARCHAR | 255 | `trouble` | `VARCHAR(255)` | 可 | | 列名を英語 `trouble` に変更 |
| 8 | `出荷数` | INTEGER | — | `shipment_qty` | `INTEGER` | 可 | | |

**PostgreSQL インデックス**

| インデックス名 | 列 |
|--------------|-----|
| `reservations_pkey` | `id` |
| `idx_reservations_shipment_date` | `shipment_date` |
| `idx_reservations_machine_no` | `machine_no` |

**業務上の補足**

- Access では `出荷日` + `機番` の組み合わせで重複チェックしています（同一キーの INSERT を拒否）。
- PostgreSQL 側にはこの UNIQUE 制約は **DDL に含めていません**（Access の挙動をアプリ層で再現する想定）。

---

### 4.3 `t_予約Backup` → `reservations_backup`

予約データのバックアップ／履歴テーブルです。列構成は `t_予約` と同一です。

| No | Access 列名 | Access 型 | サイズ | PostgreSQL 列名 | PostgreSQL 型 | NULL | PK | 変換・備考 |
|---:|---|---|---:|---|---|---|:---:|---|
| 1 | `ID` | COUNTER | — | `id` | `BIGINT` | 不可 | ○ | Access の値をそのまま保持 |
| 2 | `出荷日` | DATETIME | — | `shipment_date` | `DATE` | 不可 | | 日付のみ |
| 3 | `機番` | VARCHAR | 4 | `machine_no` | `VARCHAR(4)` | 不可 | | |
| 4 | `材料Lot` | VARCHAR | 20 | `material_lot` | `VARCHAR(20)` | 可 | | |
| 5 | `変化点` | VARCHAR | 255 | `change_point` | `VARCHAR(255)` | 可 | | |
| 6 | `備考` | VARCHAR | 255 | `remarks` | `VARCHAR(255)` | 可 | | |
| 7 | `トラブル` | VARCHAR | 255 | `trouble` | `VARCHAR(255)` | 可 | | |
| 8 | `出荷数` | INTEGER | — | `shipment_qty` | `INTEGER` | 可 | | |

**PostgreSQL インデックス**

| インデックス名 | 列 |
|--------------|-----|
| `reservations_backup_pkey` | `id` |

> `reservations` と同型ですが、インデックスは主キーのみです（DDL 定義どおり）。

---

## 5. 英語列名対応クイックリファレンス

アプリや SQL を書く人向けに、日本語 ↔ 英語の対応を 1 表にまとめます。

### `progress_entries`（旧 `t_加工進行表`）

| 日本語（Access） | 英語（PostgreSQL） |
|------------------|-------------------|
| ID | `id` |
| 機番 | `machine_no` |
| 機番ソート | `machine_sort` |
| シリアルNo | `serial_number` |
| 生産日 | `production_date` |
| 段取日 | `setup_date` |
| 客先 | `customer` |
| 品番 | `part_no` |
| 品名 | `part_name` |
| 予定数 | `planned_qty` |
| 納期 | `due_date` |
| 材料 | `material` |
| 出荷日 | `shipment_date` |
| 材料Lot | `material_lot` |
| 日産数 | `daily_output_qty` |
| 出荷数 | `shipment_qty` |
| トラブル品対象数 | `trouble_target_qty` |
| トラブル品出荷数 | `trouble_shipment_qty` |
| トラブル | `trouble_note` |
| 変化点 | `change_point` |
| 備考 | `remarks` |

### `reservations` / `reservations_backup`（旧 `t_予約` / `t_予約Backup`）

| 日本語（Access） | 英語（PostgreSQL） |
|------------------|-------------------|
| ID | `id` |
| 出荷日 | `shipment_date` |
| 機番 | `machine_no` |
| 材料Lot | `material_lot` |
| 変化点 | `change_point` |
| 備考 | `remarks` |
| トラブル | `trouble` |
| 出荷数 | `shipment_qty` |

---

## 6. ER 図（参考）

外部キーは Access メタデータ上検出されていません。3 テーブルは論理的に独立しています。

```mermaid
erDiagram
    progress_entries {
        bigint id PK
        varchar machine_no
        varchar machine_sort
        varchar serial_number
        date production_date
        date setup_date
        varchar customer
        varchar part_no
        varchar part_name
        int planned_qty
        date due_date
        varchar material
        date shipment_date
        varchar material_lot
        int daily_output_qty
        int shipment_qty
        int trouble_target_qty
        int trouble_shipment_qty
        varchar trouble_note
        varchar change_point
        varchar remarks
    }

    reservations {
        bigint id PK
        date shipment_date
        varchar machine_no
        varchar material_lot
        varchar change_point
        varchar remarks
        varchar trouble
        int shipment_qty
    }

    reservations_backup {
        bigint id PK
        date shipment_date
        varchar machine_no
        varchar material_lot
        varchar change_point
        varchar remarks
        varchar trouble
        int shipment_qty
    }
```

---

## 7. 移行手順（再現用）

### 7.1 スキーマ作成

```powershell
pwsh .\.docs\production_progress\apply_pg_schema.ps1
```

または:

```powershell
psql "postgresql://USER:PASS@HOST:5432/production_progress" -f .\.docs\production_progress\schema_pg_english_v1.sql
```

### 7.2 件数確認（ドライラン）

```powershell
python .\.docs\production_progress\migrate_access_to_pg.py --dry-run
```

### 7.3 本番移行（既存データを空にしてから投入）

```powershell
python .\.docs\production_progress\migrate_access_to_pg.py --truncate-pg
```

### 7.4 環境変数

| 変数名 | 用途 | 例 |
|--------|------|-----|
| `PRODUCTION_PROGRESS_PG_DSN` | PostgreSQL 接続 URI | `postgresql://postgres:***@192.168.1.120:5432/production_progress` |
| `PRODUCTION_PROGRESS_ACCESS_DB` | Access `.accdb` パス | `\\192.168.1.200\共有\生産管理課\AccessDB\加工進行表DB.accdb` |

---

## 8. 関連ファイル

| ファイル | 説明 |
|----------|------|
| `schema_pg_english_v1.sql` | PostgreSQL DDL（3 テーブル） |
| `migrate_access_to_pg.py` | データ移行本体 |
| `apply_pg_schema.ps1` | DDL 適用ヘルパ |
| `migrate_support/access_to_pg_maps.py` | 列マッピング実装 |
| `migrate_support/coercion.py` | 型変換実装 |
| `migrate_support/access_connection.py` | 接続・既定値 |

---

## 9. 未確定・注意事項

| 項目 | 内容 |
|------|------|
| 外部キー | Access 上は未検出。`機番` と機械マスタの参照整合はアプリ／別 DB で担保 |
| `DATETIME` → `DATE` | 時刻情報は保持しない。将来 TIMESTAMP が必要なら DDL 変更が必要 |
| `t_予約` の件数 | 運用タイミングにより 0 件になることがある（正常） |
| 文字コード | 日本語・半角カナ混在データあり。PostgreSQL は UTF-8 でそのまま格納 |
| 再移行 | `--truncate-pg` は対象 3 テーブルを **TRUNCATE** する（取り消し不可） |

---

*作成: 2026-06-15 / 根拠: `schema_pg_english_v1.sql`, `migrate_access_to_pg.py`, `加工進行表_meta.md`*
