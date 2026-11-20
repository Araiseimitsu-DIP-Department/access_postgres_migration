-- 材料入庫の材質（material_delivery_history.material_kind）と材質マスタ（material_types）の照合用の表とビューを追加する（開発DB専用）。
--   調査結果（2026-11-20、本番から複製した開発DB）:
--     入庫15,175件のうち14,689件（97%）は材質マスタと完全一致。不一致は60種類・486件。
--     不一致のうち10種類・272件は全角半角・大小文字・ハイフン・括弧の違いだけ（例: SUS303Cu → マスタは SUS303cu）。
--     材料ミルシート管理アプリは材質名の完全一致で区分記号を引くため、表記が揺れると区分記号が空になる。
--   入庫データ・材質マスタの値は変更しない。表記揺れの対応表と照合ビューを追加するだけ。
--   material_types には主キーが無いため、対応表に外部キーは付けない（対応先の欠落はビューで検出する）。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f 03_material_kind_checks_up.sql
-- 戻す場合は 03_material_kind_checks_down.sql。
\set ON_ERROR_STOP on

\ir ../product_master/00_require_dev.sql
BEGIN;

CREATE TABLE IF NOT EXISTS public.material_kind_aliases (
  alias         varchar(20) PRIMARY KEY,
  material_type varchar(20) NOT NULL,
  reason        text        NOT NULL
);

COMMENT ON TABLE public.material_kind_aliases IS
  '入庫の材質欄の表記揺れと、材質マスタ（material_types）の正しい材質名の対応表';

-- 表記の違いだけで材質マスタの1件に決まるもの。意味の判断が要るもの（HB-71、1144 など）は入れない。
INSERT INTO public.material_kind_aliases (alias, material_type, reason) VALUES
  ('SUS303Cu',    'SUS303cu',     '大文字小文字'),
  ('POM（白）',   'POM(白）',     '括弧の全角半角'),
  ('YST-1',       'YST1',         'ハイフン'),
  ('KM-31',       'K-M31',        'ハイフンの位置'),
  ('KM31',        'K-M31',        'ハイフン'),
  ('C3604(一般)', 'C3604（一般）', '括弧の全角半角'),
  ('Ｓ20Ｃ',      'S20C',         '全角英字'),
  ('Ｓ93Ｄ',      'S93D',         '全角英字'),
  ('C2700-H',     'C2700H',       'ハイフン'),
  ('G23T-8',      'G23-T8',       'ハイフンの位置')
ON CONFLICT (alias) DO NOTHING;

-- 材質マスタと一致しない入庫を、材質・区分記号ごとに集計する。
CREATE OR REPLACE VIEW public.material_kind_checks AS
SELECT
  h.material_kind,
  h.category_code,
  count(*)                    AS delivery_count,
  max(h.receipt_date)::date   AS last_receipt_date,
  a.material_type             AS suggested_material_type,
  t.symbol                    AS suggested_symbol,
  CASE
    WHEN nullif(h.material_kind, '') IS NULL THEN '材質空欄'
    WHEN a.alias IS NULL THEN 'マスタ未登録'
    WHEN t.material_type IS NULL THEN '対応先がマスタに無い'
    ELSE '表記揺れ'
  END                         AS check_result
FROM public.material_delivery_history h
LEFT JOIN public.material_kind_aliases a ON a.alias = h.material_kind
LEFT JOIN public.material_types t ON t.material_type = a.material_type
WHERE NOT EXISTS (SELECT 1 FROM public.material_types m WHERE m.material_type = h.material_kind)
GROUP BY h.material_kind, h.category_code, a.alias, a.material_type, t.material_type, t.symbol;

COMMENT ON VIEW public.material_kind_checks IS
  '材質マスタと一致しない入庫の材質。表記揺れは対応表（material_kind_aliases）の材質名を示す。照合用の読み取り専用ビュー';

COMMIT;
