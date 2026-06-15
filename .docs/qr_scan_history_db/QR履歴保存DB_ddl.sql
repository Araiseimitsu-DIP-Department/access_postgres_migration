-- PostgreSQL DDL 草案（Access メタデータから自動生成）
-- ※ 型・制約は必ず手動で確認・修正してください

CREATE TABLE "t_QR履歴保存" (
    "日付時刻" TIMESTAMP,
    "QRコード" VARCHAR(22),
    "生産ロットID" VARCHAR(7),
    "日付" TIMESTAMP,
    "工程" VARCHAR(2),
    "位置" VARCHAR(2),
    "数量" INTEGER,
    "工程コード" VARCHAR(2),
    "工程名" VARCHAR(30),
    "更新フラグ" VARCHAR(1)
);

