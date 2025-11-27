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

def get_month_date_range():
    """
    获取当前月份1号到昨天的日期范围
    
    Returns:
        List[str]: [月份1号, 昨天], 格式: YYYY-MM-DD
    """
    now = datetime.now()
    # 当前月份1号
    first_day = now.replace(day=1).strftime("%Y-%m-%d")
    # 昨天
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    return [first_day, yesterday]

def get_current_datetime():
    """获取当前日期时间（YYYY-MM-DD HH:MM:SS格式）"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_datetime_iso():
    """获取当前时间，ISO格式: YYYY-MM-DDTHH:MM:SS.fffZ"""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def get_store_ids_from_file() -> List[int]:
    """
    从门店管理数据文件中读取门店ID列表（只读取status=TRUE的门店）
    
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
        
        # 过滤status字段
        if 'status' in df.columns:
            # 过滤掉status为FALSE的门店
            original_count = len(df)
            df = df[df['status'] == True]
            filtered_count = original_count - len(df)
            if filtered_count > 0:
                logger.info(f"已过滤掉 {filtered_count} 个status=FALSE的门店")
        else:
            logger.warning("门店管理数据中未找到'status'字段，将使用全部门店")
        
        # 获取所有门店ID并去重
        store_ids = df['id'].dropna().astype(int).unique().tolist()
        logger.info(f"成功读取 {len(store_ids)} 个门店ID（status=TRUE）")
        
        return store_ids
        
    except Exception as e:
        logger.error(f"读取门店ID失败: {str(e)}")
        return [6868800000595]  # 返回默认门店ID


