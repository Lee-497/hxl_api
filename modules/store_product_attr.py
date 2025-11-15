"""
门店商品属性模块
"""

from pathlib import Path
from typing import Optional, Dict, Any
from core.base_module import ExportBasedModule
from config.api_config import EXPORT_ENDPOINTS
from config.params_config import STORE_PRODUCT_ATTR_EXPORT_PARAMS
from utils.logger import get_logger

logger = get_logger(__name__)


class StoreProductAttrModule(ExportBasedModule):
    """门店商品属性数据采集模块"""
    
    def __init__(self):
        super().__init__()
        self.module_display_name = "门店商品属性"
        self.export_url = EXPORT_ENDPOINTS["store_product_attr"]
        self.export_params = STORE_PRODUCT_ATTR_EXPORT_PARAMS
    
    def get_export_config(self, **kwargs) -> Dict[str, Any]:
        """
        获取导出配置
        
        Returns:
            导出配置字典
        """
        return {
            'export_url': self.export_url,
            'export_params': self.export_params,
            'module_name': self.module_display_name
        }
    


def main():
    """测试函数"""
    module = StoreProductAttrModule()
    result = module.execute()
    
    if result:
        print(f"✅ 门店商品属性导出成功: {result}")
    else:
        print("❌ 门店商品属性导出失败")


if __name__ == "__main__":
    main()