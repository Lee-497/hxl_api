"""
自动化数据报表脚本 - 主程序入口
"""

from core.app_runner import AppRunner
from core.report_manager import get_report_manager

# ==================== 数据采集模块 ====================
MODULE_SWITCHES = {
    "store_product_attr": True,     # 门店商品属性
    "inventory_query": True,        # 库存查询
    "inventory_statistics": False,  # 库存统计
    "org_product_info": True,       # 组织商品档案
    "store_management": True,       # 门店管理
    "org_item_mapping": False,       # 组织档案映射清单
    # 🆕 商品销售分析 - 多报表开关
    "sales_analysis": {
        "dairy_cold_drinks": True,                     # 冷藏乳饮报表
        "store_adjustment_category_lv3": False,        # 调改店-三级分类PSD
        "store_adjustment_planning_sku": False,        # 调改店-规划SKU
        "store_adjustment_all_sku": False,             # 调改店-全店SKU
        "store_adjustment_grain_oil_nonfood": False,   # 调改店-粮油非食
        "store_adjustment_frozen": False,              # 调改店-冷冻
    },
    "delivery_analysis": True,                  # 配送分析
}

# ==================== 模块参数 ====================
# 注意：sales_analysis 已改为字典开关，不需要在 MODULE_PARAMS 中配置
MODULE_PARAMS = {
    "delivery_analysis": {
        "template_name": "order_delivery",
    },
    # 🔧 为 sales_analysis 自定义日期范围（会应用到所有启用的模板）
    "sales_analysis": {
        "store_adjustment_planning_sku_bizday": ["2025-10-01", "2025-11-20"],  # 门店规划SKU自定义日期范围
        "store_adjustment_other_bizday": ["2025-11-01", "2025-11-20"]       # 三级分类和全店SKU自定义日期范围
    }
}

# ==================== 加工报表 ====================
ENABLE_PROCESSING = True

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