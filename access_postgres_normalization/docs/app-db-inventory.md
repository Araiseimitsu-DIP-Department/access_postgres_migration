# NASアプリとDBの対応（2026-11-19 調査）

NAS `normalization` フォルダの21アプリを `C:\Users\seizo\my_projects\1\normalization_workspace` に複製して調査した。NAS上の原本は変更していない。Git管理のアプリには作業ブランチ `normalization-dev` を作成した。DBの照合は開発環境 `192.168.1.120` で行い、本番 `192.168.1.121` には接続していない。

## 接続先の切替状況

全アプリの実行時設定が本番 `192.168.1.121` を指していたため、ローカル複製で次のとおり書き換えた。NAS再確認（同日）で追加・更新されたファイルはなく、21アプリで確定した。

- DB接続先：`.env`・`config.env` とコード内の既定値を開発 `192.168.1.120` に変更した。
- 認証情報：Git管理外の `.env`・`config.env` のみ開発用に差し替えた。コード内の既定値には秘密値を書き込んでいない。
- NASのファイルパス：本番の共有フォルダ（`生産管理課`・`品質保証課`・`製造課`・`QRシステム`、別名ホスト `Landisk-6ac78a` を含む）を、読み込み元・書き込み先ともに `\\192.168.1.200\共有\デジタルイノベーション推進部\社内システム移行テスト\テスト環境\` 配下へ変更した。テスト環境に無いファイル（Access DB の多く、出荷データ抽出、梱包履歴、請求書データなど）を使う機能は、テスト用ファイルを用意するまで失敗する。
- 検証：書き換え後の全設定で開発DBへ読み取り接続し、`qr_scan_history_db` を除いて接続できた。

| アプリ | 接続するDB | 設定ファイル・キー |
|---|---|---|
| astemo_label_print | astemo_label_print（schema `astemo`） | `.env` POSTGRES_CONNECTION_URL |
| defect_information_search | appearance_inspection_db, delivery_label_db, arai_masters | `.env` POSTGRES_*_CONNECTION_URL |
| dimensional_inspection_record | ベースURLのみ（DB名はコード側） | `.env`, `packaging/runtime/.env` POSTGRES_BASE_URL |
| Gauge_Management | pingauge_management_db | `.env` POSTGRES_CONNECTION_URL, DATABASE_URL |
| incoming_material_inspection | material_millsheet_manager | `.env` DATABASE_URL |
| inspection_record | appearance_inspection_db, delivery_label_db | `.env` DATABASE_URL, DELIVERY_DATABASE_URL |
| Inspection_Records_Search | appearance_inspection_db, delivery_label_db | `.env` POSTGRES_CONNECTION_URL, DELIVERY_LABEL_POSTGRES_CONNECTION_URL |
| jucyu_manager | order_management | `backend/.env` JUCYU_DB_* |
| label_print | arai_masters, delivery_label_db, production_progress | `config.env` POSTGRES_* |
| material_management_system | material_scheduling, order_management | `.env` PG_* |
| material_millsheet_manager | material_millsheet_manager | `.env` DATABASE_URL |
| murakami_kaimeido_label_print | murakami_kaimeido_label_print | `.env` POSTGRES_CONNECTION_URL |
| order_performance | order_performance_db, order_management | `.env`、`order_performance/config.py` の既定値 |
| production_progress_sheet | production_progress, material_scheduling | `.env`、`backend/db_defaults.py` の既定値 |
| qr_management | delivery_label_db, qr_scan_history_db, arai_masters | `.env` POSTGRES_*_URL |
| QRreader | appearance_inspection_db, delivery_label_db, arai_masters | `config.env` POSTGRES_* |
| quotes_manager | quotes_manager_db | `config.env` POSTGRES_* |
| secondary_process_records | secondary_process_record_db, delivery_label_db | `.env` POSTGRES_CONNECTION_URL ほか |
| shipping_inspection_list | shipping_inspection_db, delivery_label_db, appearance_inspection_db | `config.env` POSTGRES_* |
| subcon-manager | subcon_manager | `backend/.env` DATABASE_URL |
| work_in_process_search | arai_masters, delivery_label_db, order_management, material_scheduling, subcon_manager, production_progress | `.env` PG_* |

`qr_management` と `work_in_process_search` は `qr_scan_history_db` を参照する設定を持つが、開発DBに `qr_scan_history_db` は存在しない（`work_in_process_search` の PG_QR_SCAN は delivery_label_db を指している）。

## 開発DBの外部サーバー

`appearance_inspection_db` と `delivery_label_db` の外部サーバー `appearance_inspection_srv`・`arai_masters_srv` は本番を指していた。開発の `192.168.1.120` に切り替え、ユーザーマッピングの認証情報も開発用に差し替えた。切替後、外部テーブル経由の件数が開発側の実テーブルと一致した（numeric_inspection_records 33,121件、machine_master 61件）。戻し用SQLはローカル作業領域に保管し、リポジトリには置かない。

## 複数アプリが共有するテーブル

ソース中のテーブル名の出現から抽出した。`item`・`machine`・`floor` など一般語と同名のものは誤検出が多いため除外した。「書込」はSQL文の INSERT・UPDATE・DELETE を検出したアプリで、ORM経由の書き込みは未集計。

| テーブル（DB） | 参照アプリ数 | 書込を検出したアプリ |
|---|---:|---|
| delivery_label_history（delivery_label_db） | 11 | label_print, qr_management |
| product_master（arai_masters, order_management, secondary_process_record_db, subcon_manager） | 10 | material_management_system, subcon-manager |
| qr_history（delivery_label_db） | 7 | 未検出 |
| inspector_master（appearance_inspection_db） | 5 | 未検出 |
| inspectors（incoming_material_inspection, material_millsheet_manager） | 5 | 未検出 |
| orders（order_management） | 5 | 未検出 |
| numeric_inspector_master（appearance_inspection_db） | 4 | 未検出 |
| machine_master（5DB） | 4 | 未検出 |
| customers / customer_master（quotes_manager_db, subcon_manager, order_management） | 4 / 3 | 未検出 |
| app_control（5DB） | 4 | material_management_system |
| appearance_inspection_summaries（appearance_inspection_db） | 3 | QRreader |
| progress_entries（production_progress） | 3 | production_progress_sheet |
| part_master（astemo_label_print, murakami_kaimeido_label_print） | 2 | 両アプリ |

## 計画への影響

- 現品票履歴の `excel_product_slip_history`・`excel_delivery_label_history` は、どのアプリの実行コードからも参照されていない（スキーマ定義・移行・検証SQLのみ）。
- 共有の中心は `delivery_label_db.delivery_label_history` と、4DBに分かれた `product_master`。正規化の効果と影響範囲はこの2つが大きい。
- 2026-11-19 の合意により、優先度1を `delivery_label_history` と `product_master` に変更し、現品票履歴は後順位とする。

## 優先度1の詳細（開発DB 2026-11-19 時点）

Access移行は完了済みのため、開発DBの現状を正として調べた。

### `qr_scan_history_db`

`qr_management` の設定に接続URLはあるが、接続・取得メソッド（`_connect_qr_scan_history`・`_fetch_qr_scan_history`）はどこからも呼ばれていない。QR履歴の実体は `delivery_label_db.qr_history`（約15万件）。開発DBへの作成は不要。

### `delivery_label_db.delivery_label_history`

ロット単位の現品票（145,375件、主キー `production_lot_id`）。品番・品名・客先・材料・工程②〜⑨は印刷時点の値を保持する。

| 区分 | アプリと箇所 |
|---|---|
| 登録・数量更新 | label_print（`app/db.py:244` INSERT、`app/admin_service.py:665-978` INSERT・UPDATE） |
| 工程・完了・数量の更新 | qr_management（`app/repositories/postgres_repository.py:400-521` UPDATE） |
| 参照（工程②〜⑨を含む全列） | QRreader, work_in_process_search |
| 参照（ロット・品番・数量など一部列） | Inspection_Records_Search, defect_information_search, dimensional_inspection_record, inspection_record, material_management_system, secondary_process_records, shipping_inspection_list |

工程②〜⑨は6アプリ以上が列名で直接参照している。明細表に分ける場合は、既存の列構成を返す互換ビューが必要。

### `product_master`（4DB）

| DB | 件数 | キー | 更新元 | 参照アプリ |
|---|---:|---|---|---|
| arai_masters | 1,612 | `id`（主キー） | material_management_system（管理表Excelの未登録品番を追加） | label_print, QRreader, qr_management, shipping_inspection_list, work_in_process_search, defect_information_search, material_management_system, subcon-manager（同期元） |
| order_management | 1,586 | なし（品番に索引のみ） | jucyu_manager（画面の登録・更新、管理表Excelからの取込） | jucyu_manager |
| subcon_manager | 1,573 | `product_code`（主キー） | subcon-manager（arai_masters から同期。外注加工費も arai の `external_machining_cost` を同期） | subcon-manager |
| secondary_process_record_db | 4,543 | なし | なし | なし（二次工程アプリは delivery_label_history から製品一覧を作る） |

上表は切替前の状態。切替後は order_management・subcon_manager が arai の互換ビュー、secondary_process_record_db は退避済み（下記「実施結果」）。

`arai_masters.product_master` が共通マスタとして最も多く参照されている。order_management と subcon_manager は品番・品名・客先が重複し、単価・締日・担当・外注加工費など業務固有の列を持つ。

### 製品マスタ一本化の実施結果（開発DB 2026-11-19）

方針は arai_masters を正とする（合意済み）。手順と戻し方は [README](../README.md) を参照。

| 項目 | 結果 |
|---|---|
| 形式崩れの修復 | 次工程378件を受注管理・委託加工の完全な値で復元し、列を VARCHAR(255) に拡張。工程コード1,584件・締日23件を整数表記に修正。内容の食い違い（単価28件、締日3件、担当2件、品名1件、工程コード1件、次工程3件）は arai_masters の値を維持。 |
| 受注管理の切替 | order_management.product_master を外部テーブル `arai.product_master` の互換ビューに置換（1,586件、品番の過不足0）。元の表は `normalization_backup.product_master_before_fdw`。 |
| 保護 | 品番の一意制約（空欄行を除く）、`updated_at`・`updated_by`、変更履歴 `product_master_history`、受注・現品票・委託加工で使用中の品番の変更・削除を防ぐトリガー（SQLSTATE `PM001`）。使用中の判定は取引データ（受注 `orders`、現品票 `delivery_label_history`、委託加工の発注 `purchase_orders`・納入 `deliveries`）を照会し、照会列に索引を追加。 |
| 根本原因 | 移行用の生成スクリプト `.docs/arai_masters/create_product_master.py` の次工程を255文字に変更し、整数の数値セルを「42」と文字列化。切り詰めが起きた場合は警告を出す。 |
| 受注管理アプリ | 画面からの新規登録は `J00001` 形式で採番。管理表取込は「ID」列で登録し、空き確保ID行を埋める。使用中品番・重複品番の保存は409で案内。 |
| 管理表取込 | material_management_system の次工程上限を255文字に変更。受注管理と material_management_system は、どちらも管理表の「ID」列を共通製品マスタの主キーとして使う。取込ルールを変える場合は両方をそろえる。 |
| 検証 | 受注管理APIを開発DBに接続して取込（追加0・既存1,585・除外1行は従来どおり）、使用中品番の変更拒否、新規採番を確認。テストは正規化ツール13件、受注管理238件（開発用パス変更による既定値テスト2件を除く）、material_management_system 77件、subcon-manager 40件（委託加工の切替後）が成功。委託加工APIを開発DBに接続し、一覧1,586件・使用中品番の変更409・納期担当の更新と復元を確認。 |
| 委託加工の切替 | subcon_manager.product_master を arai の互換ビューに置換（1,586件。旧表1,573件はすべて含まれ、arai のみの13件が追加）。外部委託加工費・品名・客先・担当は旧表と全件一致。食い違いは次工程9件・納期担当14件で、arai の値になった（旧表は `normalization_backup.product_master_before_fdw`）。委託加工の画面での更新は arai に保存され履歴に `subcon_manager_fdw` と記録される。使用中品番の変更は409で案内。同期ツールはビューを検出して何もしない。 |
| 二次工程の製品マスタ | どのアプリ・ビュー・関数・他DBからも参照がないため `normalization_backup.product_master_unused` へ退避（削除はしていない）。現品票にあって arai にない旧品番1,298件のうち618件の情報を持つため、旧品番の参照資料として残すことを推奨。 |

## `delivery_label_history` の調査結果（開発DB 2026-11-19）

| 観点 | 結果 |
|---|---|
| 品番の参照 | `product_code_id` は arai の `id`（A+5桁）。145,375件中 131,387件が arai の品番と一致、11,333件は arai にない ID、2,631件は同じ ID が別品番を指す（改番・枝番）。品番自体が arai にない行は13,975件（1,298品番、2009年からの旧品番）。 |
| 品名・客先 | 印刷時点の値。arai と比べ品名409件、客先7,799件が異なる（客先名の変更履歴とみられる）。 |
| 工程②〜⑨ | arai の製品マスタにも同じ列があり、label_print が印刷時に写す。qr_management・label_print・QRreader・work_in_process_search などが列名で読み書きする。 |
| 値の揺れ | `issue_flag` に空文字と NULL が混在。`completion_flag` は 0〜4・9 と NULL。指示日が1年以上先の行が1件。 |

印刷時点の記録のため、品名・客先・工程を製品マスタへの参照に置き換えると過去の現品票の内容が変わる。外部キーも旧品番があるため付けられない。2026-11-19 の合意により、現品票履歴は現状の構成（印刷時点の記録）を維持し、正規化の対象外とする。

## 機械・仕入先の一本化（開発DB 2026-11-19）

### 機械マスタ

正は `arai_masters.machine_master`（61台、machine_id・machine_no・machine_sort・serial_no に一意制約）。

| DB・表 | 件数 | 利用元 | 対応 |
|---|---:|---|---|
| arai_masters.machine_master | 61 | label_print、外観検査・現品票DBの外部テーブル | 正（変更なし） |
| material_scheduling.machine_master | 59 | production_progress_sheet（機番一覧・存在確認） | arai の互換ビューに切替。旧表は `normalization_backup.machine_master_before_fdw`。`model_type` は機種末尾の数値で旧表と全件一致。arai のみの A-5・B-4 が機番一覧に加わり、D-12・F-14 の機種は arai の値（L20・L12(L16)）になった。 |
| mass_production_management.machine | 61 | NAS配置のアプリなし | `master_ref` で arai の machine_id を参照済み。変更なし |
| secondary_process_record_db.machine_master | 94 | なし（二次工程アプリは号機を現品票の文字として扱う） | `normalization_backup.machine_master_unused` へ退避（機械以外のコード34件を含む） |
| material_scheduling.legacy_machine_ids | 96 | なし | 旧ID対応表のため残す |

### 仕入先

仕入先は用途ごとにコード体系が異なり、共通する会社は1社（購買529と委託加工H18のニッケイインスツルメンツ）のみ。1つの表に統合する対象ではないため、体系ごとの管理元を確定した。

| 体系 | 管理元 | 対応 |
|---|---|---|
| 材料仕入先（01〜21） | material_millsheet_manager.suppliers（画面で登録・更新・削除） | material_scheduling.suppliers（13件の古い複製、参照なし）を `normalization_backup.suppliers_unused` へ退避 |
| 委託加工先（G01〜） | subcon_manager.supplier_master | 変更なし |
| 購買仕入先（101〜） | purchase_summary_db.suppliers | 購買アプリは正規化の対象外（2026-11-19 合意）。同じDBの旧表 `supplier_master` との二重管理もそのまま残す |

検証：production_progress_sheet を開発DBに接続し、機番一覧61台・存在確認（A-5は有、未登録の機番は無）を確認。テスト54件成功。

## 列の繰り返しの明細化（開発DB 2026-11-19）

| 表 | 判断 |
|---|---|
| appearance_inspection_db.defect_information（164,574件。検査者1〜10、不具合種別31列） | 記録の形は維持し、集計用ビューを追加（合意済み）。 |
| arai_masters.product_master の工程②〜⑨ | 管理表Excelで管理しているため、Excel運用の廃止時に扱う。 |
| secondary_process_record_db.washing_process_daily_reports（作業コード1〜18） | NAS配置のアプリが使っていないため対象外。 |
| 見積（cost_quote_*）・出荷検査（process_wip_quantities）・受注取込（import_management_sheet） | 繰り返しが少数、または取込・帳票用の一時的な形のため対象外。 |

`defect_information` の対応：

- 集計用ビュー `defect_information_inspectors`（検査者1人1行、291,611行）と `defect_information_counts`（種別ごとの件数1行）を追加。件数の合計は元の表と一致する。SQLは `sql/defect_information/`。
- 不具合情報検索アプリが検査者1〜5しか読んでおらず、6人以上の記録（26件）で6人目以降が一覧・詳細に出なかったため、検査者10人まで表示するよう修正。集計Excelは既存書式の列位置を保つため検査者1〜5のまま（列は非表示）。
- データの確認事項：不具合件数が -1 の値が3件（毟れ・メッキ・こすれ）。入力誤りとみられるが値は変更していない。総不具合数と種別合計の食い違いは3件（2023年）。

## 受注・納品・委託加工の照合（開発DB 2026-11-19）

受注実績は受注管理から新しい注文を写したあと独自に修正・取消する台帳で、納入済数・残も「完納扱い」の意味を持つため、表の統合や自動計算への置き換えはせず、照合用ビューを追加した（合意済み）。SQLは `sql/transactions/`。

| ビュー（DB） | 内容 | 件数 |
|---|---|---|
| `order_reconciliation`（order_performance_db） | 受注管理と受注実績の食い違い。注文IDのない2014〜2017年の旧データは対象外 | 内容の食い違い690（大半が2018〜2019年）、受注管理のみ804（443件は2017年）、受注実績のみ12 |
| `order_delivery_qty_check`（order_management） | 注文の納品数と納品合計の差。完納扱い（完納フラグ1・納品数＝注文数）を除く | 5 |
| `purchase_order_delivery_qty_check`（subcon_manager） | 発注の納入済数と納入合計の差。完納扱い（完了フラグE・済数＝発注数）を除く | 41（2025年以降6） |

確認事項：

- 保存された納品数が実際の合計の約2倍になっている注文・発注がある（受注管理 C3110326・C3110079〈2026年〉、委託加工 18330・18721・18722〈2025年〉）。納品の二重計上が疑われるが、変更履歴・削除処理のコードからは原因を特定できていない。
- 委託加工の「発注が見つからない納入」3,295件は、2017〜2018年の移行時の繰越データ（`deliveries_start` と同じ行）で、現在の運用では発生していない。
- 「残」が「数量−済数」と合わない行は、完納時に残を0にする仕様によるもの。

## アプリを開発で起動する前の注意

- 本番のAccess・Excel・出力先フォルダはテスト環境へ変更済み。NASから再複製した場合や新しいアプリを追加した場合は、本番パスが残っていないことを起動前に再確認する。
- `label_print` と `shipping_inspection_list` は設定に本番用・開発用の両方のキーを持つ。本番用キーの値もテスト環境に変更したが、起動時に選ばれるモードを確認してから動作確認する。
- `qr_management/database/postgresql/001_schema.sql` などのスキーマSQLには `DROP TABLE` を含むものがある。開発DBでも、実行前に対象と影響を確認する。
