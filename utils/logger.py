"""
日志工具
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import LOGS_DIR, LOG_DATE_FORMAT


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称（通常使用 __name__）
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)  # 设置为最低级别，让handler控制输出
    
    # 控制台处理器 - 只显示错误
    console_formatter = logging.Formatter("❌ %(message)s")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR)  # 控制台只显示错误
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 记录所有详细信息
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        LOG_DATE_FORMAT
    )
    log_file = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger
