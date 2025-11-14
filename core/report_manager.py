"""
报表管理器
统一管理所有数据加工报表
"""

import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportManager:
    """报表管理器"""
    
    def __init__(self):
        self.processing_dir = Path(__file__).parent.parent / "processing"
        self.available_reports = {}
        self._discover_reports()
    
    def _discover_reports(self):
        """自动发现所有报表模块"""
        if not self.processing_dir.exists():
            logger.warning("processing目录不存在")
            return
        
        for py_file in self.processing_dir.glob("*_report.py"):
            if py_file.name == "__init__.py":
                continue
            
            module_name = py_file.stem
            try:
                # 动态导入报表模块
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 检查必要的函数和变量
                if hasattr(module, 'run') and hasattr(module, 'DEPENDENCIES'):
                    self.available_reports[module_name] = {
                        'module': module,
                        'file_path': py_file,
                        'dependencies': getattr(module, 'DEPENDENCIES', []),
                        'description': getattr(module, 'get_description', lambda: '无描述')()
                    }
                    logger.info(f"发现报表模块: {module_name}")
                else:
                    logger.warning(f"报表模块 {module_name} 缺少必要的函数或变量")
                    
            except Exception as e:
                logger.error(f"加载报表模块 {module_name} 失败: {str(e)}")
    
    def list_reports(self) -> Dict[str, dict]:
        """列出所有可用报表"""
        return self.available_reports.copy()
    
    def get_report_info(self, report_name: str) -> Optional[dict]:
        """获取指定报表的信息"""
        return self.available_reports.get(report_name)
    
    def run_report(self, report_name: str) -> Optional[Path]:
        """
        运行指定报表
        
        Args:
            report_name: 报表名称
            
        Returns:
            生成的报表文件路径，失败返回None
        """
        if report_name not in self.available_reports:
            logger.error(f"报表 {report_name} 不存在")
            return None
        
        report_info = self.available_reports[report_name]
        logger.info(f"开始运行报表: {report_name}")
        logger.info(f"依赖模块: {report_info['dependencies']}")
        
        try:
            # 运行报表
            result = report_info['module'].run()
            
            if result:
                logger.info(f"报表 {report_name} 运行成功: {result}")
            else:
                logger.error(f"报表 {report_name} 运行失败")
            
            return result
            
        except Exception as e:
            logger.error(f"运行报表 {report_name} 时发生异常: {str(e)}")
            return None
    
    def run_all_reports(self) -> Dict[str, Optional[Path]]:
        """
        运行所有报表
        
        Returns:
            报表名称到结果文件路径的字典
        """
        results = {}
        
        logger.info(f"开始运行所有报表，共 {len(self.available_reports)} 个")
        
        for report_name in self.available_reports:
            print(f">> 运行报表: {report_name}")
            result = self.run_report(report_name)
            results[report_name] = result
            
            if result:
                print(f"[成功] {report_name} 完成")
            else:
                print(f"[失败] {report_name} 失败")
            print()
        
        return results
    
    def run_enabled_reports(self, processing_switches: Dict[str, bool]) -> Dict[str, Optional[Path]]:
        """
        运行启用的报表
        
        Args:
            processing_switches: 报表开关配置字典
            
        Returns:
            报表名称到结果文件路径的字典
        """
        results = {}
        enabled_reports = [name for name, enabled in processing_switches.items() if enabled and name in self.available_reports]
        
        if not enabled_reports:
            logger.warning("没有启用任何报表")
            print("[警告] 没有启用任何报表，请检查 PROCESSING_SWITCHES 配置")
            return results
        
        logger.info(f"开始运行启用的报表，共 {len(enabled_reports)} 个")
        
        for report_name in enabled_reports:
            print(f">> 运行报表: {report_name}")
            result = self.run_report(report_name)
            results[report_name] = result
            
            if result:
                print(f"[成功] {report_name} 完成")
            else:
                print(f"[失败] {report_name} 失败")
            print()
        
        # 显示被跳过的报表
        skipped_reports = [name for name, enabled in processing_switches.items() if not enabled and name in self.available_reports]
        if skipped_reports:
            print(f"[跳过] 以下报表被禁用: {', '.join(skipped_reports)}")
            print()
        
        return results
    
    def check_dependencies(self, report_name: str, available_modules: List[str]) -> bool:
        """
        检查报表依赖是否满足
        
        Args:
            report_name: 报表名称
            available_modules: 可用的模块列表
            
        Returns:
            依赖是否满足
        """
        if report_name not in self.available_reports:
            return False
        
        dependencies = self.available_reports[report_name]['dependencies']
        missing_deps = [dep for dep in dependencies if dep not in available_modules]
        
        if missing_deps:
            logger.warning(f"报表 {report_name} 缺少依赖: {missing_deps}")
            return False
        
        return True
    
    def print_reports_info(self):
        """打印所有报表信息"""
        if not self.available_reports:
            print("未发现任何报表模块")
            return
        
        print("=" * 80)
        print(">>> 可用报表列表 <<<")
        print("=" * 80)
        
        for report_name, info in self.available_reports.items():
            print(f"报表名称: {report_name}")
            print(f"描述: {info['description']}")
            print(f"依赖模块: {', '.join(info['dependencies']) if info['dependencies'] else '无'}")
            print(f"文件路径: {info['file_path']}")
            print("-" * 80)


def get_report_manager() -> ReportManager:
    """获取报表管理器实例"""
    return ReportManager()
