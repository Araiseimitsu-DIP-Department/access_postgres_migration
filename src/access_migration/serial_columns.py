"""Access COUNTER 列の BIGSERIAL 化・主キー制約・シーケンス同期。"""
from __future__ import annotations

import logging
from typing import Any, Callable, Protocol


class CounterColumn(Protocol):
    access_type: str
    postgres_name: str
    postgres_type: str
    nullable: bool


class CounterTableMapping(Protocol):
    postgres_name: str
    columns: list[CounterColumn]


def counter_postgres_type() -> str:
    return "BIGSERIAL"


def counter_column_note() -> str:
    return "AccessのCOUNTER。BIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期"


def counter_type_mapping_note() -> str:
    return "AccessのID値を投入後、setvalで次採番をMAX(id)+1に同期。PRIMARY KEY付与"


def counter_caution_note() -> str:
    return "COUNTER列はBIGSERIAL化しPRIMARY KEYを付与。移行後にMAX(id)でシーケンスを同期しています。"


def is_counter_column(column: CounterColumn) -> bool:
    return column.access_type == "COUNTER"


def build_column_sql(column: CounterColumn, quote_identifier: Callable[[str], str]) -> str:
    if is_counter_column(column):
        return f"{quote_identifier(column.postgres_name)} BIGSERIAL PRIMARY KEY"
    nullable_sql = "" if column.nullable else " NOT NULL"
    return f"{quote_identifier(column.postgres_name)} {column.postgres_type}{nullable_sql}"


def sync_counter_sequences(
    cursor: Any,
    schema: str,
    mapping: CounterTableMapping,
    quote_identifier: Callable[[str], str],
    qualified_name: Callable[[str, str], str],
    logger: logging.Logger | None = None,
) -> None:
    counter_columns = [column for column in mapping.columns if is_counter_column(column)]
    if not counter_columns:
        return

    table_qualified = qualified_name(schema, mapping.postgres_name)
    table_regclass = f"{schema}.{mapping.postgres_name}"
    for column in counter_columns:
        col_quoted = quote_identifier(column.postgres_name)
        cursor.execute(f"SELECT MAX({col_quoted}) FROM {table_qualified}")
        max_row = cursor.fetchone()
        max_id = max_row[0] if max_row else None

        cursor.execute(
            "SELECT pg_get_serial_sequence(%s, %s)",
            (table_regclass, column.postgres_name),
        )
        sequence_row = cursor.fetchone()
        sequence_name = sequence_row[0] if sequence_row else None
        if not sequence_name:
            if logger is not None:
                logger.warning(
                    "シーケンスが見つかりません（スキップ）: %s.%s",
                    mapping.postgres_name,
                    column.postgres_name,
                )
            continue

        if max_id is None:
            # 0件テーブル: setval(0) は不可のため次採番を 1 にリセット
            cursor.execute("SELECT setval(%s, 1, false)", (sequence_name,))
        else:
            cursor.execute("SELECT setval(%s, %s, true)", (sequence_name, max_id))

        if logger is not None:
            logger.info(
                "シーケンス同期: %s.%s (max=%s)",
                mapping.postgres_name,
                column.postgres_name,
                max_id if max_id is not None else 0,
            )
