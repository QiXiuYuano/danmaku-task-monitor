# 通知模块
import requests
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_MESSAGE_TEMPLATE
from .utils import setup_logger

logger = setup_logger(__name__)

def _escape_markdown_v2(text):
    """转义 MarkdownV2 特殊字符"""
    if not isinstance(text, str):
        text = str(text)
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in escape_chars else c for c in text)

class TelegramNotifier:
    """Telegram 通知器"""

    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.message_template = TELEGRAM_MESSAGE_TEMPLATE

    def send_task_completion_notification(self, task, round_no=None):
        """发送任务完成通知"""
        log_prefix = f"[监控轮次 {round_no}] " if round_no is not None else ""
        try:
            # 构造通知消息
            message = self._format_task_message(task)

            # 发送消息
            response = requests.post(
                f"{self.base_url}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "MarkdownV2"
                },
                timeout=10
            )

            response.raise_for_status()
            result = response.json()

            if result.get("ok"):
                logger.info(f"{log_prefix}任务通知发送成功: {task.get('taskId')}")
                return True
            else:
                logger.error(f"{log_prefix}Telegram API 返回错误: {result.get('description')}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"{log_prefix}发送 Telegram 通知失败: {e}")
            return False
        except Exception as e:
            logger.error(f"{log_prefix}处理任务通知时发生错误: {e}")
            return False

    def _format_task_message(self, task):
        """格式化任务消息并转义"""
        message = self.message_template.format(
            task_id=_escape_markdown_v2(task.get('taskId', '未知ID')),
            title=_escape_markdown_v2(task.get('title', '未知任务')),
            description=_escape_markdown_v2(task.get('description', '无描述')),
            created_at=_escape_markdown_v2(task.get('createdAt', '未知时间'))
        )
        return message.strip()