def get_item_and_store_ids_from_planning() -> tuple[List[int], List[int]]:
    """
    从调改店模版的“规划清单”Sheet中读取商品代码和门店代码，
    并关联到对应的item_id和store_id
    
    流程:
    1. 读取 reference/调改店模版.xlsx["规划清单"]
    2. 商品代码 → 关联 组织档案映射清单.code → 获取 item_id
    3. 门店代码 → 关联 门店管理.store_number → 获取 id
    
    Returns:
        tuple: (item_ids, store_ids)
    """
    from config.settings import REFERENCE_DIR
    
    try:
        # 1. 读取调改店模版 - 规划清单
        planning_file = REFERENCE_DIR / "调改店模版.xlsx"
        if not planning_file.exists():
            logger.error(f"未找到调改店模版文件: {planning_file}")
            return [], []
        
        logger.info(f"读取调改店模版: {planning_file.name}")
        planning_df = pd.read_excel(planning_file, sheet_name="规划清单")
        
        if '商品代码' not in planning_df.columns or '门店代码' not in planning_df.columns:
            logger.error("规划清单中缺少必要字段")
            return [], []
        
        # 提取商品代码和门店代码（去重，先转整数去除.0，再转字符串）
        # 🔧 关键修复：Excel读取数字列会变成浮点数（如 44020181.0），需要先转整数再转字符串
        item_codes = planning_df['商品代码'].dropna().astype(int).astype(str).str.strip().unique().tolist()
        store_numbers = planning_df['门店代码'].dropna().astype(int).astype(str).str.strip().unique().tolist()
        
        logger.info(f"规划清单: {len(item_codes)} 个商品代码, {len(store_numbers)} 个门店代码")
        
        # 2. 关联组织档案映射清单 - 获取item_id
        mapping_files = list(DOWNLOADS_DIR.glob("组织档案映射清单_*.xlsx"))
        if not mapping_files:
            logger.error("未找到组织档案映射清单文件，请先执行 org_item_mapping 模块")
            return [], []
        
        latest_mapping = max(mapping_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"读取组织档案映射: {latest_mapping.name}")
        mapping_df = pd.read_excel(latest_mapping)
        
        # 🔧 关键优化：将code转为字符串后去空格，确保与规划清单匹配
        # （组织档案映射清单中的code已存储为整数，读取时会自动转为数字，需转为字符串匹配）
        mapping_df['code'] = mapping_df['code'].astype(str).str.strip()
        item_mapping = dict(zip(mapping_df['code'], mapping_df['item_id']))
        
        # 匹配item_id
        item_ids = []
        for code in item_codes:
            if code in item_mapping:
                item_ids.append(int(item_mapping[code]))
            else:
                logger.warning(f"商品代码 {code} 未在映射表中找到")
        
        logger.info(f"匹配到 {len(item_ids)}/{len(item_codes)} 个商品ID")
        
        # 3. 关联门店管理 - 获取store_id
        store_files = list(DOWNLOADS_DIR.glob("门店管理_*.xlsx"))
        if not store_files:
            logger.error("未找到门店管理文件，请先执行 store_management 模块")
            return item_ids, []
        
        latest_store = max(store_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"读取门店管理数据: {latest_store.name}")
        store_df = pd.read_excel(latest_store)
        
        # 🔧 关键修复：将store_number转为字符串类型并去除空格，确保匹配成功
        if 'store_number' not in store_df.columns:
            logger.error("门店管理数据中未找到 store_number 字段")
            return item_ids, []
        
        store_df['store_number'] = store_df['store_number'].astype(str).str.strip()
        store_mapping = dict(zip(store_df['store_number'], store_df['id']))
        
        # 匹配store_id
        store_ids = []
        for number in store_numbers:
            if number in store_mapping:
                store_ids.append(int(store_mapping[number]))
            else:
                logger.warning(f"门店代码 {number} 未在门店管理表中找到")
        
        logger.info(f"匹配到 {len(store_ids)}/{len(store_numbers)} 个门店ID")
        
        return item_ids, store_ids
        
    except Exception as e:
        logger.error(f"读取规划清单失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return [], []

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

# 库存统计模块 - 仓库配置列表
INVENTORY_STATISTICS_WAREHOUSES = [
    {
        "name": "广东从化仓",
        "store_id": 6868800000674,
        "storehouse_id": 6868800000776,
    },
    {
        "name": "广东东莞二仓",
        "store_id": 6666600013197,
        "storehouse_id": 6666600012498,
    },
]

# 库存统计模块 - 基础导出参数（不包含门店和仓库ID）
INVENTORY_STATISTICS_BASE_PARAMS = {
    "company_id": 66666,
    "operator_store_id": 6666600004441,
    "page_number": 0,
    "page_size": 200,
    "query_unit": "PURCHASE",
    "unit_type": "PURCHASE"
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
        "summary_types": ["STORE", "CATEGORY_LV1", "CATEGORY_LV2", "CATEGORY_LV3", "ITEM"],
        "columns": [
            {
                "name": "基本信息",
                "code": "basic_info",
                "children": [
                    {"name": "门店名称", "code": "store_name", "align": "left", "width": 160},
                    {"name": "门店代码", "code": "store_code", "align": "left", "width": 100}
                ]
            },
            {
                "name": "商品分类",
                "code": "item_category",
                "children": [
                    {"name": "一级商品类别", "code": "one_item_category_name", "width": 160},
                    {"name": "二级商品类别", "code": "two_item_category_name", "width": 160},
                    {"name": "三级商品类别", "code": "three_item_category_name", "width": 160}
                ]
            },
            {
                "name": "商品信息",
                "code": "item_info",
                "children": [
                    {"name": "商品代码", "code": "item_code", "width": 96},
                    {"name": "商品条码", "code": "item_bar_code", "width": 124},
                    {"name": "商品名称", "code": "item_name", "width": 260}
                ]
            },
            {
                "name": "数量合计",
                "code": "basic_quantity",
                "width": 120,
                "align": "center"
            },
            {
                "name": "金额合计",
                "code": "money",
                "width": 120,
                "align": "center"
            }
        ]
        # bizday, store_ids 将在 get_sales_analysis_params() 中动态注入
    },
    
    # 🆕 调改店报表 - 三级分类PSD数据源
    "store_adjustment_category_lv3": {
        "company_id": 66666,
        "date_range": "DAY",
        "operator_store_id": 6666600004441,
        "query_count": True,
        "query_no_tax": False,
        "query_year_compare": False,
        "summary_types": ["CATEGORY_LV1", "CATEGORY_LV2", "CATEGORY_LV3"],
        "item_category_ids": [
            6666600001269, 6666600001270, 6666600001271, 6666600001272, 6666600001273,
            6666600001427, 6666600001428, 6666600001042, 6666600001152, 6666600001153,
            6666600001343, 6666600001394, 6666600001395, 6666600001396, 6666600001255,
            6666600001149, 6666600001342, 6666600001323, 6666600001324, 6666600001325,
            6666600001397, 6666600001326, 6666600001327, 6666600001328, 6666600001337,
            6666600001398, 6666600001330, 6666600001331, 6666600001332, 6666600001333,
            6666600001399, 6666600001400, 6666600001401, 6666600001402, 6666600001334,
            6666600001335, 6666600001336, 6666600001403, 6666600001404, 6666600001299,
            6666600001300, 6666600001303, 6666600001304, 6666600001305, 6666600001306,
            6666600001307, 6666600001250, 6666600001315, 6666600001316, 6666600001317,
            6666600001340, 6666600001341, 6666600001376, 6666600001392, 6666600001393,
            6666600001301, 6666600001308, 6666600001309, 6666600001302, 6666600001310,
            6666600001311, 6666600001312, 6666600001313, 6666600001314
        ]
        # bizday 和 store_ids 将在 get_sales_analysis_params() 中动态注入
    },
    
    # 🆕 调改店报表 - 规划SKU数据源（基于规划清单）
    "store_adjustment_planning_sku": {
        "company_id": 66666,
        "date_range": "DAY",
        "operator_store_id": 6666600004441,
        "query_count": True,
        "query_no_tax": False,
        "query_year_compare": False,
        "sale_mode": "DIRECT",
        "summary_types": ["STORE", "ITEM"]
        # bizday, item_ids, store_ids 将在 get_sales_analysis_params() 中动态注入
    },
    
    # 🆕 调改店报表 - 全店SKU数据源（基于全部门店）
    "store_adjustment_all_sku": {
        "company_id": 66666,
        "date_range": "DAY",
        "operator_store_id": 6666600004441,
        "query_count": True,
        "query_no_tax": False,
        "query_year_compare": False,
        "sale_mode": "DIRECT",
        "summary_types": ["ITEM"]  # 注意：全店SKU的汇总条件与规划SKU不同
        # bizday, item_ids, store_ids 将在 get_sales_analysis_params() 中动态注入
    },
    
    # 🆕 调改店报表 - 粮油非食数据源
    "store_adjustment_grain_oil_nonfood": {
        "company_id": 66666,
        "date_range": "DAY",
        "operator_store_id": 6666600004441,
        "query_count": True,
        "query_no_tax": False,
        "query_year_compare": False,
        "sale_mode": "DIRECT",
        "summary_types": ["STORE"],
        "item_category_ids": [
            6666600001042, 6666600001152, 6666600001153, 6666600001343, 6666600001394, 6666600001395,
            6666600001255, 6666600001149, 6666600001342, 6666600001323, 6666600001324, 6666600001325,
            6666600001397, 6666600001326, 6666600001327, 6666600001328, 6666600001337,
            6666600001398, 6666600001330, 6666600001331, 6666600001332, 6666600001333,
            6666600001399, 6666600001400, 6666600001401, 6666600001402, 6666600001334,
            6666600001335, 6666600001336, 6666600001403, 6666600001404, 6666600001299,
            6666600001300, 6666600001303, 6666600001304, 6666600001305, 6666600001306,
            6666600001307, 6666600001250, 6666600001315, 6666600001316, 6666600001317,
            6666600001340, 6666600001341, 6666600001376, 6666600001392, 6666600001393,
            6666600001301, 6666600001308, 6666600001309, 6666600001302, 6666600001310,
            6666600001311, 6666600001312, 6666600001313, 6666600001314
        ]
        # bizday, store_ids 将在 get_sales_analysis_params() 中动态注入
    },
    
    # 🆕 调改店报表 - 冷冻数据源
    "store_adjustment_frozen": {
        "company_id": 66666,
        "date_range": "DAY",
        "operator_store_id": 6666600004441,
        "query_count": True,
        "query_no_tax": False,
        "query_year_compare": False,
        "sale_mode": "DIRECT",
        "summary_types": ["STORE"],
        "item_category_ids": [
        6666600001269,
        6666600001270,
        6666600001271,
        6666600001272,
        6666600001273,
        6666600001427,
        6666600001428,
        ]
        # bizday, store_ids 将在 get_sales_analysis_params() 中动态注入
    }
}


