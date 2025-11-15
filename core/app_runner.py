"""
应用程序执行器 - 统一模块调用接口
"""

from typing import Dict, Any, Optional
from modules.store_product_attr import StoreProductAttrModule
from modules.org_product_info import OrgProductInfoModule
from modules.inventory_query import InventoryQueryModule
from modules.store_management import StoreManagementModule
from modules.sales_analysis import SalesAnalysisModule
from modules.delivery_analysis import DeliveryAnalysisModule
from utils.logger import get_logger

logger = get_logger(__name__)


class AppRunner:
    """应用程序执行器 - 统一调用所有模块的execute方法"""
    
    # 模块映射表
    MODULE_CLASSES = {
        "store_product_attr": StoreProductAttrModule,
        "inventory_query": InventoryQueryModule,
        "org_product_info": OrgProductInfoModule,
        "store_management": StoreManagementModule,
        "sales_analysis": SalesAnalysisModule,
        "delivery_analysis": DeliveryAnalysisModule,
    }
    
    # 模块显示名称映射
    MODULE_DISPLAY_NAMES = {
        "store_product_attr": "门店商品属性",
        "inventory_query": "库存查询",
        "org_product_info": "组织商品档案",
        "store_management": "门店管理",
        "sales_analysis": "商品销售分析",
        "delivery_analysis": "配送分析",
    }
    
    def __init__(self):
        self.results = {}
    
    def run_module(self, module_key: str, module_config: Any) -> bool:
        """
        统一执行模块
        
        Args:
            module_key: 模块键名
            module_config: 模块配置（可以是bool/dict）
            
        Returns:
            bool: 执行是否成功
        """
        if module_key not in self.MODULE_CLASSES:
            logger.error(f"未知模块: {module_key}")
            return False
        
        try:
            # 获取模块类
            module_class = self.MODULE_CLASSES[module_key]
            display_name = self.MODULE_DISPLAY_NAMES.get(module_key, module_key)
            
            # 创建模块实例
            module = module_class()
            
            # 解析配置参数
            kwargs = self._parse_module_config(module_config)
            
            logger.info(f"开始执行模块: {display_name}")
            if kwargs:
                logger.info(f"模块参数: {list(kwargs.keys())}")
            
            # 统一调用execute方法
            result = module.execute(**kwargs)
            
            if result:
                logger.info(f"{display_name}执行成功: {result}")
                return True
            else:
                logger.error(f"{display_name}执行失败")
                return False
                
        except Exception as e:
            logger.error(f"{self.MODULE_DISPLAY_NAMES.get(module_key, module_key)}模块异常: {str(e)}")
            return False
    
    def _parse_module_config(self, config: Any) -> Dict[str, Any]:
        """
        解析模块配置（用于向后兼容）
        
        Args:
            config: 模块配置（字典/字符串/布尔）
            
        Returns:
            Dict: 参数字典
        """
        if isinstance(config, dict):
            return config
        elif isinstance(config, str):
            # 字符串配置，作为template_name参数（向后兼容）
            return {"template_name": config}
        else:
            # 布尔值或其他，返回空字典（无参数）
            return {}
    
    def execute_modules(self, module_switches: Dict[str, Any], 
                       module_params: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        执行启用的模块（统一调用方式）
        
        Args:
            module_switches: 模块启用开关字典
                推荐格式: {"module_name": True/False}
                向后兼容: {"module_name": "template_name"} 或 {"module_name": {...}}
                
            module_params: 模块参数配置字典（可选）
                格式: {"module_name": {"param1": "value1", ...}}
                只对启用的模块生效
                
        Returns:
            dict: 执行结果统计
            
        示例（推荐方式）：
            module_switches = {
                "store_management": False,  # 禁用
                "sales_analysis": True,     # 启用
            }
            
            module_params = {
                "sales_analysis": {
                    "template_name": "dairy_cold_drinks",
                    "bizday": ["2025-11-14", "2025-11-14"]
                }
            }
        """
        if module_params is None:
            module_params = {}
        
        total_modules = 0
        success_modules = 0
        failed_modules = []
        
        for module_key, module_switch in module_switches.items():
            # 向后兼容：处理旧格式配置
            # 旧格式: "sales_analysis": "dairy_cold_drinks" 或 {"template_name": ...}
            # 新格式: "sales_analysis": True/False
            if isinstance(module_switch, str) or (isinstance(module_switch, dict) and "template_name" in module_switch):
                # 旧格式：直接作为参数配置
                logger.warning(f"模块 {module_key} 使用旧配置格式，建议使用新格式（MODULE_SWITCHES + MODULE_PARAMS）")
                is_enabled = True
                # 如果MODULE_PARAMS中没有配置，使用旧格式的配置
                if module_key not in module_params:
                    module_params[module_key] = self._parse_module_config(module_switch)
            else:
                # 新格式：布尔值
                is_enabled = bool(module_switch)
            
            # 跳过未启用的模块
            if not is_enabled:
                continue
            
            # 获取显示名称
            display_name = self.MODULE_DISPLAY_NAMES.get(module_key, module_key)
            
            # 获取模块参数（如果有）
            module_config = module_params.get(module_key, {})
            
            # 打印执行信息
            total_modules += 1
            config_info = self._get_config_display(module_config)
            print(f">> 执行{display_name}模块{config_info}...")
            
            # 执行模块
            if self.run_module(module_key, module_config):
                success_modules += 1
                print(f"[成功] {display_name}模块完成")
            else:
                failed_modules.append(display_name)
                print(f"[失败] {display_name}模块失败")
            print()
        
        return {
            "total": total_modules,
            "success": success_modules,
            "failed": failed_modules
        }
    
    def _get_config_display(self, config: Any) -> str:
        """
        获取配置显示文本
        
        Args:
            config: 模块配置
            
        Returns:
            str: 显示文本
        """
        if isinstance(config, str):
            return f"（模板: {config}）"
        elif isinstance(config, dict):
            keys = list(config.keys())
            return f"（参数: {', '.join(keys[:3])}{'...' if len(keys) > 3 else ''}）"
        else:
            return ""
    
    def print_summary(self, results):
        """打印执行总结"""
        print("=" * 60)
        print(">>> 执行总结 <<<")
        print("=" * 60)
        print(f"总模块数: {results['total']}")
        print(f"成功模块数: {results['success']}")
        print(f"失败模块数: {len(results['failed'])}")
        
        if results['failed']:
            print(f"失败模块: {', '.join(results['failed'])}")
        
        if results['total'] == 0:
            print("[警告] 没有启用任何模块，请检查模块开关配置")
        elif results['success'] == results['total']:
            print("[成功] 所有模块执行成功！")
        else:
            print("[警告] 部分模块执行失败，请查看日志")
        
        print("=" * 60)
