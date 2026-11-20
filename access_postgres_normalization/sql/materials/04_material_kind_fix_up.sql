-- 入庫の材質欄の表記揺れを、材質マスタの材質名に寄せる（開発DB専用）。03_material_kind_checks_up.sql の後に実行する。
--   対象: material_kind_aliases に載っていて、対応先が material_types にある入庫（2026-11-20 時点で272件）。
--   material_kind を材質マスタの材質名に書き換え、区分記号が空（NULL・空文字）の行だけ材質マスタの記号で埋める（5件）。
--   すでに入っている区分記号は変えない（YST-1 の S、Ｓ93Ｄ の F など、マスタと食い違うものは現場の確認待ち）。
--   変更前の値は normalization_backup.material_kind_fix_before に控える。戻す場合は 04_material_kind_fix_down.sql。
-- 実行: psql -h 192.168.1.120 -U postgres -d material_millsheet_manager -f 04_material_kind_fix_up.sql
\set ON_ERROR_STOP on

\ir ../product_master/00_require_dev.sql
BEGIN;

CREATE SCHEMA IF NOT EXISTS normalization_backup;

CREATE TABLE IF NOT EXISTS normalization_backup.material_kind_fix_before (
  id            bigint PRIMARY KEY,
  material_kind varchar(15),
  category_code varchar(1),
  backed_up_at  timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE normalization_backup.material_kind_fix_before IS
  '04_material_kind_fix_up.sql で書き換える前の入庫の材質・区分記号（戻し用）';

-- 再実行時に、すでに控えた行の変更前の値を上書きしない
INSERT INTO normalization_backup.material_kind_fix_before (id, material_kind, category_code)
SELECT h.id, h.material_kind, h.category_code
FROM public.material_delivery_history h
JOIN public.material_kind_aliases a ON a.alias = h.material_kind
JOIN public.material_types t ON t.material_type = a.material_type
ON CONFLICT (id) DO NOTHING;

UPDATE public.material_delivery_history h
SET material_kind = t.material_type,
    category_code = CASE WHEN nullif(h.category_code, '') IS NULL THEN t.symbol ELSE h.category_code END
FROM public.material_kind_aliases a
JOIN public.material_types t ON t.material_type = a.material_type
WHERE a.alias = h.material_kind;

COMMIT;
