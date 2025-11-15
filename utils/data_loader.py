"""
数据加载工具
用于加载原始数据和架构信息表
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from config.settings import DOWNLOADS_DIR, REFERENCE_DIR
from utils.logger import get_logger
from utils.file_utils import get_module_files

logger = get_logger(__name__)


class DataLoader:
    """数据加载器"""
    
    def __init__(self):
        self.downloads_dir = DOWNLOADS_DIR
        self.reference_dir = REFERENCE_DIR
        
        # 英文模块名到中文文件名的映射
        self.module_name_mapping = {
            "inventory_query": "库存查询",
            "store_product_attr": "门店商品属性",
            "store_product_attributes": "门店商品属性",
            "org_product_info": "组织商品档案",
            "product_archive": "组织商品档案",
            "sales_analysis": "商品销售数据",
            "delivery_analysis": "配送分析",
            "订单配送": "订单配送",
        }
    
    def load_latest_module_data(self, module_name: str) -> Optional[pd.DataFrame]:
        """
        加载指定模块的最新数据文件
        
        Args:
            module_name: 模块名称（英文或中文）
            
        Returns:
            DataFrame或None
        """
        try:
            # 获取实际的文件名前缀（中文名）
            file_name_prefix = self.module_name_mapping.get(module_name, module_name)
            
            files = get_module_files(self.downloads_dir, file_name_prefix)
            if not files:
                logger.error(f"未找到 {module_name} 的数据文件")
                print(f"❌ 未找到 {module_name} 的数据文件")
                return None
            
            latest_file = files[0]  # 已按时间排序，第一个是最新的
            logger.info(f"加载数据文件: {latest_file}")
            print(f"✅ 找到数据文件: {latest_file.name}")
            
            df = pd.read_excel(latest_file)
            logger.info(f"成功加载 {module_name} 数据: {len(df)} 行, {len(df.columns)} 列")
            print(f"✅ 成功加载数据: {len(df)} 行, {len(df.columns)} 列")
            return df
            
        except Exception as e:
            logger.error(f"加载 {module_name} 数据失败: {str(e)}")
            print(f"❌ 加载 {module_name} 数据失败: {str(e)}")
            return None
    
    def load_reference_data(self, reference_name: str) -> Optional[pd.DataFrame]:
        """
        加载架构信息表
        
        Args:
            reference_name: 架构表名称（不含扩展名）
            
        Returns:
            DataFrame或None
        """
        try:
            file_path = self.reference_dir / f"{reference_name}.xlsx"
            if not file_path.exists():
                logger.warning(f"架构信息表不存在: {file_path}")
                return None
            
            df = pd.read_excel(file_path)
            logger.info(f"成功加载架构信息表 {reference_name}: {len(df)} 行, {len(df.columns)} 列")
            return df
            
        except Exception as e:
            logger.error(f"加载架构信息表 {reference_name} 失败: {str(e)}")
            return None
    
    def load_multiple_modules(self, module_names: list) -> Dict[str, pd.DataFrame]:
        """
        批量加载多个模块的数据
        
        Args:
            module_names: 模块名称列表
            
        Returns:
            模块名到DataFrame的字典
        """
        data_dict = {}
        
        for module_name in module_names:
            df = self.load_latest_module_data(module_name)
            if df is not None:
                data_dict[module_name] = df
            else:
                logger.warning(f"跳过模块 {module_name}，数据加载失败")
        
        logger.info(f"成功加载 {len(data_dict)}/{len(module_names)} 个模块的数据")
        return data_dict


def get_data_loader() -> DataLoader:
    """获取数据加载器实例"""
    return DataLoader()
