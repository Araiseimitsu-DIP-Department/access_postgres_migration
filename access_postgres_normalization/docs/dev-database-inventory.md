# 開発DB全体の棚卸しと優先照合

## 対象と照合方法

開発環境 `192.168.1.120` の27DBを読み取り専用で調査した。通常テーブル418件、ビュー7件、外部テーブル4件を確認した。[従来の計画](plan.md) に加え、この一覧を以後の調査対象とする。台帳には件数や定義上の依存関係を記録し、データ値や接続認証情報は記録しない。

Web検査・在庫購買・生産進捗の7組では同名テーブル131組を抽出した。列名と型が同じ列を対象に、行のチェックサムと出現回数を比較した。共通の主キーがある場合は同一キーの差分も数えた。129組を比較し、残る2組は検証DBの `purchaser_master` との比較で、同名かつ同型の列がなかった。接続はDBごとのため、更新中のテーブルは同一時点を保証しない。

## 開発環境の外部テーブル

外観検査・現品票の両DBにある `fdw_appearance.numeric_inspection_records` と `fdw_arai.machine_master` は、外部サーバー設定が本番アドレスを指す。確認したのは開発DBのカタログ定義のみ。外部テーブルの読み取りと本番への接続は行っていない。

これらを通る画面やSQLを開発環境で試す前に、開発上の参照元・接続ロール・利用箇所を確認する。開発向けの参照先を用意する場合は、対象の外部サーバー、依存アプリ、切り戻し手順を確定する。

## 優先照合の結果

| テーブル | 左側／右側 | 一致 | 判断 |
|---|---|---:|---|
| Web検査の `web_masters` | `inspection_web` 25,164件／`appearance_sorting_web_trial` 25,103件 | 24,438件 | trial側の25,103 IDすべてが共通で、665件の内容に差がある。更新ジョブと配信元を確認する。 |
| Web検査の `inspector_legacy_records` | Web検査 2,612件／trial 2,594件 | 2,594件 | trial側が全件一致。移行や同期の履歴を確認する。 |
| Web検査の `web_master_sources` | Web検査 6件／trial 6件 | 3件 | 全6キーが共通だが3件に差がある。環境別の接続設定や参照元の違いを確認する。 |
| 出荷検査のWeb系テーブル | 出荷検査／Web検査との同名14表 | 出荷側12表が0件 | 行があるのは `web_master_refresh_runs` と `web_revision` の各1件。アプリが起動時に使用するかを確認する。 |
| 購買の `purchase_detail` | `purchase_summary_db` 47,593件／復元系 47,593件 | 47,593件 | 全件一致。復元系を参照しているアプリの有無と保全目的を確認する。 |
| 購買の `purchase_results` | 購買 48,123件／復元系 47,820件 | 47,816件 | 共通IDのうち3件は内容が異なる。 |
| 購買の `inventory_transactions` | 購買 1,100件／復元系 1,039件 | 1,039件 | 復元系の全件が含まれる。 |
| 購買の `purchase_orders` | 購買 26,585件／復元系 193件 | 187件 | データ量の差が大きい。復元系の作成・利用用途を確認する。 |
| 購買の `purchase_results` と検証系 | 購買 48,123件／検証系 17件 | 0件 | 検証データの用途を確認する。 |
| 生産進捗の `progress_entries` | 生産進捗 88,022件／試験系 85,278件 | 82,846件 | 共通20列での一致。共通85,216 IDのうち2,370件に差がある。 |

Web検査のログイン・セッション系は環境ごとの運用を確認し、業務マスタの移行対象とは別に判断する。

## アプリから確認できた読み書き

| 確認範囲 | 参照・更新経路 | 移行前に確認すること |
|---|---|---|
| 材料入荷検査アプリ `incoming_material_inspection` | PostgreSQL実装は `material_delivery_history.id` と各検査テーブルの `purchase_id` を結合する。検査登録・確認更新の書き込み先は `inspection_data` と `legacy_inspection_data`。既定の接続DB名は `material_millsheet_manager`。 | 配備時に接続先が上書きされているか確認する。ミルシートDBの現行検査1,530件は全件入庫に対応し、旧検査7,993件のうち24件に現在の入庫が見つからなかった。 |
| 量産管理アプリ `mass-production-management` | 材料同期処理は `material_millsheet_manager.public.material_delivery_history` を読み、自アプリの `material_receipt` へ同期する。同期先で `source_ref` を照合する。 | 同期元を変更する場合は、既存の参照IDと差分同期を保持し、二重取込が起きないことを確認する。 |
| Web検査と在庫購買 | 接続確認時に識別できた接続は管理ツール。対象DBには `pg_stat_statements` がなく、テーブルの累積件数だけでは利用アプリを特定できない。調査したローカルソースでは優先テーブルのアプリ実装を確認できていない。 | 配備時のDB名、ジョブ設定、画面・APIの参照と書き込みを確認する。テーブルへの過去の投入や今回の読み取りは利用状況の証拠から除く。 |

