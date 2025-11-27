"""
组织档案映射清单模块
通过分页API采集商品基础信息（code, item_id, name）
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

from core.base_module import ApiBasedModule
from config.api_config import API_ENDPOINTS
from config.params_config import ORG_ITEM_MAPPING_QUERY_PARAMS
from utils.logger import get_logger
from utils.file_utils import cleanup_module_files
from config.settings import DOWNLOADS_DIR

logger = get_logger(__name__)


class OrgItemMappingModule(ApiBasedModule):
    """组织档案映射清单数据采集模块"""

    def __init__(self) -> None:
        super().__init__()
        self.api_url = API_ENDPOINTS["org_item_mapping"]
        self.module_display_name = "组织档案映射清单"

    def fetch_data(self, **kwargs) -> Optional[list]:
        """
        分页获取所有商品数据
        
        Returns:
            Optional[list]: 商品数据列表
        """
        logger.info(f"开始采集{self.module_display_name}数据")
        
        # 使用配置文件中的请求参数
        base_params = ORG_ITEM_MAPPING_QUERY_PARAMS.copy()
        
        all_items = []
        page_number = 0
        total_pages = None
        
        while True:
            # 更新页码
            base_params["page_number"] = page_number
            
            logger.info(f"正在获取第 {page_number + 1} 页数据...")
            
            # 发送请求
            response = self.request_handler.post(
                url=self.api_url,
                json_data=base_params
            )
            
            if not response or response.get("code") != 0:
                logger.error(f"获取第 {page_number + 1} 页失败")
                break
            
            # 解析数据
            data = response.get("data", {})
            content = data.get("content", [])
            
            if total_pages is None:
                total_pages = data.get("total_pages", 0)
                total_elements = data.get("total_elements", 0)
                logger.info(f"总页数: {total_pages}, 总记录数: {total_elements}")
            
            # 提取关键字段
            for item in content:
                all_items.append({
                    "code": item.get("code"),
                    "item_id": item.get("item_id"),
                    "name": item.get("name")
                })
            
            logger.info(f"第 {page_number + 1} 页完成，获取 {len(content)} 条数据")
            
            # 判断是否最后一页
            if data.get("last", True):
                logger.info("已到达最后一页")
                break
            
            page_number += 1
        
        logger.info(f"总共采集 {len(all_items)} 条数据")
        return all_items if all_items else None

    def save_data(self, data: Any) -> Optional[Path]:
        """
        保存数据到Excel文件
        
        Args:
            data: 商品数据列表
            
        Returns:
            Optional[Path]: 保存的文件路径
        """
        try:
            # 转换为DataFrame
            df = pd.DataFrame(data)
            
            # 🔧 关键修复：去重处理（双重保障）
            original_count = len(df)
            df = df.drop_duplicates(subset=['code'], keep='first')
            dedup_count = len(df)
            if original_count != dedup_count:
                logger.info(f"去重处理: {original_count} → {dedup_count} 条记录")
            
            # 🔧 关键优化：将 code 字段转换为整数类型（避免Excel的数字文本警告）
            if 'code' in df.columns:
                # 先转为字符串去除空格，再转为整数
                df['code'] = pd.to_numeric(df['code'], errors='coerce').astype('Int64')
                logger.info(f"已将 code 字段转换为整数类型")
            
            # 🗑️ 删除旧文件（确保文件夹中每个类型只有一个文件）
            deleted = cleanup_module_files(DOWNLOADS_DIR, self.module_display_name, keep_latest=0)
            if deleted > 0:
                logger.info(f"清理了 {deleted} 个旧的{self.module_display_name}文件")
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.module_display_name}_{timestamp}.xlsx"
            filepath = DOWNLOADS_DIR / filename
            
            # 保存为Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            logger.info(f"数据已保存到: {filepath}")
            logger.info(f"文件大小: {filepath.stat().st_size / 1024:.2f} KB")
            logger.info(f"数据行数: {len(df)}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"保存数据失败: {str(e)}")
            return None

    def execute(self, **kwargs) -> Optional[Path]:
        """执行数据采集任务"""
        return super().execute(**kwargs)
