"""
文件下载处理器
"""

import os
from pathlib import Path
from typing import Optional
from core.request_handler import RequestHandler
from config.settings import DOWNLOADS_DIR, AUTO_CLEANUP_FILES, KEEP_LATEST_FILES
from utils.logger import get_logger
from utils.file_utils import generate_timestamped_filename, ensure_dir_exists, cleanup_module_files, get_module_files

logger = get_logger(__name__)


class DownloadHandler:
    """处理文件下载逻辑"""
    
    def __init__(self):
        self.request_handler = RequestHandler()
    
    def download_file(self, url: str, module_name: str, 
                     save_dir: Optional[Path] = None) -> Optional[Path]:
        """
        从URL下载文件（支持阿里云OSS直接下载）
        
        Args:
            url: 文件下载URL（阿里云OSS地址）
            module_name: 模块名称（用于文件命名）
            save_dir: 保存目录，默认为DOWNLOADS_DIR
            
        Returns:
            保存的文件路径，失败返回None
        """
        if not url:
            logger.error("下载URL为空")
            return None
        
        logger.info(f"开始下载文件: {url}")
        
        # 确定保存目录
        if save_dir is None:
            save_dir = DOWNLOADS_DIR
        ensure_dir_exists(save_dir)
        
        # 从URL提取文件名或生成新文件名
        original_filename = url.split("/")[-1].split("?")[0]  # 去除查询参数
        file_extension = os.path.splitext(original_filename)[1] or ".xlsx"
        
        # 生成本地文件名
        local_filename = generate_timestamped_filename(module_name, file_extension.lstrip('.'))
        save_path = save_dir / local_filename
        
        try:
            # 发送GET请求下载文件（阿里云OSS不需要特殊headers）
            response = self.request_handler.get(url)
            
            if not response:
                logger.error("下载请求失败")
                return None
            
            # 写入文件
            logger.info(f"保存文件到: {save_path}")
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(save_path)
            logger.info(f"文件下载成功: {save_path} (大小: {file_size / 1024:.2f} KB)")
            return save_path
            
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            # 清理失败的文件
            if save_path.exists():
                save_path.unlink()
            return None
    
    def download_from_export(
        self,
        download_url: str,
        module_name: str,
        file_name_prefix: Optional[str] = None,
    ) -> Optional[Path]:
        """
        从导出任务获取的URL下载文件
        
        Args:
            download_url: 导出任务返回的下载URL
            module_name: 模块名称
            
        Returns:
            保存的文件路径，失败返回None
        """
        logger.info(f"开始下载文件: {download_url}")
        
        # 确保下载目录存在
        ensure_dir_exists(DOWNLOADS_DIR)
        
        filename_base = file_name_prefix or module_name

        # 检查并清理历史文件（如果启用自动清理）
        if AUTO_CLEANUP_FILES:
            existing_files = get_module_files(DOWNLOADS_DIR, filename_base)
            if existing_files:
                logger.info(f"发现 {len(existing_files)} 个历史文件")
                print(f"[发现] {len(existing_files)} 个 {filename_base} 历史文件:")
            for i, file_path in enumerate(existing_files, 1):
                file_size = file_path.stat().st_size / 1024
                print(f"   {i}. {file_path.name} ({file_size:.2f} KB)")
            
            # 清理历史文件
            deleted_count = cleanup_module_files(
                DOWNLOADS_DIR, filename_base, keep_latest=KEEP_LATEST_FILES
            )
            if deleted_count > 0:
                print(f"[清理] 已清理 {deleted_count} 个历史文件，保留最新 {KEEP_LATEST_FILES} 个")
        
        # 下载新文件
        result = self.download_file(download_url, filename_base)

        if result:
            file_size_kb = result.stat().st_size / 1024
            print(f"[完成] 新文件下载完成: {result.name} ({file_size_kb:.2f} KB)")
        
        return result
