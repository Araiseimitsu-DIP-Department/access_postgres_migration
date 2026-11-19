"""開発環境の現品票履歴を読み取り専用で突合する。"""

import logging
from collections import Counter
from contextlib import closing

import psycopg2
from psycopg2 import sql

from access_postgres_normalization.dev_db import DevConnectionError, connect_dev, dev_connection_settings

HISTORY_COLUMNS = (
    "production_lot_id",
    "machine_no",
    "product_code",
    "product_name",
    "customer",
    "material",
    "material_lot_no",
    "quantity",
    "remarks",
    "instruction_date",
    "completion_flag",
)

HistoryCounts = Counter[tuple]
LOGGER = logging.getLogger(__name__)


def fetch_counts(connection: dict[str, str], database: str, table: str) -> HistoryCounts:
    query = sql.SQL("SELECT {} FROM public.{}").format(
        sql.SQL(", ").join(map(sql.Identifier, HISTORY_COLUMNS)),
        sql.Identifier(table),
    )
    try:
        with closing(connect_dev(connection, database)) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return Counter(cursor)
    except psycopg2.Error as error:
        LOGGER.error(
            "%s.public.%s の読み取りに失敗しました（%s）",
            database,
            table,
            error.pgcode or type(error).__name__,
        )
        raise


def summarize(inspection: HistoryCounts, labels: HistoryCounts) -> dict[str, int]:
    inspection_rows = inspection.total()
    label_rows = labels.total()
    matching_rows = (inspection & labels).total()
    return {
        "外観検査側": inspection_rows,
        "現品票側": label_rows,
        "全11列一致": matching_rows,
        "外観検査側のみ": inspection_rows - matching_rows,
        "現品票側のみ": label_rows - matching_rows,
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        connection = dev_connection_settings()
    except DevConnectionError as error:
        LOGGER.error("%s", error)
        return 1

    try:
        inspection = fetch_counts(
            connection, "appearance_inspection_db", "excel_product_slip_history"
        )
        labels = fetch_counts(connection, "delivery_label_db", "excel_delivery_label_history")
    except psycopg2.Error:
        return 1

    for label, count in summarize(inspection, labels).items():
        LOGGER.info("%s %s件", label, f"{count:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
