-- 主キーを追加する共通処理（01_primary_keys_up.sql から \ir で読み込む）。
-- 呼び出し側でトランザクション内に SET LOCAL normalization.pk_targets で対象を設定する。
--   書式: "表:列" をカンマ区切り。3つ目に制約名を書くと、その名前で主キーを作る
--         （同名の一意制約がある場合は主キーに置き換える。アプリが制約名でエラーを見分けている表に使う）。
-- 先に全表の空欄・重複を確認し、1件でもあれば何も変更せずに中止する（本番データの移行時の失敗を防ぐ）。
-- 既に主キーがある表は飛ばすため、再実行しても結果は変わらない。
DO $$
DECLARE
  item text;
  target_table text;
  key_column text;
  constraint_name text;
  null_count bigint;
  duplicate_count bigint;
  problems text[] := '{}';
  pending_items text[] := '{}';  -- 主キーがまだない表だけを残す（確認と追加で同じ対象を使う）
BEGIN
  FOREACH item IN ARRAY string_to_array(current_setting('normalization.pk_targets'), ',') LOOP
    target_table := split_part(item, ':', 1);
    key_column := split_part(item, ':', 2);
    CONTINUE WHEN EXISTS (SELECT 1 FROM pg_constraint
                          WHERE conrelid = format('public.%I', target_table)::regclass AND contype = 'p');
    pending_items := pending_items || item;
    EXECUTE format('SELECT count(*) - count(%1$I), count(%1$I) - count(DISTINCT %1$I) FROM public.%2$I',
                   key_column, target_table)
      INTO null_count, duplicate_count;
    IF null_count > 0 OR duplicate_count > 0 THEN
      problems := problems || format('%s.%s（空欄 %s件・重複 %s件）', target_table, key_column, null_count, duplicate_count);
    END IF;
  END LOOP;
  IF cardinality(problems) > 0 THEN
    RAISE EXCEPTION '主キーにできない値があるため中止しました: %', array_to_string(problems, '、');
  END IF;

  FOREACH item IN ARRAY pending_items LOOP
    target_table := split_part(item, ':', 1);
    key_column := split_part(item, ':', 2);
    constraint_name := coalesce(nullif(split_part(item, ':', 3), ''), target_table || '_pkey');
    IF EXISTS (SELECT 1 FROM pg_constraint
               WHERE conrelid = format('public.%I', target_table)::regclass AND conname = constraint_name) THEN
      EXECUTE format('ALTER TABLE public.%I DROP CONSTRAINT %I', target_table, constraint_name);
    END IF;
    EXECUTE format('ALTER TABLE public.%I ADD CONSTRAINT %I PRIMARY KEY (%I)',
                   target_table, constraint_name, key_column);
    RAISE NOTICE '主キーを追加: %.%（%）', target_table, key_column, constraint_name;
  END LOOP;
END $$;
