"""
HTTP请求处理器
"""

import requests
import time
from typing import Dict, Any, Optional
from config.headers_config import HEADERS
from config.settings import REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY
from utils.logger import get_logger

logger = get_logger(__name__)


class RequestHandler:
    """封装HTTP请求逻辑"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def post(self, url: str, json_data: Dict[str, Any], 
             timeout: int = REQUEST_TIMEOUT) -> Optional[Dict[str, Any]]:
        """
        发送POST请求
        
        Args:
            url: 请求URL
            json_data: JSON请求体
            timeout: 超时时间
            
        Returns:
            响应JSON数据，失败返回None
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"发送POST请求: {url} (尝试 {attempt}/{MAX_RETRIES})")
                response = self.session.post(url, json=json_data, timeout=timeout)
                response.raise_for_status()
                
                result = response.json()
                
                # 检查业务状态码
                if result.get("code") == 0:
                    logger.info(f"请求成功: {url}")
                    return result
                else:
                    logger.error(f"业务错误: {result.get('msg', '未知错误')}")
                    return result
                    
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (尝试 {attempt}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常: {str(e)} (尝试 {attempt}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    
            except Exception as e:
                logger.error(f"未知错误: {str(e)}")
                break
        
        logger.error(f"请求失败，已达最大重试次数: {url}")
        return None
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None,
            timeout: int = REQUEST_TIMEOUT) -> Optional[requests.Response]:
        """
        发送GET请求（用于文件下载）
        
        Args:
            url: 请求URL
            params: 查询参数
            timeout: 超时时间
            
        Returns:
            响应对象，失败返回None
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(f"发送GET请求: {url} (尝试 {attempt}/{MAX_RETRIES})")
                response = self.session.get(url, params=params, timeout=timeout, stream=True)
                response.raise_for_status()
                logger.info(f"GET请求成功: {url}")
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (尝试 {attempt}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常: {str(e)} (尝试 {attempt}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    
            except Exception as e:
                logger.error(f"未知错误: {str(e)}")
                break
        
        logger.error(f"GET请求失败，已达最大重试次数: {url}")
        return None
