"""
汇总配置（全局设置）
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 存储路径配置
STORAGE_ROOT = PROJECT_ROOT / "storage"
DOWNLOADS_DIR = STORAGE_ROOT / "downloads"
PROCESSED_DIR = STORAGE_ROOT / "processed"
LOGS_DIR = STORAGE_ROOT / "logs"
REFERENCE_DIR = STORAGE_ROOT / "reference"  # 架构信息表存储目录

# 确保目录存在
for directory in [DOWNLOADS_DIR, PROCESSED_DIR, LOGS_DIR, REFERENCE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 请求配置
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
MAX_RETRIES = 3       # 最大重试次数
RETRY_DELAY = 2       # 重试延迟（秒）

# 导出任务轮询配置
EXPORT_POLL_INTERVAL = 15   # 轮询间隔（秒）- 优化为15秒，更快响应
EXPORT_MAX_WAIT_TIME = 300  # 最大等待时间（秒）- 给足够时间让任务完成
EXPORT_INITIAL_WAIT = 20    # 初始等待时间（秒）- 等待任务启动和记录生成

# 日志配置
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 文件命名配置
FILE_NAME_DATE_FORMAT = "%Y%m%d_%H%M%S"

# 文件管理配置
# KEEP_LATEST_FILES = 0 → 删除所有历史文件
# KEEP_LATEST_FILES = 1 → 保留1个最新文件
# KEEP_LATEST_FILES = 3 → 保留3个最新文件
# AUTO_CLEANUP_FILES = False → 禁用自动清理
AUTO_CLEANUP_FILES = True    # 是否自动清理历史文件
KEEP_LATEST_FILES = 0        # 保留最新文件数量（0表示删除所有历史文件）
