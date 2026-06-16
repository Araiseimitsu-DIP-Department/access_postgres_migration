-- PostgreSQL DDL 草案（Access メタデータから自動生成）
-- ※ 型・制約は必ず手動で確認・修正してください

CREATE TABLE "t_クロス集計用" (
    "ID" BIGSERIAL,
    "費目コード" VARCHAR(2),
    "費目名" VARCHAR(30),
    "購入先コード" VARCHAR(3),
    "購入先名" VARCHAR(30),
    "購入月" VARCHAR(4),
    "金額" NUMERIC(19,4)
);


CREATE TABLE "t_コントロール" (
    "ID" BIGSERIAL,
    "購入月From" VARCHAR(4),
    "購入月To" VARCHAR(4),
    "集計方法" INTEGER
);


CREATE TABLE "t_科目名マスタ" (
    "科目コード" VARCHAR(2),
    "科目名" VARCHAR(6)
);


CREATE TABLE "t_購入先マスタ" (
    "購入先コード" VARCHAR(3),
    "購入先名" VARCHAR(20),
    "費目コード" VARCHAR(2),
    "費目名" VARCHAR(10),
    "締日" VARCHAR(2),
    "かな" VARCHAR(1),
    "表示フラグ" VARCHAR(1)
);


CREATE TABLE "t_購入品明細" (
    "ID" BIGSERIAL,
    "納入日" TIMESTAMP,
    "購入先コード" VARCHAR(3),
    "購入先名" VARCHAR(30),
    "購入者コード" VARCHAR(3),
    "購入者名" VARCHAR(30),
    "費目コード" VARCHAR(2),
    "費目名" VARCHAR(10),
    "購入月" VARCHAR(4),
    "納品書番号" VARCHAR(15),
    "品名" VARCHAR(60),
    "数量" INTEGER,
    "単価" DOUBLE PRECISION,
    "金額" NUMERIC(19,4),
    "単位" VARCHAR(5),
    "備考" VARCHAR(30),
    "入力日" TIMESTAMP,
    "科目名" VARCHAR(6)
);


CREATE TABLE "t_購入者マスタ" (
    "購入者コード" VARCHAR(3),
    "購入者名" VARCHAR(10),
    "かな" VARCHAR(1),
    "表示フラグ" VARCHAR(1)
);

