-- 材質マスタに未登録の材質を登録し、入庫の区分記号をそろえる（開発DB専用）。04_material_kind_fix_up.sql の後に実行する。
--   現場確認（2026-11-20）: YST1 の区分記号は F。未登録の材質は材質マスタへ登録する。
--   1) 材質マスタへ登録: 材質の規格名と読めるものだけ。記号は入庫で多く使われている区分記号にする。
--      加工名・部品名（クロスバー、センターレス加工など）、総称（銅合金、SNCM、POM）、区分記号の無いもの（SD4 など）、
--      誤記の疑いがあるもの（B3604、C3406Lcd、C45CFS）は登録しない。
--   2) 表記揺れの対応表へ追加: 規格名にサイズや規格番号が付いただけのもの（303 → SUS303 など）。
--   3) 入庫: 対応表で材質名を寄せ、YST1 の区分記号を F にし、空の区分記号を材質マスタの記号で埋める。
--      ほかの既存の区分記号は変えない。
--   変更前の入庫の値は normalization_backup.material_category_fix_before に控える。戻す場合は 05_material_types_register_down.sql。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f 05_material_types_register_up.sql
\set ON_ERROR_STOP on

\ir ../product_master/00_require_dev.sql
BEGIN;

CREATE SCHEMA IF NOT EXISTS normalization_backup;

-- 1) 材質マスタへの登録（登録した材質名を控え、戻しで削除する）
CREATE TABLE IF NOT EXISTS normalization_backup.material_types_added (
  material_type varchar(20) PRIMARY KEY,
  symbol        varchar(1)  NOT NULL
);

COMMENT ON TABLE normalization_backup.material_types_added IS
  '05_material_types_register_up.sql で材質マスタに登録した材質（戻し用）';

WITH new_types (material_type, symbol) AS (VALUES
  ('1144', 'F'), ('HB-71', 'B'), ('SUS304G', 'S'), ('SUS420J2', 'S'), ('PBT（GF30％）', 'A'),
  ('SKD11', 'F'), ('C1100BD', 'B'), ('KM31-MB', 'F'), ('SUS316F', 'S'), ('C1100BD-H', 'B'),
  ('A5056-H34', 'A'), ('SKD61', 'F'), ('SUS303G', 'S'), ('C3604B', 'B'), ('SGD3', 'F'),
  ('SUS430', 'S'), ('SVJ2', 'F'), ('ASK1100BG', 'F'), ('C1020B', 'B'), ('C2700', 'B'),
  ('C27010T', 'B'), ('C3603Lcd', 'B'), ('C3607', 'B'), ('C3771', 'B'), ('C6782B', 'B'),
  ('ELCH2S', 'F'), ('G21', 'A'), ('S15C', 'F')
), inserted AS (
  INSERT INTO public.material_types (material_type, symbol)
  SELECT n.material_type, n.symbol
  FROM new_types n
  WHERE NOT EXISTS (SELECT 1 FROM public.material_types t WHERE t.material_type = n.material_type)
  RETURNING material_type, symbol
)
INSERT INTO normalization_backup.material_types_added (material_type, symbol)
SELECT material_type, symbol FROM inserted
ON CONFLICT (material_type) DO NOTHING;

-- 2) 表記揺れの対応表への追加
INSERT INTO public.material_kind_aliases (alias, material_type, reason) VALUES
  ('303',           'SUS303',   'SUS の省略'),
  ('303Cu',         'SUS303cu', 'SUS の省略・大文字小文字'),
  ('1144 ASTM A31', '1144',     '規格番号つき'),
  ('SUM22φ8.165G',  'SUM22',    'サイズつき')
ON CONFLICT (alias) DO NOTHING;

-- 3) 入庫の材質名と区分記号
CREATE TABLE IF NOT EXISTS normalization_backup.material_category_fix_before (
  id            bigint PRIMARY KEY,
  material_kind varchar(15),
  category_code varchar(1),
  backed_up_at  timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE normalization_backup.material_category_fix_before IS
  '05_material_types_register_up.sql で書き換える前の入庫の材質・区分記号（戻し用）';

CREATE TEMP TABLE material_kind_targets ON COMMIT DROP AS
SELECT h.id,
       coalesce(t_alias.material_type, t.material_type)                    AS new_kind,
       CASE
         WHEN coalesce(t_alias.material_type, t.material_type) = 'YST1' THEN 'F'
         WHEN nullif(h.category_code, '') IS NULL THEN coalesce(t_alias.symbol, t.symbol)
         ELSE h.category_code
       END                                                                 AS new_category
FROM public.material_delivery_history h
LEFT JOIN public.material_types t ON t.material_type = h.material_kind
LEFT JOIN public.material_kind_aliases a ON a.alias = h.material_kind AND t.material_type IS NULL
LEFT JOIN public.material_types t_alias ON t_alias.material_type = a.material_type
WHERE coalesce(t_alias.material_type, t.material_type) IS NOT NULL;

DELETE FROM material_kind_targets x
USING public.material_delivery_history h
WHERE h.id = x.id
  AND h.material_kind = x.new_kind
  AND h.category_code IS NOT DISTINCT FROM x.new_category;

-- 再実行時に、すでに控えた行の変更前の値を上書きしない
INSERT INTO normalization_backup.material_category_fix_before (id, material_kind, category_code)
SELECT h.id, h.material_kind, h.category_code
FROM public.material_delivery_history h
JOIN material_kind_targets x ON x.id = h.id
ON CONFLICT (id) DO NOTHING;

UPDATE public.material_delivery_history h
SET material_kind = x.new_kind,
    category_code = x.new_category
FROM material_kind_targets x
WHERE x.id = h.id;

COMMIT;
