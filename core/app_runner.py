"""
应用程序执行器
"""

from modules.store_product_attr import StoreProductAttrModule
from modules.org_product_info import OrgProductInfoModule
from modules.inventory_query import InventoryQueryModule
from utils.logger import get_logger

logger = get_logger(__name__)


class AppRunner:
    """应用程序执行器"""
    
    def __init__(self):
        self.results = {}
    
    def run_store_product_attr(self):
        """执行门店商品属性模块"""
        try:
            module = StoreProductAttrModule()
            result = module.export_and_download()
            return bool(result)
        except Exception as e:
            logger.error(f"门店商品属性模块异常: {str(e)}")
            return False
    
    def run_inventory_query(self):
        """执行库存查询模块"""
        try:
            module = InventoryQueryModule()
            result = module.export_and_download()
            return bool(result)
        except Exception as e:
            logger.error(f"库存查询模块异常: {str(e)}")
            return False
    
    def run_org_product_info(self):
        """执行组织商品档案模块"""
        try:
            module = OrgProductInfoModule()
            result = module.export_and_download()
            return bool(result)
        except Exception as e:
            logger.error(f"组织商品档案模块异常: {str(e)}")
            return False
    
    def execute_modules(self, module_switches):
        """
        执行启用的模块
        
        Args:
            module_switches: 模块开关字典
            
        Returns:
            dict: 执行结果统计
        """
        total_modules = 0
        success_modules = 0
        failed_modules = []
        
        # 门店商品属性模块
        if module_switches.get("store_product_attr", False):
            total_modules += 1
            print(">> 执行门店商品属性模块...")
            if self.run_store_product_attr():
                success_modules += 1
                print("[成功] 门店商品属性模块完成")
            else:
                failed_modules.append("门店商品属性")
                print("[失败] 门店商品属性模块失败")
            print()
        
        # 库存查询模块
        if module_switches.get("inventory_query", False):
            total_modules += 1
            print(">> 执行库存查询模块...")
            if self.run_inventory_query():
                success_modules += 1
                print("[成功] 库存查询模块完成")
            else:
                failed_modules.append("库存查询")
                print("[失败] 库存查询模块失败")
            print()
        
        # 组织商品档案模块
        if module_switches.get("org_product_info", False):
            total_modules += 1
            print(">> 执行组织商品档案模块...")
            if self.run_org_product_info():
                success_modules += 1
                print("[成功] 组织商品档案模块完成")
            else:
                failed_modules.append("组织商品档案")
                print("[失败] 组织商品档案模块失败")
            print()
        
        return {
            "total": total_modules,
            "success": success_modules,
            "failed": failed_modules
        }
    
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
