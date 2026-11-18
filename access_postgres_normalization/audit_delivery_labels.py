"""開発環境の現品票履歴を読み取り専用で突合する。"""

import logging
import os
from collections import Counter
from contextlib import closing

import psycopg2
from psycopg2 import sql

DEFAULT_DEV_HOST = "192.168.1.120"
POSTGRES_PORT = 5432
CONNECTION_TIMEOUT_SECONDS = 5
STATEMENT_TIMEOUT = "15s"
LOCK_TIMEOUT = "1s"
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
    connection_options = (
        f"-c default_transaction_read_only=on -c statement_timeout={STATEMENT_TIMEOUT} "
        f"-c lock_timeout={LOCK_TIMEOUT} -c TimeZone=UTC"
    )
    try:
        with closing(
            psycopg2.connect(
                **connection,
                port=POSTGRES_PORT,
                dbname=database,
                connect_timeout=CONNECTION_TIMEOUT_SECONDS,
                options=connection_options,
            )
        ) as conn:
            conn.set_session(readonly=True)
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
    user = os.environ.get("NORMALIZATION_DEV_USER")
    if not user:
        LOGGER.error("NORMALIZATION_DEV_USER を設定してください。")
        return 1

    connection = {
        "host": os.environ.get("NORMALIZATION_DEV_HOST", DEFAULT_DEV_HOST),
        "user": user,
    }
    password = os.environ.get("NORMALIZATION_DEV_PASSWORD")
    if password is not None:
        connection["password"] = password

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
