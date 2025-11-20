"""
组织商品档案模块
"""

from pathlib import Path
from typing import Dict, Any

from core.base_module import ExportBasedModule
from config.api_config import EXPORT_ENDPOINTS
from config.params_config import ORG_PRODUCT_INFO_EXPORT_PARAMS
from utils.logger import get_logger

logger = get_logger(__name__)


class OrgProductInfoModule(ExportBasedModule):
    """组织商品档案数据采集模块"""

    def __init__(self) -> None:
        super().__init__()
        self.export_url = EXPORT_ENDPOINTS["org_product_info"]
        self.module_display_name = "组织商品档案"

    def get_export_config(self, **kwargs: Any) -> Dict[str, Any]:
        """提供导出配置"""
        if kwargs:
            logger.info(f"忽略额外参数: {list(kwargs.keys())}")

        return {
            "export_url": self.export_url,
            "export_params": ORG_PRODUCT_INFO_EXPORT_PARAMS,
            "module_name": self.module_display_name,
        }

    def execute(self, **kwargs) -> Path | None:
        return super().execute(**kwargs)