# 尝试设置时区（仅在支持的平台上）
try:
    import os
    from .config import TZ
    os.environ['TZ'] = TZ
    import time
    time.tzset()
except (ImportError, AttributeError):
    # Windows平台不支持tzset，忽略时区设置
    pass

import time
from datetime import datetime, timedelta
from typing import List, Dict
from .config import CHECK_INTERVAL, MAX_TASKS_TO_PROCESS, TZ
from .api_client import DanmakuAPIClient
from .utils import setup_logger, load_state, save_state, is_task_processed, add_processed_task, get_current_time_iso
from .notifier import TelegramNotifier

logger = setup_logger("monitor")

class TaskMonitor:
    """任务监控器"""
    
    def __init__(self):
        self.api_client = DanmakuAPIClient()
        self.notifier = TelegramNotifier()
        self.state = load_state()
        self.initial_check_time_str = self.state.get("initial_check_time")
        self.initial_check_time = datetime.fromisoformat(self.initial_check_time_str)
        # 在内存中只创建一个包含最近50个任务ID的set用于快速查找
        processed_tasks = self.state.get("processed_tasks", [])
        self.processed_task_ids_set = set(processed_tasks[-50:] if len(processed_tasks) > 50 else processed_tasks)

    def _filter_new_tasks(self, tasks: List[Dict], initial_check_time: datetime) -> List[Dict]:
        """过滤出新的任务（基于任务ID匹配）"""
        new_tasks = []
        
        # 只处理最近的MAX_TASKS_TO_PROCESS个任务
        tasks_to_process = tasks[:MAX_TASKS_TO_PROCESS] if len(tasks) > MAX_TASKS_TO_PROCESS else tasks
        
        logger.info(f"从{len(tasks)}个任务中筛选出{len(tasks_to_process)}个最近的任务进行处理")
        
        # 遍历筛选后的任务列表
        for task in tasks_to_process:
            try:
                task_created_time = datetime.fromisoformat(task["createdAt"])

                # 确保initial_check_time也不包含时区信息以进行比较
                comparison_initial_check_time = initial_check_time.replace(tzinfo=None) if initial_check_time.tzinfo is not None else initial_check_time

                if task_created_time < comparison_initial_check_time:
                    continue
                if task["taskId"] in self.processed_task_ids_set:
                    continue
                    
                # 如果在内存set中未找到，再检查状态文件中最近的50个任务ID（较少发生的情况）
                processed_tasks = self.state["processed_tasks"]
                recent_processed_tasks = processed_tasks[-50:] if len(processed_tasks) > 50 else processed_tasks
                if task["taskId"] in recent_processed_tasks:
                    continue
                    
                new_tasks.append(task)
            except ValueError as e:
                logger.warning(f"任务 {task.get('taskId', 'unknown')} 的创建时间格式不正确: {e}")
                continue
                
        logger.info(f"筛选出 {len(new_tasks)} 个新任务")
        return new_tasks
    
    def _process_new_tasks(self, new_tasks: List[Dict]):
        """处理新任务"""
        for task in new_tasks:
            try:
                logger.info(f"处理新任务: {task['taskId']} - {task['title']}")
                # 发送Telegram通知
                self.notifier.send_task_completion_notification(task)
                # 添加到已处理任务列表
                self.state["processed_tasks"] = add_processed_task(
                    task["taskId"], 
                    self.state["processed_tasks"]
                )
                # 同步更新内存中的set（只保留最近的50个）
                if len(self.processed_task_ids_set) >= 50:
                    # 移除一个旧的任务ID以保持set大小
                    oldest_id = next(iter(self.processed_task_ids_set))
                    self.processed_task_ids_set.discard(oldest_id)
                self.processed_task_ids_set.add(task["taskId"])
            except Exception as e:
                logger.error(f"处理任务 {task['taskId']} 时出错: {e}")
    
    def run(self):
        """运行监控器"""
        logger.info("任务监控器启动")
        while True:
            try:
                # 获取上次检查时间
                last_check_time_str = self.state.get("last_check_time")
                if last_check_time_str:
                    last_check_time = datetime.fromisoformat(last_check_time_str)
                    logger.info(f"上次检查时间: {last_check_time.isoformat()}")
                else:
                    logger.info("上次检查时间: 无")
                
                # 获取已完成的任务列表
                tasks = self.api_client.get_completed_tasks()
                if tasks is None:
                    logger.error("获取任务列表失败，跳过本次检查")
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                # 过滤出新的任务
                new_tasks = self._filter_new_tasks(tasks, self.initial_check_time)
                
                # 处理新任务
                if new_tasks:
                    self._process_new_tasks(new_tasks)
                else:
                    logger.info("没有发现新任务")

                # 更新检查时间
                current_time = datetime.fromisoformat(get_current_time_iso())
                self.state["last_check_time"] = current_time.isoformat()
                
                # 保存状态
                try:
                    save_state(self.state)
                    logger.debug(f"状态文件已保存，当前检查时间: {current_time.isoformat()}")
                except Exception as e:
                    logger.error(f"保存状态文件失败: {e}")
                
                logger.info(f"检查完成，等待 {CHECK_INTERVAL} 秒后进行下次检查")
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("收到中断信号，正在退出...")
                break
            except Exception as e:
                logger.error(f"监控过程中发生未预期的错误: {e}")
                time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor = TaskMonitor()
    monitor.run()