"""
商品销售分析模块
用于查询和采集商品销售分析数据，支持多种参数模板
"""

import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from core.base_module import ExportBasedModule
from utils.logger import get_logger
from config.api_config import EXPORT_ENDPOINTS
from config.params_config import get_sales_analysis_params

logger = get_logger(__name__)


TEMPLATE_FILE_LABELS = {
    "dairy_cold_drinks": "冷藏乳饮",
    "store_adjustment_category_lv3": "调改店-三级分类PSD",
    "store_adjustment_planning_sku": "调改店-规划SKU",
    "store_adjustment_all_sku": "调改店-全店SKU",
    "store_adjustment_grain_oil_nonfood": "调改店-粮油非食",
    "store_adjustment_frozen": "调改店-冷冻",
}


class SalesAnalysisModule(ExportBasedModule):
    """商品销售分析数据采集模块（支持灵活参数配置）"""
    
    def __init__(self):
        super().__init__()
        self.export_url = EXPORT_ENDPOINTS["sales_analysis"]
        self.module_display_name = "商品销售分析"
        
    
    def get_export_config(self, **kwargs) -> Dict[str, Any]:
        """
        获取导出配置（支持灵活参数配置）
        
        参数优先级：
        1. custom_params（完全自定义参数，最高优先级）
        2. 模板参数 + 覆盖参数
        3. 默认模板参数
        
        Args:
            template_name: 参数模板名称（默认: dairy_cold_drinks）
            custom_params: 自定义参数，会覆盖模板参数
            bizday: 自定义日期范围 ["YYYY-MM-DD", "YYYY-MM-DD"]
            store_adjustment_planning_sku_bizday: 门店规划SKU自定义日期范围
            store_adjustment_other_bizday: 三级分类和全店SKU自定义日期范围
            **kwargs: 其他参数（如 store_ids 等）会覆盖模板对应字段
            
        Returns:
            Dict: 导出配置
        """
        # 1. 获取模板名称
        template_name = kwargs.pop('template_name', 'dairy_cold_drinks')
        custom_params = kwargs.pop('custom_params', None)
        bizday = kwargs.pop('bizday', None)  # 提取 bizday 参数
        store_adjustment_planning_sku_bizday = kwargs.pop('store_adjustment_planning_sku_bizday', None)
        store_adjustment_other_bizday = kwargs.pop('store_adjustment_other_bizday', None)
        
        # 2. 如果提供了 custom_params，直接使用（完全自定义）
        if custom_params:
            logger.info("使用完全自定义参数")
            export_params = custom_params
        else:
            # 3. 从模板获取基础参数（传递日期参数）
            logger.info(f"使用参数模板: {template_name}")
            export_params = get_sales_analysis_params(
                template_name, 
                bizday=bizday,
                store_adjustment_planning_sku_bizday=store_adjustment_planning_sku_bizday,
                store_adjustment_other_bizday=store_adjustment_other_bizday
            )
            
            # 4. 用 kwargs 中的参数覆盖模板参数
            if kwargs:
                logger.info(f"参数覆盖: {list(kwargs.keys())}")
                export_params.update(kwargs)
        
        # 5. 生成文件名前缀，便于加工阶段识别
        file_label = TEMPLATE_FILE_LABELS.get(template_name)
        if not file_label and custom_params:
            file_label = custom_params.get("file_label")
        if not file_label and kwargs.get("file_label"):
            file_label = kwargs["file_label"]
        file_name_prefix = "商品销售数据"
        if file_label:
            file_name_prefix = f"{file_name_prefix}_{file_label}"

        logger.info(f"最终导出参数: {list(export_params.keys())}")
        logger.info(f"文件名前缀: {file_name_prefix}")

        return {
            'export_url': self.export_url,
            'export_params': export_params,
            'module_name': self.module_display_name,
            'file_name_prefix': file_name_prefix,
        }


def run(template_name: str = "dairy_cold_drinks") -> Optional[Path]:
    """
    模块入口函数（供main.py调用）- 已弃用，建议直接使用类方法
    
    Args:
        template_name: 参数模板名称
        
    Returns:
        下载的文件路径，失败返回None
    """
    logger.info(f"启动销售分析模块，模板: {template_name}")
    
    try:
        module = SalesAnalysisModule()
        result = module.execute(template_name=template_name)
        
        if result:
            logger.info(f"销售分析模块执行成功: {result}")
        else:
            logger.error("销售分析模块执行失败")
        
        return result
        
    except Exception as e:
        logger.error(f"销售分析模块执行异常: {str(e)}")
        return None


def get_description() -> str:
    """获取模块描述"""
    return "商品销售分析数据采集模块，支持日/周/月销售数据分析"


# 模块信息
MODULE_NAME = "sales_analysis"
DEPENDENCIES = []  # 销售分析模块不依赖其他模块的数据

if __name__ == "__main__":
    # 测试运行
    result = run("daily_sales")
    if result:
        print(f"测试成功，文件路径: {result}")
    else:
        print("测试失败")
