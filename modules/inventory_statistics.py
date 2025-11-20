"""
库存统计模块
与库存查询模块不同，用于统计分析
支持多仓库循环采集
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from core.base_module import BaseModule
from core.export_handler import ExportHandler
from core.download_handler import DownloadHandler
from config.api_config import EXPORT_ENDPOINTS
from config.params_config import INVENTORY_STATISTICS_WAREHOUSES, INVENTORY_STATISTICS_BASE_PARAMS
from utils.logger import get_logger

logger = get_logger(__name__)


class InventoryStatisticsModule(BaseModule):
    """库存统计数据采集模块 - 支持多仓库循环采集"""
    
    def __init__(self):
        super().__init__()
        self.module_display_name = "库存库位明细"  # 与导出记录匹配的名称
        self.export_url = EXPORT_ENDPOINTS["inventory_statistics"]
        self.base_params = INVENTORY_STATISTICS_BASE_PARAMS
        self.warehouses = INVENTORY_STATISTICS_WAREHOUSES
        self.export_handler = ExportHandler()
        self.download_handler = DownloadHandler()
    
    def execute(self, **kwargs) -> Optional[Path]:
        """
        执行多仓库循环采集
        
        Args:
            **kwargs: 可选参数
                - warehouses: 自定义仓库列表（覆盖默认配置）
        
        Returns:
            最后一个成功下载的文件路径，全部失败返回None
        """
        # 获取仓库列表
        warehouses = kwargs.get('warehouses', self.warehouses)
        
        if not warehouses:
            logger.error("仓库列表为空，无法执行采集")
            return None
        
        logger.info(f"开始库存统计多仓库采集，共 {len(warehouses)} 个仓库")
        
        success_count = 0
        failed_count = 0
        last_success_file = None
        
        # 循环处理每个仓库
        for index, warehouse in enumerate(warehouses, 1):
            warehouse_name = warehouse.get('name', f'仓库{index}')
            store_id = warehouse.get('store_id')
            storehouse_id = warehouse.get('storehouse_id')
            
            logger.info(f"[{index}/{len(warehouses)}] 开始采集: {warehouse_name}")
            logger.info(f"  门店ID: {store_id}, 仓库ID: {storehouse_id}")
            
            # 构建导出参数
            export_params = self.base_params.copy()
            export_params['store_ids'] = [store_id]
            export_params['storehouse_ids'] = [storehouse_id]
            
            # 执行单个仓库的导出下载
            file_path = self._export_single_warehouse(
                warehouse_name=warehouse_name,
                export_params=export_params
            )
            
            if file_path:
                logger.info(f"✅ [{warehouse_name}] 采集成功: {file_path}")
                success_count += 1
                last_success_file = file_path
            else:
                logger.error(f"❌ [{warehouse_name}] 采集失败")
                failed_count += 1
            
            print()  # 空行分隔
        
        # 打印总结
        logger.info("=" * 60)
        logger.info(f"库存统计采集完成: 成功 {success_count}/{len(warehouses)}, 失败 {failed_count}")
        logger.info("=" * 60)
        
        return last_success_file
    
    def _export_single_warehouse(self, warehouse_name: str, export_params: Dict[str, Any]) -> Optional[Path]:
        """
        执行单个仓库的导出和下载
        
        Args:
            warehouse_name: 仓库名称
            export_params: 导出参数
        
        Returns:
            下载的文件路径，失败返回None
        """
        try:
            # 1. 提交导出任务并获取下载URL
            download_url = self.export_handler.export_and_get_url(
                export_url=self.export_url,
                export_params=export_params,
                module_name=self.module_display_name
            )
            
            if not download_url:
                logger.error(f"[{warehouse_name}] 导出任务失败，未获取到下载URL")
                return None
            
            logger.info(f"[{warehouse_name}] 获取到下载URL: {download_url}")
            
            # 2. 下载文件（使用仓库名称作为文件名前缀）
            file_name_prefix = f"库存库位明细_{warehouse_name}"
            file_path = self.download_handler.download_from_export(
                download_url=download_url,
                module_name=self.module_display_name,
                file_name_prefix=file_name_prefix,
            )
            
            return file_path
            
        except Exception as e:
            logger.error(f"[{warehouse_name}] 采集异常: {str(e)}")
            return None


def main():
    """测试函数"""
    module = InventoryStatisticsModule()
    result = module.execute()
    
    if result:
        print(f"✅ 库存统计导出成功: {result}")
    else:
        print("❌ 库存统计导出失败")


if __name__ == "__main__":
    main()
