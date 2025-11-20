"""
导出任务处理器
"""

import time
from typing import Optional, Dict, Any
from core.request_handler import RequestHandler
from config.api_config import DOWNLOAD_ENDPOINT
from config.params_config import get_download_params
from config.settings import EXPORT_POLL_INTERVAL, EXPORT_MAX_WAIT_TIME, EXPORT_INITIAL_WAIT
from utils.logger import get_logger

logger = get_logger(__name__)


class ExportHandler:
    """处理导出任务的提交和状态查询"""
    
    def __init__(self):
        self.request_handler = RequestHandler()
    
    def submit_export_task(self, export_url: str, export_params: Dict[str, Any]) -> bool:
        """
        提交导出任务（只提交一次，不重试）
        
        Args:
            export_url: 导出接口URL
            export_params: 导出参数
            
        Returns:
            是否提交成功
        """
        logger.info(f"提交导出任务: {export_url}")
        logger.debug(f"导出参数: {export_params}")
        
        # 使用单次请求，不重试（避免重复提交）
        result = self._single_post_request(export_url, export_params)
        
        if result and result.get("code") == 0:
            logger.info("导出任务提交成功")
            return True
        elif result and result.get("code") == 2006:
            # 正在处理中，说明任务已存在，也算成功
            logger.info("导出任务已在处理中，无需重复提交")
            return True
        elif result is None:
            # 请求超时，但任务可能已在后台启动，继续等待检查
            logger.warning("导出接口超时，但任务可能已在后台启动，继续等待检查...")
            return True
        else:
            logger.error(f"导出任务提交失败: {result}")
            return False
    
    def _single_post_request(self, url: str, json_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        发送单次POST请求（不重试）
        """
        try:
            logger.info(f"发送POST请求: {url}")
            response = self.request_handler.session.post(url, json=json_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"请求成功: {url}")
            return result
            
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            return None
    
    def wait_for_export_completion(self, module_name: str, 
                                   max_wait_time: int = EXPORT_MAX_WAIT_TIME) -> Optional[str]:
        """
        轮询等待导出任务完成并获取下载URL
        
        Args:
            module_name: 模块名称（用于匹配任务）
            max_wait_time: 最大等待时间（秒）
            
        Returns:
            文件下载URL，失败返回None
        """
        logger.info(f"开始轮询导出任务状态，模块: {module_name}")
        
        start_time = time.time()
        poll_count = 0
        
        while time.time() - start_time < max_wait_time:
            poll_count += 1
            logger.info(f"第 {poll_count} 次轮询...")
            
            # 获取下载任务列表
            download_params = get_download_params()
            result = self.request_handler.post(DOWNLOAD_ENDPOINT, download_params)
            
            if not result or result.get("code") != 0:
                logger.warning(f"获取任务列表失败，等待 {EXPORT_POLL_INTERVAL} 秒后重试")
                time.sleep(EXPORT_POLL_INTERVAL)
                continue
            
            # 解析任务列表
            content = result.get("data", {}).get("content", [])
            
            if not content:
                logger.warning("任务列表为空，等待后重试")
                time.sleep(EXPORT_POLL_INTERVAL)
                continue
            
            # 查找匹配的任务 - 按创建时间排序，获取最新的
            matching_tasks = []
            
            for task in content:
                task_name = task.get("name", "")
                task_module = task.get("module_name", "")
                state = task.get("state")
                schedule = task.get("schedule", 0)
                create_time = task.get("create_time", "")
                
                # 匹配模块名称
                if module_name in task_name or module_name in task_module:
                    matching_tasks.append({
                        "task": task,
                        "name": task_name,
                        "state": state,
                        "schedule": schedule,
                        "create_time": create_time,
                        "url": task.get("url", "")
                    })
            
            if not matching_tasks:
                logger.info("未找到匹配的任务（过滤掉历史任务后为空），等待后重试")
                time.sleep(EXPORT_POLL_INTERVAL)
                continue
            
            # 按创建时间排序，最新的在前面（假设content已经按时间排序，第一个就是最新的）
            latest_task = matching_tasks[0]
            
            logger.info(f"找到匹配任务: {latest_task['name']}, 状态: {latest_task['state']}, "
                       f"进度: {latest_task['schedule']}%, 创建时间: {latest_task['create_time']}")
            
            # state=1 且 schedule=100 表示完成
            if latest_task['state'] == 1 and latest_task['schedule'] == 100:
                url = latest_task['url']
                if url:
                    logger.info(f"导出任务完成，下载URL: {url}")
                    return url
                else:
                    logger.error("任务完成但未找到下载URL")
                    return None
            else:
                logger.info(f"任务进行中，进度: {latest_task['schedule']}%")
                # 继续轮询
            
            # 等待后继续轮询
            time.sleep(EXPORT_POLL_INTERVAL)
        
        logger.error(f"等待超时（{max_wait_time}秒），导出任务未完成")
        return None
    
    def export_and_get_url(self, export_url: str, export_params: Dict[str, Any], 
                          module_name: str) -> Optional[str]:
        """
        提交导出任务并等待完成，返回下载URL
        
        Args:
            export_url: 导出接口URL
            export_params: 导出参数
            module_name: 模块名称
            
        Returns:
            文件下载URL，失败返回None
        """
        # 记录开始时间，用于判断是否是本次导出的任务
        import datetime
        start_time = datetime.datetime.now()
        logger.info(f"开始导出任务，开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 提交导出任务
        if not self.submit_export_task(export_url, export_params):
            return None
        
        # 2. 等待初始时间让导出任务处理和记录生成
        logger.info(f"等待导出任务处理和记录生成，预计需要{EXPORT_INITIAL_WAIT}秒...")
        time.sleep(EXPORT_INITIAL_WAIT)  # 等待配置的初始时间让任务充分处理并生成记录
        
        # 3. 开始轮询获取结果
        download_url = self.wait_for_export_completion_with_time(module_name, start_time)
        return download_url
    
    def wait_for_export_completion_with_time(self, module_name: str, start_time, 
                                           max_wait_time: int = EXPORT_MAX_WAIT_TIME) -> Optional[str]:
        """
        轮询等待导出任务完成并获取下载URL（带时间判断）
        
        Args:
            module_name: 模块名称（用于匹配任务）
            start_time: 导出开始时间
            max_wait_time: 最大等待时间（秒）
            
        Returns:
            文件下载URL，失败返回None
        """
        logger.info(f"开始轮询导出任务状态，模块: {module_name}")
        
        poll_start_time = time.time()
        poll_count = 0
        
        while time.time() - poll_start_time < max_wait_time:
            poll_count += 1
            logger.info(f"第 {poll_count} 次轮询...")
            
            # 获取下载任务列表
            download_params = get_download_params()
            result = self.request_handler.post(DOWNLOAD_ENDPOINT, download_params)
            
            if not result or result.get("code") != 0:
                logger.warning(f"获取任务列表失败，等待 {EXPORT_POLL_INTERVAL} 秒后重试")
                time.sleep(EXPORT_POLL_INTERVAL)
                continue
            
            # 解析任务列表
            content = result.get("data", {}).get("content", [])
            
            if not content:
                logger.warning("任务列表为空，等待后重试")
                time.sleep(EXPORT_POLL_INTERVAL)
                continue
            
            # 查找匹配的任务 - 只考虑开始时间之后创建的任务
            matching_tasks = []
            
            for task in content:
                task_name = task.get("name", "")
                task_module = task.get("module_name", "")
                state = task.get("state")
                schedule = task.get("schedule", 0)
                create_time_str = task.get("create_time", "")
                
                # 匹配模块名称
                if module_name in task_name or module_name in task_module:
                    # 解析创建时间
                    try:
                        import datetime
                        create_time = datetime.datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S")
                        
                        # 只考虑开始时间之后创建的任务（允许5秒误差）
                        time_diff = (create_time - start_time).total_seconds()
                        if time_diff >= -5:  # 允许少量时间差，避免匹配到历史任务
                            matching_tasks.append({
                                "task": task,
                                "name": task_name,
                                "state": state,
                                "schedule": schedule,
                                "create_time": create_time_str,
                                "url": task.get("url", ""),
                                "time_diff": time_diff
                            })
                    except ValueError:
                        # 时间格式解析失败，跳过时间判断
                        matching_tasks.append({
                            "task": task,
                            "name": task_name,
                            "state": state,
                            "schedule": schedule,
                            "create_time": create_time_str,
                            "url": task.get("url", ""),
                            "time_diff": 0
                        })
            
            if not matching_tasks:
                logger.info("未找到匹配的任务，可能任务尚未开始")
                time.sleep(EXPORT_POLL_INTERVAL)
                continue
            
            # 按时间差排序，选择最接近开始时间的任务
            matching_tasks.sort(key=lambda x: abs(x['time_diff']))
            latest_task = matching_tasks[0]
            
            logger.info(f"找到匹配任务: {latest_task['name']}, 状态: {latest_task['state']}, "
                       f"进度: {latest_task['schedule']}%, 创建时间: {latest_task['create_time']}")
            
            # state=1 且 schedule=100 表示完成
            if latest_task['state'] == 1 and latest_task['schedule'] == 100:
                url = latest_task['url']
                if url:
                    logger.info(f"导出任务完成，下载URL: {url}")
                    return url
                else:
                    logger.error("任务完成但未找到下载URL")
                    return None
            else:
                logger.info(f"任务进行中，进度: {latest_task['schedule']}%")
                # 继续轮询
            
            # 等待后继续轮询
            time.sleep(EXPORT_POLL_INTERVAL)
        
        logger.error(f"等待超时（{max_wait_time}秒），导出任务未完成")
        return None
