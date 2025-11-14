"""
门店商品属性模块
"""

from pathlib import Path
from typing import Optional
from core.export_handler import ExportHandler
from core.download_handler import DownloadHandler
from config.api_config import EXPORT_ENDPOINTS
from config.params_config import STORE_PRODUCT_ATTR_EXPORT_PARAMS
from utils.logger import get_logger

logger = get_logger(__name__)


class StoreProductAttrModule:
    """门店商品属性数据采集模块"""
    
    def __init__(self):
        self.export_handler = ExportHandler()
        self.download_handler = DownloadHandler()
        self.module_name = "门店商品属性"
        self.export_url = EXPORT_ENDPOINTS["store_product_attr"]
        self.export_params = STORE_PRODUCT_ATTR_EXPORT_PARAMS
    
    def export_and_download(self) -> Optional[Path]:
        """
        执行完整的导出和下载流程
        
        Returns:
            下载文件的路径，失败返回None
        """
        logger.info(f"开始执行{self.module_name}导出和下载流程")
        
        try:
            # 1. 提交导出任务并获取下载URL
            logger.info("步骤1: 提交导出任务...")
            download_url = self.export_handler.export_and_get_url(
                self.export_url, 
                self.export_params, 
                self.module_name
            )
            
            if not download_url:
                logger.error("导出任务失败，未获取到下载URL")
                return None
            
            # 2. 下载文件
            logger.info("步骤2: 下载文件...")
            file_path = self.download_handler.download_from_export(
                download_url, 
                self.module_name
            )
            
            if file_path:
                logger.info(f"{self.module_name}导出和下载完成: {file_path}")
                return file_path
            else:
                logger.error("文件下载失败")
                return None
                
        except Exception as e:
            logger.error(f"{self.module_name}导出和下载过程中发生异常: {str(e)}")
            return None
    
    def export_only(self) -> Optional[str]:
        """
        仅执行导出任务，返回下载URL
        
        Returns:
            下载URL，失败返回None
        """
        logger.info(f"执行{self.module_name}导出任务")
        return self.export_handler.export_and_get_url(
            self.export_url, 
            self.export_params, 
            self.module_name
        )
    
    def download_only(self, download_url: str) -> Optional[Path]:
        """
        仅执行下载任务
        
        Args:
            download_url: 文件下载URL
            
        Returns:
            下载文件的路径，失败返回None
        """
        logger.info(f"执行{self.module_name}文件下载")
        return self.download_handler.download_from_export(download_url, self.module_name)


def main():
    """测试函数"""
    module = StoreProductAttrModule()
    result = module.export_and_download()
    
    if result:
        print(f"✅ 门店商品属性导出成功: {result}")
    else:
        print("❌ 门店商品属性导出失败")


if __name__ == "__main__":
    main()