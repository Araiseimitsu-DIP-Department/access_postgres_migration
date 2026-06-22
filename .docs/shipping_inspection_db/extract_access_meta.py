"""Access DB メタデータ抽出（shipping_inspection_db）。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pyodbc

DB_PATH = r"C:\Users\seika\Desktop\出荷検査一覧DB.accdb"
OUT_PATH = Path(__file__).resolve().parent / "出荷検査一覧DB_meta.json"


def main() -> None:
    conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};" f"DBQ={DB_PATH};ReadOnly=1;"
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()

    objects: dict[tuple[str, str], dict] = {}
    for row in cursor.tables():
        name = row.table_name
        table_type = row.table_type
        if name.startswith("MSys"):
            continue
        if table_type not in {"TABLE", "VIEW", "SYNONYM"}:
            continue
        key = (name, table_type)
        if key not in objects:
            objects[key] = {"name": name, "table_type": table_type}

    tables = []
    for (_, _), table in sorted(objects.items(), key=lambda item: (item[1]["table_type"], item[1]["name"])):
        name = table["name"]
        table_type = table["table_type"]

        columns = []
        columns_error = None
        try:
            for col in cursor.columns(table=name):
                columns.append(
                    {
                        "name": col.column_name,
                        "access_type": col.type_name,
                        "sql_data_type": col.data_type,
                        "column_size": col.column_size,
                        "decimal_digits": col.decimal_digits,
                        "nullable": col.nullable == 1,
                    }
                )
        except Exception as error:
            columns_error = str(error)

        primary_key: list[str] = []
        try:
            for idx in cursor.statistics(table=name):
                if idx.ORDINAL_POSITION == 1 and idx.NON_UNIQUE == 0:
                    primary_key.append(idx.COLUMN_NAME)
        except Exception:
            pass

        row_count = None
        row_count_error = None
        if table_type in {"TABLE", "SYNONYM", "VIEW"}:
            try:
                count_cursor = conn.cursor()
                count_cursor.execute(f"SELECT COUNT(*) FROM [{name}]")
                row_count = int(count_cursor.fetchone()[0])
            except Exception as error:
                row_count_error = str(error)

        notes = []
        if table_type == "SYNONYM":
            notes.append("Accessリンクテーブル（外部DB参照）")
        if table_type == "VIEW":
            notes.append("Accessクエリ/ビュー")
        if columns_error:
            notes.append(f"カラム取得エラー: {columns_error}")

        tables.append(
            {
                "name": name,
                "table_type": table_type,
                "row_count": row_count,
                "row_count_error": row_count_error,
                "primary_key": primary_key,
                "columns": columns,
                "indexes": [],
                "note": " / ".join(notes),
            }
        )

    meta = {
        "database_path": DB_PATH,
        "driver_used": "Microsoft Access Driver (*.mdb, *.accdb)",
        "extracted_at": datetime.now().isoformat(),
        "tables": tables,
    }
    OUT_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Objects: {len(tables)}")
    for table in tables:
        print(f"  [{table['table_type']}] {table['name']}: {table['row_count']} rows, {len(table['columns'])} cols")
    conn.close()


if __name__ == "__main__":
    main()
