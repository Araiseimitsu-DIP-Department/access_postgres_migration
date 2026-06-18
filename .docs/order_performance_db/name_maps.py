"""受注実績データ集計DB の Access → PostgreSQL 英語名マッピング。"""

TABLE_NAME_MAP: dict[str, str] = {
    "t_コントロール": "app_control",
    "t_受注キャンセル": "order_cancellations",
    "t_受注実績": "order_performance",
    "t_売月": "sales_months",
}

COLUMN_NAME_MAP: dict[str, str] = {
    "ID": "id",
    "コード": "code",
    "客先": "customer",
    "売月": "sales_month",
    "営業担当": "sales_rep",
    "受注日": "order_date",
    "最終日": "last_date",
    "書込みフォルダ": "output_folder",
    "当月From": "current_month_from",
    "当月To": "current_month_to",
    "注文ID": "order_id",
    "注文数": "order_qty",
    "注文番号": "order_no",
    "単価": "unit_price",
    "品名": "product_name",
    "品番": "product_no",
    "納期": "due_date",
    "累積客別From": "cumulative_by_customer_from",
    "累積客別To": "cumulative_by_customer_to",
    "累積月別From": "cumulative_by_month_from",
    "累積月別To": "cumulative_by_month_to",
    "締日": "closing_day",
    "金額": "amount",
}
