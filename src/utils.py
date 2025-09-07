# 工具函数
import json
import logging
import os
from datetime import datetime, timedelta
from .config import STATE_FILE_PATH, STATE_FILE_MAX_AGE, LOG_BACKUP_COUNT, LOG_FILE_PATH
import logging.handlers

def setup_logger(name, level=logging.INFO):
    """设置日志记录器"""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
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
        # 检查状态文件是否存在且不超过指定天数
        if os.path.exists(STATE_FILE_PATH):
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(STATE_FILE_PATH))
            if file_age > timedelta(days=STATE_FILE_MAX_AGE):
                logger = logging.getLogger("utils")
                logger.info(f"状态文件超过{STATE_FILE_MAX_AGE}天，进行清理")
                os.remove(STATE_FILE_PATH)
                raise FileNotFoundError("状态文件已清理")
        
        with open(STATE_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 如果状态文件不存在，返回默认状态
        return {
            "last_check_time": None,
            "processed_tasks": []
        }
    except Exception as e:
        raise Exception(f"加载状态文件失败: {e}")

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
        # 限制已处理任务列表大小，避免无限增长
        if len(processed_tasks) > max_size:
            processed_tasks = processed_tasks[-max_size:]
    return processed_tasks