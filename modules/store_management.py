"""
门店管理模块
用于查询和采集门店信息，保存为Excel文件
此模块使用直接API调用方式，不同于其他模块的导出任务方式
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List
from core.base_module import ApiBasedModule
from utils.logger import get_logger
from utils.file_utils import generate_timestamped_filename, cleanup_module_files
from config.api_config import EXPORT_ENDPOINTS
from config.params_config import STORE_MANAGEMENT_QUERY_PARAMS
from config.settings import DOWNLOADS_DIR

logger = get_logger(__name__)


class StoreManagementModule(ApiBasedModule):
    """门店管理数据采集模块（使用直接API调用方式）"""
    
    def __init__(self):
        super().__init__()
        self.base_url = EXPORT_ENDPOINTS["store_management"]
        self.default_params = STORE_MANAGEMENT_QUERY_PARAMS.copy()
        self.module_display_name = "门店管理"
    
    def fetch_data(self, **kwargs) -> Optional[List[Dict[str, Any]]]:
        """
        获取门店数据（实现ApiBasedModule抽象方法）
        
        Returns:
            门店数据列表
        """
        result = self.get_all_stores()
        if "error" in result:
            return None
        return result.get("data", [])
    
    def save_data(self, data: List[Dict[str, Any]]) -> Optional[Path]:
        """
        保存门店数据到Excel（实现ApiBasedModule抽象方法）
        
        Args:
            data: 门店数据列表
            
        Returns:
            保存的文件路径
        """
        try:
            # 提取关键字段
            extracted_data = self.extract_store_data(data)
            
            # 转换为DataFrame
            df = pd.DataFrame(extracted_data)
            
            # 🗑️ 删除旧文件（确保文件夹中每个类型只有一个文件）
            deleted = cleanup_module_files(DOWNLOADS_DIR, self.module_display_name, keep_latest=0)
            if deleted > 0:
                logger.info(f"清理了 {deleted} 个旧的{self.module_display_name}文件")
            
            # 生成文件名
            filename = generate_timestamped_filename(self.module_display_name, "xlsx")
            file_path = DOWNLOADS_DIR / filename
            
            # 确保目录存在
            DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
            
            # 保存到Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            logger.info(f"门店数据已保存到: {file_path}")
            logger.info(f"保存门店数量: {len(extracted_data)}")
            
            return file_path
            
        except Exception as e:
            logger.error(f"保存门店数据失败: {str(e)}")
            return None
        
    def query_stores(self, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        查询门店信息
        
        Args:
            custom_params: 自定义查询参数，会覆盖默认参数
            
        Returns:
            查询结果字典
        """
        try:
            # 合并参数
            params = self.default_params.copy()
            if custom_params:
                params.update(custom_params)
            
            logger.info(f"开始查询门店信息")
            logger.info(f"请求URL: {self.base_url}")
            logger.info(f"请求参数: {json.dumps(params, indent=2, ensure_ascii=False)}")
            
            # 使用 RequestHandler 发送POST请求
            result = self.request_handler.post(self.base_url, params)
            
            if not result:
                logger.error("门店查询请求失败")
                return {"error": "请求失败"}
            
            logger.info("门店查询成功")
            
            # 记录响应数据统计和结构
            if isinstance(result, dict):
                logger.info(f"API响应结构: {list(result.keys())}")
                
                # 检查不同的数据格式
                if 'data' in result:
                    data = result['data']
                    if isinstance(data, dict):
                        logger.info(f"data是字典，键: {list(data.keys())}")
                        if 'content' in data:
                            content = data['content']
                            logger.info(f"content类型: {type(content)}, 长度: {len(content) if isinstance(content, list) else 'N/A'}")
                    elif isinstance(data, list):
                        logger.info(f"data是列表，长度: {len(data)}")
                elif 'total' in result:
                    logger.info(f"门店总数: {result['total']}")
            
            return result
            
        except Exception as e:
            logger.error(f"门店查询发生错误: {str(e)}")
            return {"error": f"查询失败: {str(e)}"}
    
    def query_stores_by_group(self, store_group_ids: list) -> Dict[str, Any]:
        """
        根据门店组ID查询门店
        
        Args:
            store_group_ids: 门店组ID列表
            
        Returns:
            查询结果字典
        """
        custom_params = {
            "store_group_ids": store_group_ids
        }
        return self.query_stores(custom_params)
    
    def query_stores_by_area(self, business_area_ids: list) -> Dict[str, Any]:
        """
        根据商圈ID查询门店
        
        Args:
            business_area_ids: 商圈ID列表
            
        Returns:
            查询结果字典
        """
        custom_params = {
            "business_area_ids": business_area_ids
        }
        return self.query_stores(custom_params)
    
    def query_stores_by_city(self, city_codes: list) -> Dict[str, Any]:
        """
        根据城市代码查询门店
        
        Args:
            city_codes: 城市代码列表
            
        Returns:
            查询结果字典
        """
        custom_params = {
            "city_codes": city_codes
        }
        return self.query_stores(custom_params)
    
    def query_stores_with_pagination(self, page_number: int = 0, page_size: int = 200) -> Dict[str, Any]:
        """
        分页查询门店
        
        Args:
            page_number: 页码，从0开始
            page_size: 每页大小
            
        Returns:
            查询结果字典
        """
        custom_params = {
            "page_number": page_number,
            "page_size": page_size
        }
        return self.query_stores(custom_params)
    
    def get_all_stores(self) -> Dict[str, Any]:
        """
        获取所有门店信息（自动分页）
        
        Returns:
            包含所有门店的结果字典
        """
        all_stores = []
        page_number = 0
        page_size = 200
        
        try:
            while True:
                logger.info(f"正在获取第 {page_number + 1} 页门店数据...")
                
                result = self.query_stores_with_pagination(page_number, page_size)
                
                if "error" in result:
                    logger.error(f"获取门店数据失败: {result['error']}")
                    break
                
                # 解析API返回的标准格式
                if result.get('code') == 0 and 'data' in result:
                    data = result['data']
                    if isinstance(data, dict) and 'content' in data:
                        # 标准分页格式: {code: 0, data: {content: [...], total_elements: N}}
                        current_stores = data.get('content', [])
                        total_elements = data.get('total_elements', 0)
                        total_pages = data.get('total_pages', 1)
                        current_page = data.get('number', 0)
                        
                        logger.info(f"第{current_page + 1}页: {len(current_stores)}个门店，总计{total_elements}个，共{total_pages}页")
                        
                        if not current_stores:
                            logger.info(f"第{current_page + 1}页没有数据，停止分页")
                            break
                        
                        all_stores.extend(current_stores)
                        logger.info(f"累计获取: {len(all_stores)}个门店")
                        
                        # 检查是否还有更多页
                        if current_page + 1 >= total_pages:
                            logger.info(f"已获取所有{total_pages}页数据")
                            break
                            
                        page_number += 1
                    else:
                        logger.warning(f"数据格式异常: data字段不包含content")
                        break
                else:
                    logger.error(f"API返回错误: code={result.get('code')}, msg={result.get('msg')}")
                    break
            
            logger.info(f"总共获取到 {len(all_stores)} 个门店")
            
            return {
                "success": True,
                "total": len(all_stores),
                "data": all_stores
            }
            
        except Exception as e:
            logger.error(f"获取所有门店数据时发生错误: {str(e)}")
            return {"error": f"获取所有门店失败: {str(e)}"}
    
    def extract_store_data(self, stores_data: list) -> list:
        """
        提取门店关键信息
        
        Args:
            stores_data: 原始门店数据列表
            
        Returns:
            提取后的门店信息列表
        """
        extracted_stores = []
        
        for store in stores_data:
            if not isinstance(store, dict):
                continue
                
            # 只提取需要的6个字段
            extracted_store = {
                "id": store.get("id"),
                "store_number": store.get("store_number"),
                "store_name": store.get("store_name"),
                "opening_time": store.get("opening_time"),
                "create_time": store.get("create_time"),
                "status": store.get("status")
            }
            
            extracted_stores.append(extracted_store)
        
        return extracted_stores
    
    def _determine_store_enabled_status(self, store: dict) -> bool:
        """
        判断门店启用状态
        
        Args:
            store: 门店数据字典
            
        Returns:
            bool: True表示启用，False表示未启用
        """
        # 主要状态字段
        status = store.get("status")
        state = store.get("state", "").upper()
        store_status = store.get("store_status", "").upper()
        opening_status = store.get("opening_status")
        
        # 判断逻辑：如果明确关闭或状态为False，则未启用
        if (state in ["CLOSED"] or 
            "CLOSED" in store_status or 
            status is False or 
            opening_status is False):
            return False
            
        return True
    


def main():
    """测试门店管理功能"""
    store_mgmt = StoreManagementModule()
    
    print("=== 门店管理模块测试 ===")
    
    # 测试统一接口
    print("\n1. 测试execute接口...")
    result = store_mgmt.execute()
    
    if result:
        print(f"✅ 门店数据采集成功，文件保存至: {result}")
    else:
        print("❌ 门店数据采集失败")


if __name__ == "__main__":
    main()
