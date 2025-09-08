# 通知模块
import logging
import requests
from typing import Dict
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_MESSAGE_TEMPLATE
from .utils import setup_logger

logger = setup_logger("notifier")

class TelegramNotifier:
    """Telegram通知器"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.message_template = TELEGRAM_MESSAGE_TEMPLATE
        
    def send_task_completion_notification(self, task: Dict) -> bool:
        """发送任务完成通知"""
        try:
            # 构造通知消息
            message = self._format_task_message(task)
            
            # 发送消息
            response = requests.post(
                f"{self.base_url}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("ok"):
                logger.info(f"任务通知发送成功: {task['taskId']}")
                return True
            else:
                logger.error(f"Telegram API返回错误: {result.get('description')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"发送Telegram通知失败: {e}")
            return False
        except Exception as e:
            logger.error(f"处理任务通知时发生错误: {e}")
            return False
    
    def _format_task_message(self, task: Dict) -> str:
        """格式化任务消息"""
        # 使用配置文件中的模板格式化消息
        message = self.message_template.format(
            task_id=task.get('taskId', '未知ID'),
            title=task.get('title', '未知任务'),
            description=task.get('description', '无描述'),
            status=task.get('status', '未知状态'),
            progress=task.get('progress', '未知进度'),
            created_at=task.get('createdAt', '未知时间')
        )
        
        return message.strip()