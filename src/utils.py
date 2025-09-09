# 工具函数
import json
import logging
import os
from datetime import datetime
import logging.handlers
from .config import STATE_FILE_PATH, LOG_BACKUP_COUNT, LOG_FILE_PATH, TZINFO


def get_current_time_iso() -> str:
    """获取当前时区下的ISO格式时间字符串"""
    return datetime.now(TZINFO).replace(tzinfo=None, microsecond=0).isoformat()

def setup_logger(name, level=logging.INFO):
    """设置日志记录器"""
    class TimeZoneFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            dt = datetime.fromtimestamp(record.created, tz=TZINFO)
            return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

    formatter = TimeZoneFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # formatter = TimeZoneFormatter('%(asctime)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 文件处理器，每天轮转一次，保留指定天数的日志
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_FILE_PATH,
        when='midnight',
        interval=1,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

def load_state(round_no=None):
    """加载状态文件"""
    logger = logging.getLogger("utils")
    log_prefix = f"[监控轮次 {round_no}] " if round_no is not None else ""
    try:
        if os.path.exists(STATE_FILE_PATH):
            with open(STATE_FILE_PATH, 'r', encoding='utf-8') as f:
                state = json.load(f)
                if "initial_check_time" in state:
                    try:
                        datetime.fromisoformat(state["initial_check_time"])
                    except ValueError:
                        state["initial_check_time"] = get_current_time_iso()

                return state
    except Exception as e:
        logger.warning(f"{log_prefix}加载状态文件时出错: {e}")

    initial_check_time = get_current_time_iso()
    return {
        "initial_check_time": initial_check_time,
        "processed_tasks": []
    }

def save_state(state, round_no=None):
    """保存状态文件"""
    log_prefix = f"[监控轮次 {round_no}] " if round_no is not None else ""
    try:
        with open(STATE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"{log_prefix}保存状态文件失败: {e}")
