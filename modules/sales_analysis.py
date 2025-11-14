"""
商品销售分析模块
用于查询和采集商品销售分析数据，支持多种参数模板
"""

import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import get_logger
from config.api_config import EXPORT_ENDPOINTS
from config.params_config import get_sales_analysis_params
from config.headers_config import HEADERS
from core.export_handler import ExportHandler
from core.download_handler import DownloadHandler

logger = get_logger(__name__)


class SalesAnalysisModule:
    """商品销售分析类"""
    
    def __init__(self):
        self.export_url = EXPORT_ENDPOINTS["sales_analysis"]
        self.export_handler = ExportHandler()
        self.download_handler = DownloadHandler()
        
    
    def run_full_process(self, template_name: str = "dairy_cold_drinks", custom_params: Optional[Dict[str, Any]] = None) -> Optional[Path]:
        """
        执行完整的导出和下载流程
        
        Args:
            template_name: 参数模板名称
            custom_params: 自定义参数
            
        Returns:
            下载的文件路径，失败返回None
        """
        logger.info(f"开始执行销售分析完整流程，模板: {template_name}")
        
        try:
            # 获取模板参数
            params = get_sales_analysis_params(template_name)
            
            # 合并自定义参数
            if custom_params:
                params.update(custom_params)
            
            logger.info(f"使用参数模板: {template_name}")
            logger.info(f"请求URL: {self.export_url}")
            
            # 直接使用导出处理器执行完整流程（导出+下载）
            # 使用中文名称匹配ERP系统中的任务名称
            download_url = self.export_handler.export_and_get_url(
                export_url=self.export_url,
                export_params=params,
                module_name="商品销售分析"
            )
            
            if not download_url:
                logger.error("导出任务失败，未获取到下载URL")
                return None
            
            logger.info(f"导出任务成功，下载URL: {download_url}")
            
            # 使用获得的URL下载文件
            file_path = self.download_handler.download_from_export(download_url, "商品销售数据")
            
            if file_path:
                logger.info(f"销售分析完整流程执行成功: {file_path}")
            else:
                logger.error("文件下载失败")
            
            return file_path
            
        except Exception as e:
            logger.error(f"销售分析完整流程执行异常: {str(e)}")
            return None


def run(template_name: str = "dairy_cold_drinks") -> Optional[Path]:
    """
    模块入口函数（供main.py调用）
    
    Args:
        template_name: 参数模板名称
        
    Returns:
        下载的文件路径，失败返回None
    """
    logger.info(f"启动销售分析模块，模板: {template_name}")
    
    try:
        module = SalesAnalysisModule()
        result = module.run_full_process(template_name)
        
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
