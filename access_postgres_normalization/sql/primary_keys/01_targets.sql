-- 主キーを追加する表と列（01_primary_keys_up.sql・01_primary_keys_down.sql の共通定義）。
-- 選定基準（2026-11-20 調査）:
--   ・既存の列で空欄・重複がなく、アプリがその列で更新・削除している（または参照のみ）表に、その列で主キーを付ける。
--   ・付けない表: Excel履歴の写し・QR履歴の一時表/バックアップ（どのアプリも使わない。退避候補）、
--     空の作業表とアプリが毎回作り直す集計表（advance_inspection_list・product_inspection_staff・db_updated_at）、
--     書き込み元のアプリが作業領域にない表（appearance_inspection_db.inspection_in_progress）、
--     集計元SQLが作業領域にない表（shipping_inspection_db.process_wip_quantities）、
--     キーが空欄の行がある表（appearance_inspection_db.inspector_master。扱いを相談中）。
--   ・orders は jucyu_manager が重複エラーを制約名 uq_orders_order_id で見分けるため、その名前の主キーにする。
\set pk_appearance_inspection_db 'check_sheet_list:no,numeric_inspector_master:inspector_id,process_master:process_no'
\set pk_delivery_label_db 'lot_completion_reasons:reason_code,process_master:process_code'
\set pk_material_millsheet_manager 'inspectors:code,material_types:material_type,remarks_master:code,suppliers:supplier_code'
\set pk_material_scheduling 'inbound_email_master:supplier_code,legacy_machine_ids:machine_id,management_sheet_master:product_code,material_types:material_type,orderer_master:id,sales_rep_master:id,setup_operator_master:id'
\set pk_order_management 'customer_master:code,kanban_master:product_no,orders:order_id:uq_orders_order_id,sales_rep_master:code'
\set pk_order_performance_db 'sales_months:sales_month'
\set pk_pingauge_management_db 'pin_gauge_master:size,staff_master:staff_id'
\set pk_secondary_process_record_db 'basket_master:code,next_process_master:code,pin_master:code,polishing_stone_master:code,pressure_master:code,rotation_direction_master:code,work_master:work_code,worker_master:code'
\set pk_shipping_inspection_db 'inspection_duration:product_code,packaging_staff:id,shipping_data:order_id,shipping_inspection_remaining:order_id,shipping_inspection_remaining_prev_day:order_id'
