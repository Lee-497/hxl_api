"""
自动化数据报表脚本 - 主程序入口
"""

from core.app_runner import AppRunner
from core.report_manager import get_report_manager

# ==================== 模块开关配置 ====================
# 设置为 True 启用对应模块，False 禁用
MODULE_SWITCHES = {
    "store_product_attr": False,      # 门店商品属性
    "inventory_query": False,         # 库存查询
    "org_product_info": False,       # 组织商品档案
    "store_management": True,        # 门店管理
}

# ==================== 加工报表配置 ====================
# 设置为 True 启用加工报表生成，False 禁用
ENABLE_PROCESSING = True

# 可以单独控制每个报表的启用状态
PROCESSING_SWITCHES = {
    "inventory_summary_report": False,    # 库存汇总报表
    # 可以在这里添加更多报表的开关
}


def main():
    """主程序入口"""
    print("=" * 60)
    print(">>> 自动化数据报表脚本启动 <<<")
    print("=" * 60)
    
    # 创建应用执行器
    app_runner = AppRunner()
    
    # 执行启用的模块
    results = app_runner.execute_modules(MODULE_SWITCHES)
    
    # 打印执行总结
    app_runner.print_summary(results)
    
    # 生成加工报表（如果启用）
    if ENABLE_PROCESSING:
        print()
        print("=" * 60)
        print(">>> 开始生成数据报表 <<<")
        print("=" * 60)
        
        report_manager = get_report_manager()
        report_manager.print_reports_info()
        
        # 运行启用的报表
        report_results = report_manager.run_enabled_reports(PROCESSING_SWITCHES)
        
        # 报表总结
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