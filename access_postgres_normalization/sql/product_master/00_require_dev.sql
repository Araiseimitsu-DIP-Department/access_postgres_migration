-- 開発DB(192.168.1.120)以外での実行を防ぐ。各SQLから \ir で読み込む。
DO $$
BEGIN
  IF host(inet_server_addr()) <> '192.168.1.120' THEN
    RAISE EXCEPTION '開発DB(192.168.1.120)以外では実行しません: %', host(inet_server_addr());
  END IF;
END $$;
