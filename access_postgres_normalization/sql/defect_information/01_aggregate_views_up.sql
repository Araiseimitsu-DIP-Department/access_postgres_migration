-- 外観検査の不具合記録（defect_information）を、検査者・不具合種別ごとに1行ずつ読める集計用ビューを追加する（開発DB専用）。
-- 記録の正は defect_information のまま。アプリの登録・訂正・検索は変わらない（読み取り専用ビューの追加のみ）。
-- 実行: psql -h 192.168.1.120 -U postgres -d appearance_inspection_db -f 01_aggregate_views_up.sql
-- 戻す場合は 01_aggregate_views_down.sql。
\set ON_ERROR_STOP on

BEGIN;

\ir ../product_master/00_require_dev.sql

-- 検査者: inspector_1〜10 のうち入力のある枠だけを、枠番号つきで返す
CREATE OR REPLACE VIEW public.defect_information_inspectors AS
SELECT
  d.id AS defect_id,
  d.production_lot_id,
  d.product_code,
  d.instruction_date,
  i.inspector_no,
  btrim(i.inspector_name) AS inspector_name
FROM public.defect_information d
CROSS JOIN LATERAL (VALUES
  (1, d.inspector_1), (2, d.inspector_2), (3, d.inspector_3), (4, d.inspector_4), (5, d.inspector_5),
  (6, d.inspector_6), (7, d.inspector_7), (8, d.inspector_8), (9, d.inspector_9), (10, d.inspector_10)
) AS i(inspector_no, inspector_name)
WHERE btrim(coalesce(i.inspector_name, '')) <> '';

-- 不具合種別: 件数が0以外の種別を返す。表示名は検査記録・不具合情報検索の画面と同じ。
-- 入力誤りとみられる負の件数（2026-11-19 時点で3件）も、元の表との合計を一致させるため除外しない。
CREATE OR REPLACE VIEW public.defect_information_counts AS
SELECT
  d.id AS defect_id,
  d.production_lot_id,
  d.product_code,
  d.instruction_date,
  c.display_order,
  c.defect_type,
  c.defect_label,
  c.defect_count
FROM public.defect_information d
CROSS JOIN LATERAL (VALUES
  (1, 'appearance_scratch', '外観キズ', d.appearance_scratch),
  (2, 'dent', '圧痕', d.dent),
  (3, 'cutting_chip', '切粉', d.cutting_chip),
  (4, 'mushire', '毟れ', d.mushire),
  (5, 'oversized_hole', '穴大', d.oversized_hole),
  (6, 'undersized_hole', '穴小', d.undersized_hole),
  (7, 'hole_scratch', '穴キズ', d.hole_scratch),
  (8, 'burr', 'バリ', d.burr),
  (9, 'short_length', '短寸', d.short_length),
  (10, 'rough_surface', '面粗', d.rough_surface),
  (11, 'rust', 'サビ', d.rust),
  (12, 'blur', 'ボケ', d.blur),
  (13, 'turning_mark', '挽目', d.turning_mark),
  (14, 'stain', '汚れ', d.stain),
  (15, 'plating', 'メッキ', d.plating),
  (16, 'dropped', '落下', d.dropped),
  (17, 'swelling', 'フクレ', d.swelling),
  (18, 'crush', 'ツブレ', d.crush),
  (19, 'bump', 'ボッチ', d.bump),
  (20, 'step', '段差', d.step),
  (21, 'barrel_stone', 'バレル石', d.barrel_stone),
  (22, 'diameter_plus', '径プラス', d.diameter_plus),
  (23, 'diameter_minus', '径マイナス', d.diameter_minus),
  (24, 'gauge', 'ゲージ', d.gauge),
  (25, 'foreign_matter', '異物混入', d.foreign_matter),
  (26, 'shape_defect', '形状不良', d.shape_defect),
  (27, 'abrasion', 'こすれ', d.abrasion),
  (28, 'discoloration_stain', '変色シミ', d.discoloration_stain),
  (29, 'material_scratch', '材料キズ', d.material_scratch),
  (30, 'dust', 'ゴミ', d.dust),
  (31, 'other', 'その他', d.other)
) AS c(display_order, defect_type, defect_label, defect_count)
WHERE c.defect_count <> 0;

COMMENT ON VIEW public.defect_information_inspectors IS '不具合記録の検査者を1人1行で返す集計用ビュー（正は defect_information）';
COMMENT ON VIEW public.defect_information_counts IS '不具合記録の種別ごとの件数を1種別1行で返す集計用ビュー（正は defect_information）';

COMMIT;
