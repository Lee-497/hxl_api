"""
库存查询模块
"""

from pathlib import Path
from typing import Optional, Dict, Any
from core.base_module import ExportBasedModule
from config.api_config import EXPORT_ENDPOINTS
from config.params_config import INVENTORY_QUERY_EXPORT_PARAMS
from utils.logger import get_logger

logger = get_logger(__name__)


class InventoryQueryModule(ExportBasedModule):
    """库存查询数据采集模块"""
    
    def __init__(self):
        super().__init__()
        self.module_display_name = "库存查询"
        self.export_url = EXPORT_ENDPOINTS["inventory_query"]
        self.export_params = INVENTORY_QUERY_EXPORT_PARAMS
    
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
    module = InventoryQueryModule()
    result = module.execute()
    
    if result:
        print(f"✅ 库存查询导出成功: {result}")
    else:
        print("❌ 库存查询导出失败")


if __name__ == "__main__":
    main()