ローカル実装の根拠は [材料入荷検査のリポジトリクラス](../../../incoming_material_inspection/backend/infrastructure/postgres_inspection_repository.py#L36)、[材料入荷検査の接続設定](../../../incoming_material_inspection/backend/config.py#L15)、[量産管理の材料同期処理](../../../mass-production-management/src/mass_production_management/production/material_sync.py#L54)。

## 27DBの台帳

表数と制約は通常・パーティションテーブルの集計。主キー欄は主キーを持つテーブル数。

| DB | 表数 | 主キーあり | 外部キー | 調査方針 |
|---|---:|---:|---:|---|
| `appearance_inspection_db` | 13 | 7 | 0 | 現品票・検査。外部テーブル経由の接続先を要確認 |
| `appearance_sorting_web_trial` | 27 | 27 | 0 | Web検査。inspection_webとの重複と運用用途を確認 |
| `arai_masters` | 4 | 4 | 0 | 製品・設備・加工業者の共通マスタ候補 |
| `arai_stock_restore_20261104_finalapply` | 27 | 26 | 34 | 在庫購買の復元系候補。接続元・保管目的を確認 |
| `arai_stock_validation_20261103` | 24 | 24 | 35 | 在庫購買の検証系候補。用途と有効期限を確認 |
| `astemo_label_print` | 3 | 3 | 1 | 品番・ロット対応の照合候補 |
| `cleaning_quality_management_dev` | 37 | 37 | 37 | 清掃品質の利用者・担当者をアプリ側から確認 |
| `delivery_label_db` | 16 | 10 | 0 | 現品票・QR。外部テーブル経由の接続先を要確認 |
| `incoming_material_inspection` | 4 | 4 | 2 | 旧・現行検査とデプロイ時の接続先を確認 |
| `inspection_web` | 38 | 38 | 2 | Web検査。trialおよび出荷検査と比較済み |
| `management_system` | 0 | 0 | 0 | 業務テーブルなし |
| `mass_production_management` | 38 | 38 | 47 | 顧客・品目・設備と材料ミルシートの同期を確認 |
| `material_millsheet_manager` | 11 | 7 | 0 | 材料入庫・現行検査・旧検査の関係を確認 |
| `material_scheduling` | 23 | 13 | 0 | 材料・設備・仕入先・生産リリースを照合 |
| `murakami_kaimeido_label_print` | 2 | 2 | 1 | 品番・ロットの照合とビューの利用箇所を確認 |
| `order_management` | 20 | 15 | 0 | 受注・納品・顧客・製品の管理元を調査 |
| `order_performance_db` | 4 | 3 | 0 | 受注実績・取消の時点と保持理由を確認 |
| `part_data_reference` | 6 | 6 | 5 | 製品・出荷・不具合・段取りの参照元を確認 |
| `pingauge_management_db` | 3 | 1 | 0 | 担当者・機番と貸出データを照合 |
| `postgres` | 0 | 0 | 0 | 業務テーブルなし |
| `production_progress` | 3 | 3 | 0 | 加工進捗・予約と試験系を比較済み |
| `production_progress_test` | 2 | 2 | 0 | 試験系候補。進捗・予約に実データとの重なりあり |
| `purchase_summary_db` | 28 | 27 | 35 | 在庫購買。復元系・検証系との比較を実施 |
| `quotes_manager_db` | 32 | 32 | 0 | 顧客・製品・担当者と見積の時点を確認 |
| `secondary_process_record_db` | 16 | 6 | 0 | 二次工程・製品・作業者・機番を照合 |
| `shipping_inspection_db` | 23 | 14 | 0 | 出荷検査とWeb検査の同名表を比較済み |
| `subcon_manager` | 14 | 14 | 0 | 発注・納入・外注製品・帳票の更新元を調査 |

移行リポジトリに定義がある `qr_scan_history_db` は、今回の開発DB一覧に存在しなかった。現在のQR履歴の保存先と書き込み元を確認する。

## 移行対象を決める手順

1. 開発DBの外部テーブルとアプリの接続経路を照合する。開発での動作確認に使う参照先が開発側に閉じていることを確認する。
2. Web検査は `web_master_sources` と更新ジョブの参照元、ユーザー割当と検査履歴を書き込むアプリ、trial DBの用途を確認する。出荷検査側のWeb系テーブルは起動時や配備時の利用も確認する。
3. 在庫購買は、購買アプリ・帳票・同期ジョブの接続先を確認し、復元系と検証系の保管理由を確定する。現行購買内の品目・仕入先・発注・入庫の関連を、外部キーと画面単位で追う。
4. 材料入庫の共通化では、量産管理の `source_ref`、材料入荷検査の `purchase_id`、旧入庫未対応24件の扱いを設計条件とする。
5. 各対象で「現行の管理元」「更新するアプリ」「履歴や検証コピーの目的」「旧画面の検証条件」を記録し、確認済みのものから [移行・検証・切り戻し手順](plan.md) に沿ってDDLとデータ移行を設計する。

