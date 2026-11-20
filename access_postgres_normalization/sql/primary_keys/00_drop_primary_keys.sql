-- 01_primary_keys_up.sql で追加した主キーを外す共通処理（01_primary_keys_down.sql から \ir で読み込む）。
-- 設定 normalization.pk_targets の書式は 00_add_primary_keys.sql と同じ。
-- 制約名を指定した表は、外したあと元の一意制約（同じ名前）に戻す。
-- 主キーを外しても列の NOT NULL は残るため外す（対象の列は追加前はすべて空欄を許していた）。
DO $$
DECLARE
  item text;
  target_table text;
  key_column text;
  constraint_name text;
  original_name text;
BEGIN
  FOREACH item IN ARRAY string_to_array(current_setting('normalization.pk_targets'), ',') LOOP
    target_table := split_part(item, ':', 1);
    key_column := split_part(item, ':', 2);
    original_name := nullif(split_part(item, ':', 3), '');
    constraint_name := coalesce(original_name, target_table || '_pkey');
    IF EXISTS (SELECT 1 FROM pg_constraint
               WHERE conrelid = format('public.%I', target_table)::regclass
                 AND conname = constraint_name AND contype = 'p') THEN
      EXECUTE format('ALTER TABLE public.%I DROP CONSTRAINT %I', target_table, constraint_name);
      EXECUTE format('ALTER TABLE public.%I ALTER COLUMN %I DROP NOT NULL', target_table, key_column);
      IF original_name IS NOT NULL THEN
        EXECUTE format('ALTER TABLE public.%I ADD CONSTRAINT %I UNIQUE (%I)', target_table, original_name, key_column);
      END IF;
    END IF;
  END LOOP;
END $$;
