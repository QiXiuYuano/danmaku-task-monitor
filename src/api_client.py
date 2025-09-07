# API客户端
import requests
import logging
from typing import List, Dict, Optional
from .config import API_BASE_URL, API_KEY
from .utils import setup_logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
from datetime import datetime

# 禁用不安全的SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = setup_logger("api_client")

class DanmakuAPIClient:
    """弹幕服务API客户端"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.api_key = API_KEY
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def get_completed_tasks(self) -> List[Dict]:
        """
        获取已完成的任务
        """
        try:            
            # 构造请求URL
            url = f"{self.base_url}/api/control/tasks"
            params = {
                "status": "completed",
                "api_key": self.api_key
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = self.session.get(url, params=params, headers=headers, verify=False)
            response.raise_for_status()
            
            data = response.json()
            tasks = data.get("tasks", [])
            
            logger.info(f"获取到 {len(tasks)} 个完成的任务")
            return tasks
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取任务列表时发生错误: {e}")
            return []
        except Exception as e:
            logger.error(f"解析任务列表时发生错误: {e}")
            return []
