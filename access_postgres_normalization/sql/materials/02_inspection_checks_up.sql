-- 材料入荷検査の purchase_id（= material_delivery_history.id）に対応する入庫がない検査を一覧する照合用ビューを追加する（開発DB専用）。
-- 材料ミルシート管理アプリは入庫を削除できるため、外部キーは付けない（付けると削除操作の動作が変わる）。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f 02_inspection_checks_up.sql
-- 戻す場合は 02_inspection_checks_down.sql。
\set ON_ERROR_STOP on

BEGIN;

\ir ../product_master/00_require_dev.sql

CREATE OR REPLACE VIEW public.material_inspection_orphans AS
SELECT 'inspection_data'::text AS source_table, i.id AS inspection_id, i.purchase_id, i.inspector_name, i.judgment_result
FROM public.inspection_data i
WHERE NOT EXISTS (SELECT 1 FROM public.material_delivery_history m WHERE m.id = i.purchase_id)
UNION ALL
SELECT 'legacy_inspection_data', l.id, l.purchase_id, l.inspector_name, l.judgment_result
FROM public.legacy_inspection_data l
WHERE NOT EXISTS (SELECT 1 FROM public.material_delivery_history m WHERE m.id = l.purchase_id);

COMMENT ON VIEW public.material_inspection_orphans IS
  '入庫（material_delivery_history）が見つからない材料検査。照合用の読み取り専用ビュー';

COMMIT;
