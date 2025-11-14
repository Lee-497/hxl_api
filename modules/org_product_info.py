"""
组织商品档案模块
"""

from pathlib import Path
from typing import Optional
from core.export_handler import ExportHandler
from core.download_handler import DownloadHandler
from config.api_config import EXPORT_ENDPOINTS
from config.params_config import ORG_PRODUCT_INFO_EXPORT_PARAMS
from utils.logger import get_logger

logger = get_logger(__name__)


class OrgProductInfoModule:
    """组织商品档案数据采集模块"""
    
    def __init__(self):
        self.export_handler = ExportHandler()
        self.download_handler = DownloadHandler()
        self.module_name = "组织商品档案"
        self.export_url = EXPORT_ENDPOINTS["org_product_info"]
        self.export_params = ORG_PRODUCT_INFO_EXPORT_PARAMS
    
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
    module = OrgProductInfoModule()
    result = module.export_and_download()
    
    if result:
        print(f"✅ 组织商品档案导出成功: {result}")
    else:
        print("❌ 组织商品档案导出失败")


if __name__ == "__main__":
    main()