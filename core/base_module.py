"""
基础模块抽象类
定义所有数据采集模块的统一接口规范
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseModule(ABC):
    """
    数据采集模块基类
    所有数据采集模块必须继承此类并实现 execute 方法
    """
    
    def __init__(self):
        self.module_name = self.__class__.__name__
        
    @abstractmethod
    def execute(self, **kwargs) -> Optional[Path]:
        """
        执行数据采集任务
        
        Args:
            **kwargs: 模块特定的参数
            
        Returns:
            Optional[Path]: 生成的文件路径，失败返回None
        """
        pass
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        获取模块信息
        
        Returns:
            Dict: 包含模块名称、类型、描述等信息
        """
        return {
            "name": self.module_name,
            "type": self.__class__.__bases__[0].__name__
        }


class ExportBasedModule(BaseModule):
    """
    基于导出任务的数据采集模块
    适用于：库存查询、组织商品档案、门店商品属性、商品销售分析
    
    这类模块的特点：
    1. 通过POST请求提交导出任务
    2. 轮询导出任务状态
    3. 获取下载URL并下载文件
    """
    
    def __init__(self):
        super().__init__()
        from core.export_handler import ExportHandler
        from core.download_handler import DownloadHandler
        
        self.export_handler = ExportHandler()
        self.download_handler = DownloadHandler()
    
    @abstractmethod
    def get_export_config(self, **kwargs) -> Dict[str, Any]:
        """
        获取导出配置（子类必须实现）
        
        Args:
            **kwargs: 用户传入的参数
            
        Returns:
            Dict: 包含 export_url, export_params, module_name 的字典
        """
        pass
    
    def execute(self, **kwargs) -> Optional[Path]:
        """
        执行导出任务流程
        
        Args:
            **kwargs: 模块特定参数
            
        Returns:
            Optional[Path]: 下载的文件路径
        """
        try:
            logger.info(f"开始执行{self.module_name}导出流程")
            
            # 获取导出配置
            config = self.get_export_config(**kwargs)
            export_url = config['export_url']
            export_params = config['export_params']
            module_name = config['module_name']
            file_name_prefix = config.get('file_name_prefix', module_name)
            
            logger.info(f"导出URL: {export_url}")
            logger.info(f"模块名称: {module_name}")
            
            # 1. 提交导出任务并获取下载URL
            download_url = self.export_handler.export_and_get_url(
                export_url=export_url,
                export_params=export_params,
                module_name=module_name
            )
            
            if not download_url:
                logger.error("导出任务失败，未获取到下载URL")
                return None
            
            logger.info(f"获取到下载URL: {download_url}")
            
            # 2. 下载文件
            file_path = self.download_handler.download_from_export(
                download_url=download_url,
                module_name=module_name,
                file_name_prefix=file_name_prefix,
            )
            
            if file_path:
                logger.info(f"{self.module_name}执行成功: {file_path}")
            else:
                logger.error(f"{self.module_name}文件下载失败")
            
            return file_path
            
        except Exception as e:
            logger.error(f"{self.module_name}执行异常: {str(e)}")
            return None


class ApiBasedModule(BaseModule):
    """
    基于直接API调用的数据采集模块
    适用于：门店管理
    
    这类模块的特点：
    1. 直接调用API接口获取数据
    2. 可能需要分页处理
    3. 自行组装数据并保存为文件
    """
    
    def __init__(self):
        super().__init__()
        from core.request_handler import RequestHandler
        
        self.request_handler = RequestHandler()
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> Optional[Any]:
        """
        获取数据（子类必须实现）
        
        Args:
            **kwargs: 用户传入的参数
            
        Returns:
            Any: 获取到的数据
        """
        pass
    
    @abstractmethod
    def save_data(self, data: Any) -> Optional[Path]:
        """
        保存数据到文件（子类必须实现）
        
        Args:
            data: 要保存的数据
            
        Returns:
            Optional[Path]: 保存的文件路径
        """
        pass
    
    def execute(self, **kwargs) -> Optional[Path]:
        """
        执行API调用流程
        
        Args:
            **kwargs: 模块特定参数
            
        Returns:
            Optional[Path]: 保存的文件路径
        """
        try:
            logger.info(f"开始执行{self.module_name}API调用流程")
            
            # 1. 获取数据
            data = self.fetch_data(**kwargs)
            if data is None:
                logger.error("数据获取失败")
                return None
            
            # 2. 保存数据
            file_path = self.save_data(data)
            
            if file_path:
                logger.info(f"{self.module_name}执行成功: {file_path}")
            else:
                logger.error(f"{self.module_name}数据保存失败")
            
            return file_path
            
        except Exception as e:
            logger.error(f"{self.module_name}执行异常: {str(e)}")
            return None
