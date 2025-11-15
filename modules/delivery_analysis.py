"""配送分析模块
用于查询和采集配送分析数据，支持多参数模板和覆盖"""

from pathlib import Path
from typing import Dict, Any, Optional

from core.base_module import ExportBasedModule
from config.api_config import EXPORT_ENDPOINTS
from config.params_config import get_delivery_analysis_params
from utils.logger import get_logger

logger = get_logger(__name__)


TEMPLATE_FILE_LABELS = {
    "order_delivery": "订单配送",
}


class DeliveryAnalysisModule(ExportBasedModule):
    """配送分析数据采集模块"""

    def __init__(self):
        super().__init__()
        self.export_url = EXPORT_ENDPOINTS["delivery_analysis"]
        self.module_display_name = "配送分析"

    def get_export_config(self, **kwargs) -> Dict[str, Any]:
        """获取导出配置，支持模板、覆盖及完全自定义"""
        template_name = kwargs.pop("template_name", "order_delivery")
        custom_params = kwargs.pop("custom_params", None)
        file_label_override = kwargs.pop("file_label", None)

        if custom_params:
            logger.info("配送分析使用完全自定义参数")
            export_params = custom_params.copy()
        else:
            logger.info(f"配送分析使用模板: {template_name}")
            export_params = get_delivery_analysis_params(template_name)
            if kwargs:
                logger.info(f"配送分析参数覆盖: {list(kwargs.keys())}")
                export_params.update(kwargs)

        file_label = file_label_override
        if not file_label and custom_params:
            file_label = custom_params.get("file_label")
        if not file_label:
            file_label = TEMPLATE_FILE_LABELS.get(template_name)

        file_name_prefix = "配送分析"
        if file_label:
            file_name_prefix = f"{file_name_prefix}_{file_label}"

        logger.info(f"配送分析最终导出参数: {list(export_params.keys())}")
        logger.info(f"配送分析文件名前缀: {file_name_prefix}")

        return {
            "export_url": self.export_url,
            "export_params": export_params,
            "module_name": self.module_display_name,
            "file_name_prefix": file_name_prefix,
        }


def run(template_name: str = "order_delivery") -> Optional[Path]:
    """兼容旧流程的模块入口"""
    logger.info(f"启动配送分析模块，模板: {template_name}")
    module = DeliveryAnalysisModule()
    return module.execute(template_name=template_name)
