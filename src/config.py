# 配置文件
import os
from datetime import datetime, timedelta

# 加载.env文件中的环境变量
from dotenv import load_dotenv
load_dotenv()

# 时区设置，默认为Asia/Shanghai（东八区）
TZ = os.getenv("TZ", "Asia/Shanghai")

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
# 时间窗口缓冲(秒)，默认60秒(1分钟)
TIME_WINDOW_BUFFER = int(os.getenv("TIME_WINDOW_BUFFER", 60))
# 每次最多处理的任务数，默认50个
MAX_TASKS_TO_PROCESS = int(os.getenv("MAX_TASKS_TO_PROCESS", 50))

# 状态文件路径
STATE_FILE_PATH = os.getenv("STATE_FILE_PATH", "data/monitor_state.json")

# 日志级别，默认为 INFO
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# 日志文件路径
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/monitor.log")
# 日志文件保留天数，默认为7天
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 7))

# 已处理任务ID列表最大大小，默认为1000
MAX_PROCESSED_TASKS = int(os.getenv("MAX_PROCESSED_TASKS", 1000))
# 状态文件最大保留天数，默认为7天
STATE_FILE_MAX_AGE = int(os.getenv("STATE_FILE_MAX_AGE", 7))

# Telegram通知消息模板
TELEGRAM_MESSAGE_TEMPLATE = os.getenv("TELEGRAM_MESSAGE_TEMPLATE", """
✅ **任务完成通知**

🆔 **任务ID:** `{task_id}`

📋 **任务标题:** {title}

📝 **任务描述:** {description}

⏰ **完成时间:** {created_at}
""")