def get_sales_analysis_params(template_name="dairy_cold_drinks", bizday=None, store_adjustment_planning_sku_bizday=None, store_adjustment_other_bizday=None):
    """
    获取销售分析参数（动态生成日期和门店ID）
    
    Args:
        template_name: 模板名称，可选值: 
            - dairy_cold_drinks: 冷藏乳饮（昨天日期）
            - store_adjustment_category_lv3: 调改店-三级分类PSD（当月日期范围）
            - store_adjustment_planning_sku: 调改店-规划SKU（10月1号-昨天）
            - store_adjustment_all_sku: 调改店-全店SKU（10月1号-昨天，全部门店）
            - store_adjustment_grain_oil_nonfood: 调改店-粮油非食（10月1号-昨天）
            - store_adjustment_frozen: 调改店-冷冻（10月1号-昨天）
        bizday: 自定义日期范围，格式: ["YYYY-MM-DD", "YYYY-MM-DD"]
                如果提供，将覆盖模板默认的日期范围
        store_adjustment_planning_sku_bizday: 门店规划SKU自定义日期范围
        store_adjustment_other_bizday: 三级分类、全店SKU、粮油非食和冷冻自定义日期范围
        
    Returns:
        参数字典（包含动态日期和门店ID）
    """
    if template_name not in _SALES_ANALYSIS_TEMPLATES:
        logger.warning(f"未找到模板 {template_name}，使用默认模板 dairy_cold_drinks")
        template_name = "dairy_cold_drinks"
    
    # 获取静态模板参数
    params = _SALES_ANALYSIS_TEMPLATES[template_name].copy()
    
    # 动态注入日期（根据模板类型或自定义）
    if bizday:
        # 使用自定义日期
        params["bizday"] = bizday
        logger.info(f"使用自定义日期: {bizday[0]} → {bizday[1]}")
    elif store_adjustment_planning_sku_bizday and template_name == "store_adjustment_planning_sku":
        # 使用门店规划SKU自定义日期
        params["bizday"] = store_adjustment_planning_sku_bizday
        logger.info(f"使用门店规划SKU自定义日期: {store_adjustment_planning_sku_bizday[0]} → {store_adjustment_planning_sku_bizday[1]}")
    elif store_adjustment_other_bizday and template_name in ["store_adjustment_category_lv3", "store_adjustment_all_sku", "store_adjustment_grain_oil_nonfood", "store_adjustment_frozen"]:
        # 使用三级分类、全店SKU、粮油非食和冷冻自定义日期
        params["bizday"] = store_adjustment_other_bizday
        logger.info(f"使用三级分类、全店SKU、粮油非食和冷冻自定义日期: {store_adjustment_other_bizday[0]} → {store_adjustment_other_bizday[1]}")
    elif template_name == "store_adjustment_category_lv3":
        # 调改店-三级分类PSD：当月日期范围（月份1号 → 昨天）
        date_range = get_month_date_range()
        params["bizday"] = date_range
        logger.info(f"销售分析日期范围: {date_range[0]} → {date_range[1]}")
    elif template_name in ["store_adjustment_planning_sku", "store_adjustment_all_sku", "store_adjustment_grain_oil_nonfood", "store_adjustment_frozen"]:
        # 调改店-SKU相关：10月1号 → 昨天
        yesterday = get_yesterday_date()
        params["bizday"] = ["2025-10-01", yesterday]
        logger.info(f"销售分析日期范围: 2025-10-01 → {yesterday}")
    else:
        # 默认：昨天日期
        yesterday = get_yesterday_date()
        params["bizday"] = [yesterday, yesterday]
        logger.info(f"销售分析日期: {yesterday}")
    
    # 动态注入门店ID和商品ID（根据模板类型）
    if template_name == "store_adjustment_planning_sku":
        # 从规划清单获取item_ids和store_ids
        item_ids, store_ids = get_item_and_store_ids_from_planning()
        if item_ids:
            params["item_ids"] = item_ids
            logger.info(f"销售分析商品数: {len(item_ids)}")
        else:
            logger.warning("未获取到商品ID，请检查规划清单")
        
        if store_ids:
            params["store_ids"] = store_ids
            logger.info(f"销售分析门店数: {len(store_ids)}")
        else:
            logger.warning("未获取到门店ID，请检查规划清单")
    elif template_name == "store_adjustment_all_sku":
        # 获取全部门店ID
        store_ids = get_store_ids_from_file()
        params["store_ids"] = store_ids
        logger.info(f"销售分析门店数: {len(store_ids)}")
        
        # 从规划清单获取item_ids（商品ID）
        item_ids, _ = get_item_and_store_ids_from_planning()
        if item_ids:
            params["item_ids"] = item_ids
            logger.info(f"销售分析商品数: {len(item_ids)}")
        else:
            logger.warning("未获取到商品ID，请检查规划清单")
    else:
        # 其他模板：从门店管理文件获取store_ids（包括冷藏乳饮等）
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


# ==================== 组织档案映射清单模块 - 请求参数 ====================

ORG_ITEM_MAPPING_QUERY_PARAMS = {
    "page_size": 1000,
    "page_number": 0,
    "time_type": 0,
    "purchase_scopes": ["不限", "总部购配"],
    "Data_Compact_RangeType_create_date": "day",
    "checkValue": [
        {
            "label": "隐藏商品",
            "value": "deleted",
            "itemLable": "不显示",
            "itemKey": "false"
        }
    ],
    "deleted": False,
    "item_price_query_select": ["query_purchase_price"],
    "orders": [{"property": "code", "direction": "ASC"}],  # 🔧 关键修复：添加稳定排序，避免分页重复
    "update_date": None
}
