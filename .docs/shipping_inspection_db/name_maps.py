"""出荷検査一覧DB の Access → PostgreSQL 英語名マッピング。"""

SKIP_ACCESS_TABLES: frozenset[str] = frozenset(
    {
        "T_仕掛数",
        "T_外検担",
    }
)

LEGACY_POSTGRES_TABLES: tuple[str, ...] = (
    "wip_quantities",
    "external_inspection_staff",
)

TABLE_NAME_MAP: dict[str, str] = {
    "T_先行検査一覧": "advance_inspection_list",
    "T_出荷データ": "shipping_data",
    "T_出荷検査残": "shipping_inspection_remaining",
    "T_出荷検査残（前日）": "shipping_inspection_remaining_prev_day",
    "T_品番別検査担当者": "product_inspection_staff",
    "T_工程別仕掛数": "process_wip_quantities",
    "T_更新日時": "db_updated_at",
    "T_梱包担": "packaging_staff",
    "T_検査時間": "inspection_duration",
}

TABLE_COLUMN_OVERRIDES: dict[tuple[str, str], str] = {}

COLUMN_NAME_MAP: dict[str, str] = {
    "ID": "id",
    "品番": "product_code",
    "品名": "product_name",
    "客先": "customer",
    "注文ID": "order_id",
    "洗浄": "washing",
    "数値検査": "dimensional_inspection",
    "外観検査": "appearance_inspection",
    "その他": "other",
    "仕掛梱包": "wip_packaging",
    "処理済": "processed",
    "不適合品": "nonconforming_items",
    "完了ロット": "completed_lots",
    "出荷予定日": "scheduled_ship_date",
    "着荷予定日": "scheduled_arrival_date",
    "出荷数": "shipment_quantity",
    "在庫数": "stock_quantity",
    "当日洗浄": "same_day_washing",
    "二次処理": "secondary_process",
    "検査備考": "inspection_remarks",
    "出荷備考": "shipping_remarks",
    "送り先指定": "delivery_destination",
    "保管場所": "storage_location",
    "外検担": "external_inspection_staff_id",
    "納期担": "due_date_person",
    "先行": "advance_flag",
    "検査": "inspection_flag",
    "計量": "weighing_flag",
    "梱包": "packaging_flag",
    "変更点": "change_notes",
    "累計": "cumulative_total",
    "使用ロット": "used_lots",
    "データ": "data_flag",
    "先行洗浄": "advance_washing_flag",
    "洗浄備考": "washing_remarks",
    "梱包担": "packaging_staff_id",
    "確認者": "confirmer_id",
    "確認": "confirmed_flag",
    "検査員名": "inspector_names",
    "区別": "category",
    "表示フラグ": "display_flag",
    "工程1": "process_1",
    "工程2": "process_2",
    "工程3": "process_3",
    "工程4": "process_4",
    "工程5": "process_5",
    "工程6": "process_6",
    "工程7": "process_7",
    "工程8": "process_8",
    "工程9": "process_9",
    "最終洗浄工程番号": "final_washing_process_no",
    "日時": "updated_at",
    "担当者": "staff_name",
    "秒": "seconds",
}

IMPORTANT_COLUMNS: dict[str, list[str]] = {
    "shipping_data": ["order_id", "product_code", "scheduled_ship_date", "shipment_quantity"],
    "shipping_inspection_remaining": ["order_id", "product_code", "scheduled_ship_date"],
    "shipping_inspection_remaining_prev_day": ["order_id", "product_code", "scheduled_ship_date"],
    "advance_inspection_list": ["product_code", "order_id"],
    "packaging_staff": ["id", "staff_name"],
}
