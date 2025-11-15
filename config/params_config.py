"""
参数配置文件
集中管理所有模块的请求参数
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import pandas as pd
from config.settings import DOWNLOADS_DIR
from config.headers_config import OPERATOR_STORE_ID, COMPANY_ID, OPERATOR
from utils.logger import get_logger

logger = get_logger(__name__)

def get_current_date():
    """获取当前日期（YYYY-MM-DD格式）"""
    return datetime.now().strftime("%Y-%m-%d")

def get_yesterday_date():
    """获取昨天日期（YYYY-MM-DD格式）"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def get_current_datetime():
    """获取当前日期时间（YYYY-MM-DD HH:MM:SS格式）"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_datetime_iso():
    """获取当前时间，ISO格式: YYYY-MM-DDTHH:MM:SS.fffZ"""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def get_store_ids_from_file() -> List[int]:
    """
    从门店管理数据文件中读取门店ID列表
    
    Returns:
        List[int]: 门店ID列表
    """
    try:
        # 查找最新的门店管理数据文件
        store_files = list(DOWNLOADS_DIR.glob("门店管理_*.xlsx"))
        
        if not store_files:
            logger.warning("未找到门店管理数据文件，使用默认门店ID")
            return [6868800000595]  # 默认门店ID
        
        # 获取最新文件
        latest_file = max(store_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"读取门店管理数据: {latest_file.name}")
        
        # 读取Excel文件
        df = pd.read_excel(latest_file)
        
        # 提取id字段
        if 'id' not in df.columns:
            logger.error("门店管理数据中未找到'id'字段")
            return [6868800000595]
        
        # 获取所有门店ID并去重
        store_ids = df['id'].dropna().astype(int).unique().tolist()
        logger.info(f"成功读取 {len(store_ids)} 个门店ID")
        
        return store_ids
        
    except Exception as e:
        logger.error(f"读取门店ID失败: {str(e)}")
        return [6868800000595]  # 返回默认门店ID

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

# 销售分析参数模板（静态部分） - 根据不同业务需求配置
_SALES_ANALYSIS_TEMPLATES = {
    # 冷藏乳饮销售报表 - 基于实际业务需求的参数配置
    "dairy_cold_drinks": {
        "company_id": 66666,
        "date_range": "DAY",
        "item_category_ids": [
            6666600000591,
            6666600001229,
            6666600001113,
            6666600000859,
            6666600001114,
            6666600001116,
            6666600001117,
            6666600001418,
            6666600001421,
            6666600001422,
            6666600000592,
            6666600000862,
            6666600001230,
            6666600001231,
        ],
        "operator_store_id": 6666600004441,
        "query_count": True,
        "query_no_tax": False,
        "query_year_compare": False,
        "sale_mode": "DIRECT",
        "summary_types": ["STORE", "CATEGORY_LV1", "CATEGORY_LV2", "CATEGORY_LV3", "ITEM"]
    }
}


def get_sales_analysis_params(template_name="dairy_cold_drinks"):
    """
    获取销售分析参数（动态生成日期和门店ID）
    
    Args:
        template_name: 模板名称，可选值: dairy_cold_drinks
        
    Returns:
        参数字典（包含动态日期和门店ID）
    """
    if template_name not in _SALES_ANALYSIS_TEMPLATES:
        logger.warning(f"未找到模板 {template_name}，使用默认模板 dairy_cold_drinks")
        template_name = "dairy_cold_drinks"
    
    # 获取静态模板参数
    params = _SALES_ANALYSIS_TEMPLATES[template_name].copy()
    
    # 动态注入昨天日期
    yesterday = get_yesterday_date()
    params["bizday"] = [yesterday, yesterday]
    logger.info(f"销售分析日期: {yesterday}")
    
    # 动态注入门店ID列表
    store_ids = get_store_ids_from_file()
    params["store_ids"] = store_ids
    logger.info(f"销售分析门店数: {len(store_ids)}")
    
    return params


# ==================== 配送分析模块 - 参数模板 ====================

_DELIVERY_ANALYSIS_TEMPLATES = {
    "order_delivery": {
        "Data_Compact_RangeType_compactDatePicker": "day",
        "time_type": "audit_date",
        "audit_date": ["2025-11-14", "2025-11-14"],
        "company_id": 66666,
        "operator_store_id": 6666600004441,
        "out_store_ids": [6868800000674, 6666600013197],
        "category_level": 1,
        "storehouse_id": None,
        "summary_types": ["CATEGORY", "OUT_STORE", "DATE"],
        "unit_type": "PURCHASE",
    }
}


def get_delivery_analysis_params(template_name: str = "order_delivery") -> dict:
    """获取配送分析参数（动态注入日期等信息）"""
    if template_name not in _DELIVERY_ANALYSIS_TEMPLATES:
        logger.warning(f"未找到配送分析模板 {template_name}，使用默认模板 order_delivery")
        template_name = "order_delivery"

    params = _DELIVERY_ANALYSIS_TEMPLATES[template_name].copy()

    # 动态注入昨天日期
    yesterday = get_yesterday_date()
    params["audit_date"] = [yesterday, yesterday]
    logger.info(f"配送分析日期: {yesterday}")

    return params
