"""
文件工具函数
"""

from pathlib import Path
from typing import Optional, List
from datetime import datetime
from config.settings import FILE_NAME_DATE_FORMAT


def generate_timestamped_filename(module_name: str, extension: str = "xlsx") -> str:
    """
    生成带时间戳的文件名
    
    Args:
        module_name: 模块名称
        extension: 文件扩展名
        
    Returns:
        格式化的文件名
    """
    timestamp = datetime.now().strftime(FILE_NAME_DATE_FORMAT)
    if not extension.startswith('.'):
        extension = '.' + extension
    return f"{module_name}_{timestamp}{extension}"


def ensure_dir_exists(directory: Path) -> None:
    """
    确保目录存在，不存在则创建
    
    Args:
        directory: 目录路径
    """
    directory.mkdir(parents=True, exist_ok=True)


def find_latest_file(directory: Path, pattern: str = "*") -> Optional[Path]:
    """
    在指定目录中查找最新的文件
    
    Args:
        directory: 目录路径
        pattern: 文件匹配模式
        
    Returns:
        最新文件的路径，如果没有找到返回None
    """
    if not directory.exists():
        return None
    
    files = list(directory.glob(pattern))
    if not files:
        return None
    
    # 按修改时间排序，返回最新的
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    return latest_file


def cleanup_module_files(directory: Path, module_name: str, keep_latest: int = 1) -> int:
    """
    清理指定模块的历史文件，保留最新的几个文件
    
    Args:
        directory: 目录路径
        module_name: 模块名称
        keep_latest: 保留最新文件的数量，默认保留1个
        
    Returns:
        删除的文件数量
    """
    if not directory.exists():
        return 0
    
    # 查找该模块的所有文件
    pattern = f"{module_name}_*.xlsx"
    files = list(directory.glob(pattern))
    
    if len(files) <= keep_latest:
        return 0
    
    # 按修改时间排序，最新的在前
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # 删除多余的文件
    files_to_delete = files[keep_latest:]
    deleted_count = 0
    
    for file_path in files_to_delete:
        try:
            file_path.unlink()
            deleted_count += 1
            print(f"[删除] 删除历史文件: {file_path.name}")
        except Exception as e:
            print(f"[错误] 删除文件失败 {file_path.name}: {str(e)}")
    
    return deleted_count


def get_module_files(directory: Path, module_name: str) -> List[Path]:
    """
    获取指定模块的所有文件列表
    
    Args:
        directory: 目录路径
        module_name: 模块名称
        
    Returns:
        文件路径列表，按时间倒序排列
    """
    if not directory.exists():
        return []
    
    pattern = f"{module_name}_*.xlsx"
    files = list(directory.glob(pattern))
    
    # 按修改时间排序，最新的在前
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    return files
