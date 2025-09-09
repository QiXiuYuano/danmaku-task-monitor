# API客户端
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import API_BASE_URL, API_KEY
from .utils import setup_logger

logger = setup_logger(__name__)

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
        
    def get_completed_tasks(self, round_no=None):
        """ 获取已完成的任务 """
        log_prefix = f"[监控轮次 {round_no}] " if round_no is not None else ""
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
            
            response = self.session.get(url, params=params, headers=headers, verify=True)
            response.raise_for_status()

            try:
                tasks = response.json()
            except ValueError:
                logger.error(f"{log_prefix}响应不是有效的 JSON: {response.text[:200]}...")
                return []

            logger.info(f"{log_prefix}从API接口获取任务列表成功，共 {len(tasks)} 个已完成任务")
            return tasks
            
        except requests.exceptions.RequestException as e:
            logger.error(f"{log_prefix}获取任务列表时发生错误: {e}")
            return []
        except Exception as e:
            logger.error(f"{log_prefix}解析任务列表时发生错误: {e}")
            return []
