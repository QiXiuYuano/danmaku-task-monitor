# 工具函数
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from .config import STATE_FILE_PATH, LOG_BACKUP_COUNT, LOG_FILE_PATH, TZ
import logging.handlers

def get_current_time_iso():
    """获取当前时间的ISO格式字符串（不包含时区信息）"""
    if TZ == 'Asia/Shanghai':
        current_time = datetime.now(timezone(timedelta(hours=8)))
    else:
        current_time = datetime.now().astimezone()
    
    return current_time.replace(tzinfo=None).isoformat()

def setup_logger(name, level=logging.INFO):
    """设置日志记录器"""
    # 创建一个使用指定时区的格式化器类
    class TimeZoneFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            if TZ == 'Asia/Shanghai':
                dt = datetime.fromtimestamp(record.created, tz=timezone(timedelta(hours=8)))
            else:
                dt = datetime.fromtimestamp(record.created).astimezone()
            if datefmt:
                return dt.strftime(datefmt)
            else:
                return dt.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    
    formatter = TimeZoneFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 控制台处理器
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
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def load_state():
    """加载状态文件"""
    try:
        if os.path.exists(STATE_FILE_PATH):
            with open(STATE_FILE_PATH, 'r', encoding='utf-8') as f:
                state = json.load(f)
                if "last_check_time" in state:
                    last_check_str = state["last_check_time"]
                    try:
                        datetime.fromisoformat(last_check_str)
                    except ValueError:
                        state["last_check_time"] = get_current_time_iso()

                if "initial_check_time" in state:
                    initial_check_time_str = state["initial_check_time"]
                    try:
                        datetime.fromisoformat(initial_check_time_str)
                    except ValueError:
                        state["initial_check_time"] = get_current_time_iso()
                        
                return state
    except FileNotFoundError: 
        pass
    except Exception as e:
        logger = logging.getLogger("utils")
        logger.warning(f"加载状态文件时出错: {e}")
    
    initial_check_time = get_current_time_iso()
    return {
        "initial_check_time": initial_check_time,
        "last_check_time": initial_check_time,
        "processed_tasks": []
    }

def save_state(state):
    """保存状态文件"""
    try:
        with open(STATE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"保存状态文件失败: {e}")

def is_task_processed(task_id, processed_tasks):
    """检查任务是否已处理"""
    return task_id in processed_tasks

def add_processed_task(task_id, processed_tasks, max_size=1000):
    """添加已处理任务ID，保持列表大小限制"""
    if task_id not in processed_tasks:
        processed_tasks.append(task_id)
        if len(processed_tasks) > max_size:
            processed_tasks = processed_tasks[-50:]
    return processed_tasks