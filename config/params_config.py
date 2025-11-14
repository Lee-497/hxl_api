"""
各模块参数配置
"""

from datetime import datetime
from config.headers_config import COMPANY_ID, OPERATOR_STORE_ID, OPERATOR
from utils.logger import get_logger

logger = get_logger(__name__)


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

# 门店管理模块 - 查询参数
STORE_MANAGEMENT_QUERY_PARAMS = {
    "page_size": 200,
    "page_number": 0,
    "wait_assign": False,
    "leftSelect": {},
    "business_area_ids": [],
    "city_codes": [],
    "not_contain_external_store_flag": True,
    "store_group_ids": [
        6666600000143, 6666600000172, 6868800000002, 6868800000003, 6868800000006, 
        6868800000007, 6868800000008, 6868800000009, 6868800000010, 6868800000011,
        6868800000012, 6868800000013, 6868800000014, 6868800000015, 6868800000016,
        6868800000017, 6868800000018, 6868800000019, 6868800000020, 6868800000021,
        6868800000022, 6868800000023, 6868800000024, 6868800000039
    ],
    "store_label_ids": []
}

# ==================== 商品销售分析模块 - 参数模板 ====================

# 销售分析参数模板 - 根据不同业务需求配置
SALES_ANALYSIS_TEMPLATES = {
    # 冷藏乳饮销售报表 - 基于实际业务需求的参数配置
    "dairy_cold_drinks": {
        "bizday": ["2025-11-13", "2025-11-13"],                    # 业务日期范围
        "company_id": 66666,                                       # 公司ID
        "date_range": "DAY",                                       # 日期范围类型：DAY/WEEK/MONTH
        "item_category_ids": [6666600000591, 6666600001229, 6666600001113, 6666600000859, 6666600001114, 6666600001116],  # 商品分类ID（冷藏乳饮相关分类）
        "operator_store_id": 6666600004441,                        # 操作员门店ID
        "query_count": True,                                       # 是否查询数量
        "query_no_tax": False,                                     # 是否查询不含税金额
        "query_year_compare": False,                               # 是否查询同比
        "sale_mode": "DIRECT",                                     # 销售模式：DIRECT直营
        "store_ids": [6868800000595],                             # 目标门店ID列表
        "summary_types": ["STORE", "CATEGORY_LV1", "CATEGORY_LV2", "CATEGORY_LV3", "ITEM"]  # 汇总维度
    }
}

def get_sales_analysis_params(template_name="dairy_cold_drinks"):
    """
    获取销售分析参数模板
    
    Args:
        template_name: 模板名称，可选值: dairy_cold_drinks
        
    Returns:
        参数字典
    """
    if template_name not in SALES_ANALYSIS_TEMPLATES:
        logger.warning(f"未找到模板 {template_name}，使用默认模板 dairy_cold_drinks")
        template_name = "dairy_cold_drinks"
    
    return SALES_ANALYSIS_TEMPLATES[template_name].copy()
