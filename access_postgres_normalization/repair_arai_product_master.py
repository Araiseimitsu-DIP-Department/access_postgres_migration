"""開発DBの arai_masters.product_master にある移行時の形式崩れを修復する。

対象は次の3点のみ。内容の食い違い（単価・品名など）は arai_masters を正として変更しない。
- next_process: VARCHAR(10) で切り捨てられた値を、受注管理・委託加工の完全な値で復元する（列は VARCHAR(255) に拡張）。
- process_code / closing_day: 小数として取り込まれた「42.0」「114.」「5.」を整数表記に戻す。

既定は変更予定の集計のみ。--apply を付けた場合だけ、バックアップを作成してから更新する。
"""

import argparse
import logging
import re
from contextlib import closing
from dataclasses import dataclass

import psycopg2
from psycopg2 import sql

from access_postgres_normalization.dev_db import DevConnectionError, connect_dev, dev_connection_settings

ARAI_DB = "arai_masters"
ORDER_DB = "order_management"
SUBCON_DB = "subcon_manager"
TRUNCATED_NEXT_PROCESS_LENGTH = 10
# material_management_system の management_sheet_master.next_process と同じ上限にそろえる
NEXT_PROCESS_LENGTH = 255
BACKUP_SCHEMA = "normalization_backup"
BACKUP_TABLE = "product_master_before_repair"
ORDER_BACKUP_TABLE = "normalization_backup.product_master_before_fdw"
NUMERIC_TEXT_RE = re.compile(r"^(\d+)\.0*$")

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Repair:
    product_id: str
    column: str
    old: str
    new: str


def normalize_numeric_text(value: str | None) -> str | None:
    """「42.0」「114.」のような小数表記の整数を「42」「114」に戻す。該当しなければ None。"""
    if value is None:
        return None
    match = NUMERIC_TEXT_RE.match(value.strip())
    return match.group(1) if match else None


def restore_next_process(current: str | None, candidates: list[str | None]) -> str | None:
    """切り捨てられた次工程を、先頭が一致する完全な値で復元する。候補が食い違う場合は復元しない。"""
    if current is None or len(current) != TRUNCATED_NEXT_PROCESS_LENGTH:
        return None
    prefix = current.strip()
    if not prefix:
        return None
    restored = {
        value.strip()
        for value in candidates
        if value and value.strip().startswith(prefix) and len(value.strip()) > len(prefix)
    }
    if not restored:
        return None
    # 候補側も列幅で切れている場合があるため、すべてが最長値の先頭部分なら最長値を採用する
    longest = max(restored, key=len)
    if not all(longest.startswith(value) for value in restored):
        return None
    return longest if len(longest) <= NEXT_PROCESS_LENGTH else None


def plan_repairs(
    arai_rows: list[tuple[str, str | None, str | None, str | None, str | None]],
    order_next: dict[str, str | None],
    subcon_next: dict[str, str | None],
) -> list[Repair]:
    """arai の (id, product_no, next_process, process_code, closing_day) から修復内容を作る。"""
    repairs = []
    for product_id, product_no, next_process, process_code, closing_day in arai_rows:
        key = (product_no or "").strip()
        if key:
            restored = restore_next_process(next_process, [order_next.get(key), subcon_next.get(key)])
            if restored is not None:
                repairs.append(Repair(product_id, "next_process", next_process, restored))
        for column, value in (("process_code", process_code), ("closing_day", closing_day)):
            normalized = normalize_numeric_text(value)
            if normalized is not None:
                repairs.append(Repair(product_id, column, value, normalized))
    return repairs


def _fetch(conn, query: str) -> list[tuple]:
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def _next_process_by_product(
    settings: dict[str, str], database: str, product_column: str, preferred_table: str | None = None
) -> dict:
    with closing(connect_dev(settings, database)) as conn:
        table = "public.product_master"
        if preferred_table is not None:
            table = _fetch(conn, f"SELECT coalesce(to_regclass('{preferred_table}'), "
                                 f"'{table}'::regclass)::text")[0][0]
        rows = _fetch(conn, f"SELECT {product_column}, next_process FROM {table}")
    return {(code or "").strip(): value for code, value in rows if code}


def _apply(conn, repairs: list[Repair]) -> None:
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(BACKUP_SCHEMA)))
        # 初回の状態だけを保存する。再実行時は既存のバックアップを上書きしない。
        cursor.execute(
            sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} AS TABLE public.product_master").format(
                sql.Identifier(BACKUP_SCHEMA), sql.Identifier(BACKUP_TABLE)
            )
        )
        cursor.execute(
            "SELECT character_maximum_length FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name='product_master' AND column_name='next_process'"
        )
        if cursor.fetchone()[0] < NEXT_PROCESS_LENGTH:
            cursor.execute(
                sql.SQL("ALTER TABLE public.product_master ALTER COLUMN next_process TYPE varchar({})").format(
                    sql.Literal(NEXT_PROCESS_LENGTH)
                )
            )
        for repair in repairs:
            # 計画時点の値から変わっている行は更新しない（他の更新を上書きしないため）
            cursor.execute(
                sql.SQL("UPDATE public.product_master SET {col} = %s WHERE id = %s AND {col} = %s").format(
                    col=sql.Identifier(repair.column)
                ),
                (repair.new, repair.product_id, repair.old),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(f"{repair.column} の更新対象が変更されています（id={repair.product_id}）")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="バックアップ後に修復を実行する")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        settings = dev_connection_settings()
        # 受注管理は切替後に arai の互換ビューになるため、退避した元の表があればそちらを使う
        order_next = _next_process_by_product(settings, ORDER_DB, "product_no", ORDER_BACKUP_TABLE)
        subcon_next = _next_process_by_product(settings, SUBCON_DB, "product_code")
        with closing(connect_dev(settings, ARAI_DB, readonly=not args.apply)) as conn:
            arai_rows = _fetch(
                conn,
                "SELECT id, product_no, next_process, process_code, closing_day FROM public.product_master",
            )
            repairs = plan_repairs(arai_rows, order_next, subcon_next)
            for column in ("next_process", "process_code", "closing_day"):
                LOGGER.info("%s の修復予定 %s件", column, sum(r.column == column for r in repairs))
            if not args.apply:
                LOGGER.info("変更していません。修復するには --apply を付けて実行してください。")
                return 0
            with conn:
                _apply(conn, repairs)
            LOGGER.info("修復を反映しました（接続先 %s / %s）", settings["host"], ARAI_DB)
    except DevConnectionError as error:
        LOGGER.error("%s", error)
        return 1
    except (psycopg2.Error, RuntimeError) as error:
        LOGGER.error("修復に失敗したため変更を取り消しました: %s", getattr(error, "pgcode", None) or error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
