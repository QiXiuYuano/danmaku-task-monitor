# 配置文件
import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()

# 时区设置，默认为Asia/Shanghai
TZ = os.getenv("TZ", "Asia/Shanghai")
TZINFO = ZoneInfo(TZ)

# API配置
# 弹幕服务的API基础URL
API_BASE_URL = os.getenv("API_BASE_URL", "")
# 弹幕服务的API密钥
API_KEY = os.getenv("API_KEY", "")

# Telegram配置
# Telegram Bot的令牌
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# 接收通知的Telegram聊天ID
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# 监控检查间隔(秒)，默认60秒(1分钟)
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))
# 每次最多处理的任务数，默认20个
MAX_TASKS_TO_PROCESS = int(os.getenv("MAX_TASKS_TO_PROCESS", 20))
# 日志文件保留天数，默认为7天
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 7))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 状态文件路径
STATE_FILE_PATH = os.getenv("STATE_FILE_PATH", os.path.join(PROJECT_ROOT, "data/monitor_state.json"))
# 日志文件路径
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", os.path.join(PROJECT_ROOT, "logs/monitor.log"))

# Telegram通知消息模板
TELEGRAM_MESSAGE_TEMPLATE = os.getenv("TELEGRAM_MESSAGE_TEMPLATE", """
✅ *任务完成通知*

🆔 *任务ID:* `{task_id}`

📋 *任务标题:* {title}

📝 *任务描述:* {description}

⏰ *完成时间:* {created_at}
""")
