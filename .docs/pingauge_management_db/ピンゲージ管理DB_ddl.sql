-- PostgreSQL DDL 草案（Access メタデータから自動生成）
-- ※ 型・制約は必ず手動で確認・修正してください

CREATE TABLE "t_PGマスタ" (
    "サイズ" VARCHAR(20),
    "保有数" INTEGER,
    "ケースNo" VARCHAR(5)
);


CREATE TABLE "t_担当者マスタ" (
    "担当者ID" VARCHAR(2),
    "担当者名" VARCHAR(5),
    "部署" VARCHAR(2),
    "かな" VARCHAR(1),
    "表示" VARCHAR(1)
);


CREATE TABLE "t_貸出" (
    "ID" BIGSERIAL,
    "サイズ" VARCHAR(20),
    "担当者ID" VARCHAR(2),
    "機番" VARCHAR(4),
    "貸出日" TIMESTAMP,
    "返却日" TIMESTAMP,
    "完了フラグ" VARCHAR(1)
);

