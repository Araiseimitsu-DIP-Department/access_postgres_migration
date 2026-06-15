"""Access の列名ゆらぎを吸収し、PostgreSQL INSERT 向け tuple を組み立てる。"""

from __future__ import annotations

from typing import Any, Iterable

from migrate_support.coercion import (
    coerce_date_opt,
    coerce_int_opt,
    coerce_str_optional,
    truncate_str,
)


def normalize_access_col(name: str) -> str:
    return str(name).strip()


def row_dict_from_access_cursor(
    description: Iterable[Any],
    row: tuple[Any, ...],
) -> dict[str, Any]:
    """pyodbc cursor.description と 1行から、値を両方キーとして保持する（大小混在への耐性）。"""
    merged: dict[str, Any] = {}
    for desc, cell in zip(description, row, strict=False):
        raw = normalize_access_col(str(desc[0]))
        merged[raw] = cell
        merged.setdefault(raw.lower(), cell)
        merged.setdefault(raw.casefold(), cell)
    return merged


def _get(rd: dict[str, Any], *aliases: str) -> Any:
    """日本語／英数字の列別名どれでも拾う。"""
    for alias in aliases:
        for key, cell in rd.items():
            if not isinstance(key, str):
                continue
            nk = normalize_access_col(key).lower()
            if nk == normalize_access_col(alias).lower():
                return cell
    return None


def progress_tuple_from_access_row(rd: dict[str, Any]) -> tuple[Any, ...]:
    oid = coerce_int_opt(_get(rd, "ID", "id"))
    machine_raw = _get(rd, "機番")
    mn = truncate_str(machine_raw, 4) if machine_raw is not None else None
    if mn is None or mn == "":
        mn = ""
    return (
        oid,
        mn,
        coerce_str_optional(_get(rd, "機番ソート"), 3),
        coerce_str_optional(_get(rd, "シリアルNo", "シリアルNO"), 6),
        coerce_date_opt(_get(rd, "生産日")),
        coerce_date_opt(_get(rd, "段取日")),
        coerce_str_optional(_get(rd, "客先"), 30),
        coerce_str_optional(_get(rd, "品番"), 30),
        coerce_str_optional(_get(rd, "品名"), 30),
        coerce_int_opt(_get(rd, "予定数")),
        coerce_date_opt(_get(rd, "納期")),
        coerce_str_optional(_get(rd, "材料"), 40),
        coerce_date_opt(_get(rd, "出荷日")),
        coerce_str_optional(_get(rd, "材料Lot"), 20),
        coerce_int_opt(_get(rd, "日産数")),
        coerce_int_opt(_get(rd, "出荷数")),
        coerce_int_opt(_get(rd, "トラブル品対象数")),
        coerce_int_opt(_get(rd, "トラブル品出荷数")),
        coerce_str_optional(_get(rd, "トラブル"), 255),
        coerce_str_optional(_get(rd, "変化点"), 255),
        coerce_str_optional(_get(rd, "備考"), 255),
    )


def reservation_tuple_from_access_row(rd: dict[str, Any]) -> tuple[Any, ...] | None:
    sid = coerce_int_opt(_get(rd, "ID", "id"))
    sh = coerce_date_opt(_get(rd, "出荷日"))
    machine_raw = _get(rd, "機番")
    if sh is None or machine_raw is None or str(machine_raw).strip() == "":
        return None
    return (
        sid,
        sh,
        truncate_str(machine_raw, 4) or "",
        coerce_str_optional(_get(rd, "材料Lot"), 20),
        coerce_str_optional(_get(rd, "変化点"), 255),
        coerce_str_optional(_get(rd, "備考"), 255),
        coerce_str_optional(_get(rd, "トラブル"), 255),
        coerce_int_opt(_get(rd, "出荷数")),
    )
