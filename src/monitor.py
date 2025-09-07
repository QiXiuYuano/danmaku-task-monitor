# 任务监控器主程序
import time
import logging
# 尝试设置时区（仅在支持的平台上）
try:
    import os
    tz = os.environ.get('TZ')
    if tz:
        import time
        time.tzset()
except (ImportError, AttributeError):
    # Windows平台不支持tzset，忽略时区设置
    pass

from datetime import datetime, timedelta
from typing import List, Dict
from .config import CHECK_INTERVAL, TIME_WINDOW_BUFFER, MAX_TASKS_TO_PROCESS
from .api_client import DanmakuAPIClient
from .utils import setup_logger, load_state, save_state, is_task_processed, add_processed_task
from .notifier import TelegramNotifier

logger = setup_logger("monitor")

class TaskMonitor:
    """任务监控器"""
    
    def __init__(self):
        self.api_client = DanmakuAPIClient()
        self.notifier = TelegramNotifier()
        self.state = load_state()
        
    def _get_last_check_time(self) -> datetime:
        """获取上次检查时间"""
        last_check_str = self.state.get("last_check_time")
        if last_check_str:
            try:
                return datetime.fromisoformat(last_check_str)
            except ValueError:
                logger.warning("状态文件中的时间格式不正确，使用0.5小时前作为检查起点")
                return datetime.now() - timedelta(hours=0.5)
        else:
            logger.info("状态文件中没有上次检查时间，使用当前时间作为检查起点")
            return datetime.now()  # 修改这里，直接返回当前时间而不是1小时前

    def _filter_new_tasks(self, tasks: List[Dict], last_check_time: datetime) -> List[Dict]:
        """
        过滤出新的任务（在上次检查时间之后创建的）
        
        Args:
            tasks: 从API获取的完整任务列表
            last_check_time: 上次检查时间
            
        Returns:
            新的任务列表
        """
        new_tasks = []
        check_window_start = last_check_time - timedelta(seconds=TIME_WINDOW_BUFFER)
        
        # 只处理最近的MAX_TASKS_TO_PROCESS个任务
        # 由于任务列表是按时间倒序排列的，我们只需要取前MAX_TASKS_TO_PROCESS个任务
        tasks_to_process = tasks[:MAX_TASKS_TO_PROCESS] if len(tasks) > MAX_TASKS_TO_PROCESS else tasks
        
        logger.info(f"从{len(tasks)}个任务中筛选出{len(tasks_to_process)}个最近的任务进行处理")
        
        # 遍历筛选后的任务列表
        for task in tasks_to_process:
            try:
                task_created_time = datetime.fromisoformat(task["createdAt"])
                # 如果任务创建时间早于检查窗口开始时间，则提前结束遍历
                # 因为任务列表是按时间倒序排列的，后面的都是更早的任务
                if task_created_time < check_window_start:
                    logger.debug(f"遇到创建时间早于检查窗口的任务，提前结束遍历")
                    break
                    
                # 如果任务创建时间在检查窗口内且未处理过，则添加到新任务列表
                if task_created_time >= check_window_start and not is_task_processed(task["taskId"], self.state["processed_tasks"]):
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
            except Exception as e:
                logger.error(f"处理任务 {task['taskId']} 时出错: {e}")
    
    def run(self):
        """运行监控器"""
        logger.info("任务监控器启动")
        while True:
            try:
                # 获取上次检查时间
                last_check_time = self._get_last_check_time()
                logger.info(f"上次检查时间: {last_check_time.isoformat()}")
                
                # 获取已完成的任务列表
                # 为了确保获取到所有可能的新任务，我们将开始时间设置为上次检查时间减去缓冲时间
                # 结束时间设置为当前时间
                start_time = last_check_time - timedelta(seconds=TIME_WINDOW_BUFFER)
                end_time = datetime.now()
                tasks = self.api_client.get_completed_tasks()
                if tasks is None:
                    logger.error("获取任务列表失败，跳过本次检查")
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                # 过滤出新的任务
                new_tasks = self._filter_new_tasks(tasks, last_check_time)
                
                # 处理新任务
                if new_tasks:
                    self._process_new_tasks(new_tasks)
                else:
                    logger.info("没有发现新任务")
                
                # 更新检查时间
                self.state["last_check_time"] = datetime.now().isoformat()
                
                # 保存状态
                save_state(self.state)
                
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