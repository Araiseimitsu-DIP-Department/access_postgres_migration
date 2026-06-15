-- =============================================================================
-- PostgreSQL schema v1 — English identifiers
-- -----------------------------------------------------------------------------
-- Applies to DB (e.g. production_progress). Re-run safe: CREATE IF NOT EXISTS.
--
-- Mapping (legacy Access ⇄ this schema):
-- 加工進行表DB.accdb は次の 3 テーブルのみを忠実に再現する。
--
--   t_加工進行表         → progress_entries
--     機番→machine_no, 機番ソート→machine_sort, シリアルNo→serial_number,
--     生産日→production_date, 段取日→setup_date, 客先→customer,
--     品番→part_no, 品名→part_name, 予定数→planned_qty, 納期→due_date,
--     材料→material, 出荷日→shipment_date, 材料Lot→material_lot,
--     日産数→daily_output_qty, 出荷数→shipment_qty,
--     トラブル品対象数→trouble_target_qty, トラブル品出荷数→trouble_shipment_qty,
--     トラブル→trouble_note, 変化点→change_point, 備考→remarks
--
--   t_予約               → reservations
--   t_予約Backup         → reservations_backup
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- progress_entries (was t_加工進行表)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS progress_entries (
    id                      BIGSERIAL PRIMARY KEY,
    machine_no              VARCHAR(4)   NOT NULL,
    machine_sort            VARCHAR(3),
    serial_number           VARCHAR(6),
    production_date         DATE,
    setup_date              DATE,
    customer                VARCHAR(30),
    part_no                 VARCHAR(30),
    part_name               VARCHAR(30),
    planned_qty             INTEGER,
    due_date                DATE,
    material                VARCHAR(40),
    shipment_date           DATE,
    material_lot            VARCHAR(20),
    daily_output_qty        INTEGER,
    shipment_qty            INTEGER,
    trouble_target_qty      INTEGER,
    trouble_shipment_qty    INTEGER,
    trouble_note            VARCHAR(255),
    change_point            VARCHAR(255),
    remarks                 VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_progress_entries_shipment_date
    ON progress_entries (shipment_date);
CREATE INDEX IF NOT EXISTS idx_progress_entries_machine_no
    ON progress_entries (machine_no);
CREATE INDEX IF NOT EXISTS idx_progress_entries_part_no
    ON progress_entries (part_no);

-- ---------------------------------------------------------------------------
-- reservations (was t_予約)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservations (
    id              BIGSERIAL PRIMARY KEY,
    shipment_date DATE        NOT NULL,
    machine_no    VARCHAR(4) NOT NULL,
    material_lot    VARCHAR(20),
    change_point    VARCHAR(255),
    remarks         VARCHAR(255),
    trouble         VARCHAR(255),
    shipment_qty    INTEGER
);

CREATE INDEX IF NOT EXISTS idx_reservations_shipment_date
    ON reservations (shipment_date);
CREATE INDEX IF NOT EXISTS idx_reservations_machine_no
    ON reservations (machine_no);

-- ---------------------------------------------------------------------------
-- reservations_backup (was t_予約Backup)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservations_backup (
    id              BIGSERIAL PRIMARY KEY,
    shipment_date DATE        NOT NULL,
    machine_no    VARCHAR(4) NOT NULL,
    material_lot    VARCHAR(20),
    change_point    VARCHAR(255),
    remarks         VARCHAR(255),
    trouble         VARCHAR(255),
    shipment_qty    INTEGER
);

COMMIT;
