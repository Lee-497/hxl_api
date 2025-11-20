"""
自动化数据报表脚本 - 主程序入口
"""

from core.app_runner import AppRunner
from core.report_manager import get_report_manager

# ==================== 数据采集模块 ====================
MODULE_SWITCHES = {
    "store_product_attr": False,    # 门店商品属性
    "inventory_query": False,       # 库存查询
    "inventory_statistics": False,  # 库存统计
    "org_product_info": False,      # 组织商品档案
    "store_management": False,      # 门店管理
    
    # 🆕 商品销售分析 - 多报表开关
    "sales_analysis": {
        "dairy_cold_drinks": False,              # 冷藏乳饮报表
        "store_adjustment_category_lv3": True, # 调改店-三级分类PSD
    },
    
    "delivery_analysis": False,     # 配送分析
}

# ==================== 模块参数 ====================
# 注意：sales_analysis 已改为字典开关，不需要在 MODULE_PARAMS 中配置
MODULE_PARAMS = {
    "delivery_analysis": {
        "template_name": "order_delivery",
    },
}

# ==================== 加工报表 ====================
ENABLE_PROCESSING = False

PROCESSING_SWITCHES = {
    # 库存汇总报表
    "inventory_summary_report": True,
    # 冷藏乳饮报表
    "sales_analysis_report": True,  # ✅ 启用销售分析报表
    # 订单配送分析报表
    "inventory_store_category_report": True,
}


def main():
    """主程序入口"""
    print("=" * 60)
    print(">>> 自动化数据报表脚本启动 <<<")
    print("=" * 60)
    
    app_runner = AppRunner()
    results = app_runner.execute_modules(MODULE_SWITCHES, MODULE_PARAMS)
    app_runner.print_summary(results)
    
    if ENABLE_PROCESSING:
        print()
        print("=" * 60)
        print(">>> 开始生成数据报表 <<<")
        print("=" * 60)
        
        report_manager = get_report_manager()
        report_manager.print_reports_info()
        report_results = report_manager.run_enabled_reports(PROCESSING_SWITCHES)
        
        print("=" * 60)
        print(">>> 报表生成总结 <<<")
        print("=" * 60)
        success_reports = [name for name, result in report_results.items() if result]
        failed_reports = [name for name, result in report_results.items() if not result]
        
        print(f"总报表数: {len(report_results)}")
        print(f"成功报表数: {len(success_reports)}")
        print(f"失败报表数: {len(failed_reports)}")
        
        if success_reports:
            print(f"成功报表: {', '.join(success_reports)}")
        if failed_reports:
            print(f"失败报表: {', '.join(failed_reports)}")
        
        print("=" * 60)


if __name__ == "__main__":
    main()