"""
各模块参数配置
"""

from datetime import datetime
from config.headers_config import COMPANY_ID, OPERATOR_STORE_ID, OPERATOR


def get_current_date():
    """获取当前日期，格式: YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")


def get_current_datetime_iso():
    """获取当前时间，ISO格式: YYYY-MM-DDTHH:MM:SS.fffZ"""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

# 门店商品属性模块 - 导出参数
STORE_PRODUCT_ATTR_EXPORT_PARAMS = {
    "page_size": 200,
    "page_number": 0,
    "category_levels": [1],
    "store_ids": [6868800000674, 6666600013197],
    "product_actual_attribute": True
}

def get_download_params():
    """
    获取下载接口参数（动态生成当前日期时间）
    """
    current_date = get_current_date()
    current_datetime = get_current_datetime_iso()
    
    return {
        "operator_store_id": OPERATOR_STORE_ID,
        "company_id": COMPANY_ID,
        "operator": OPERATOR,
        "page_number": 0,
        "page_size": 200,
        "create_time": [current_date, current_date],  # 动态获取当前日期
        "start_time": current_datetime,               # 动态获取当前时间
        "end_time": current_datetime,                 # 动态获取当前时间
        "time_desc": 0
    }

# 组织商品档案模块 - 导出参数
ORG_PRODUCT_INFO_EXPORT_PARAMS = {
    "operator_store_id": OPERATOR_STORE_ID,
    "company_id": COMPANY_ID,
    "time_type": 0,
    "purchase_scopes": ["不限", "总部购配"],
    "Data_Compact_RangeType_create_date": "day",
    "category_ids": [],
    "checkValue": [{"label": "隐藏商品", "value": "deleted", "itemLable": "不显示", "itemKey": "false"}],
    "deleted": False,
    "item_price_query_select": ["query_purchase_price"],
    "page_number": 0,
    "page_size": 200,
    "supplier_ids": []
}

# 库存查询模块 - 导出参数
INVENTORY_QUERY_EXPORT_PARAMS = {
    "store_ids": [6868800000674, 6666600013197],
    "checkValue": ["show_batch_unit"],
    "unit_type": "PURCHASE",
    "filter_item_types": [],
    "filter_zero_stock": None,
    "goe_lock_quantity": None,
    "item_status_list": None,
    "left_near_expiry_day": None,
    "loe_lock_quantity": None,
    "near_expiry_day": None,
    "query_main_supplier": None,
    "query_mode": 0,
    "right_near_expiry_day": None,
    "sale_summary": None,
    "show_batch_unit": True,
    "storehouse_ids": [],
    "supplier_main_body_ids": None
}
