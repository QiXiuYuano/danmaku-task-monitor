# 任务监控器
import time
from datetime import datetime
from typing import List, Dict
from .config import CHECK_INTERVAL, MAX_TASKS_TO_PROCESS
from .api_client import DanmakuAPIClient
from .notifier import TelegramNotifier
from .utils import setup_logger, load_state, save_state, get_current_time_iso

logger = setup_logger(__name__)

class TaskMonitor:
    """任务监控器"""
    
    def __init__(self):
        self.STATE_TASK_LIMIT = 1000
        self.RECENT_TASKS_LIMIT = 50
        self.round_no = 0  # 轮次计数器
        self.api_client = DanmakuAPIClient()
        self.notifier = TelegramNotifier()
        self.state = load_state(self.round_no)
        self.initial_check_time = datetime.fromisoformat(
            self.state.get("initial_check_time")
        )
        # 在内存中创建一个包含最近50个任务ID的list
        processed_tasks = self.state.get("processed_tasks", [])
        self.processed_task_ids_list = processed_tasks[-self.RECENT_TASKS_LIMIT:]
        logger.info(f"[监控器初始化] {self.processed_task_ids_list}")
        # 初次运行时写入状态文件，确保初始化的数据持久化
        try:
            save_state(self.state)
            logger.info("[监控器初始化] 监控器开始运行，状态文件已初始化或加载")
        except Exception as e:
            logger.error(f"初次保存状态文件失败: {e}")

    def _add_processed_task(self, task_id, processed_tasks):
        """添加已处理任务ID，状态文件列表超上限时，删除旧ID只保留最近50条"""
        if task_id not in processed_tasks:
            processed_tasks.append(task_id)
            if len(processed_tasks) > self.STATE_TASK_LIMIT:
                processed_tasks = processed_tasks[-self.RECENT_TASKS_LIMIT:]
        return processed_tasks

    def _filter_new_tasks(self, tasks: List[Dict], initial_check_time: datetime) -> List[Dict]:
        """过滤出新的任务（基于任务ID匹配）"""
        new_tasks = []
        
        # 只处理最近的MAX_TASKS_TO_PROCESS个任务
        tasks_to_process = tasks[:MAX_TASKS_TO_PROCESS]
        logger.info(f"[监控轮次 {self.round_no}] 筛选出任务列表中最近 {len(tasks_to_process)} 个已完成任务")
        
        # 遍历筛选后的任务列表
        for task in tasks_to_process:
            try:
                task_created_time = datetime.fromisoformat(task["createdAt"])
                if task_created_time < initial_check_time:
                    continue
                if task["taskId"] in self.processed_task_ids_list:
                    continue

                new_tasks.append(task)
            except ValueError as e:
                logger.warning(f"[监控轮次 {self.round_no}] 任务 {task.get('taskId', 'unknown')} 的创建时间格式不正确: {e}")
                continue

        # API返回倒序（最新在前），反转为正序（最早在前）
        new_tasks.reverse()
        if new_tasks:
            logger.info(f"[监控轮次 {self.round_no}] 监测到 {len(new_tasks)} 个新任务")
        else:
            logger.debug(f"[监控轮次 {self.round_no}] 未监测到新任务")
        return new_tasks
    
    def _process_new_tasks(self, new_tasks: List[Dict]):
        """处理新任务"""
        has_new_task = False
        for task in new_tasks:
            try:
                logger.info(f"[监控轮次 {self.round_no}] 监测到已完成任务，发送通知: taskId:{task['taskId']} - title:{task['title']}")
                self.notifier.send_task_completion_notification(task, self.round_no)

                # 内存 list 更新（仅最近50条）
                self.processed_task_ids_list.append(task["taskId"])
                if len(self.processed_task_ids_list) > self.RECENT_TASKS_LIMIT:
                    self.processed_task_ids_list.pop(0)
                logger.info(self.processed_task_ids_list)

                # 状态文件历史任务列表更新
                self.state["processed_tasks"] = self._add_processed_task(
                    task["taskId"],
                    self.state["processed_tasks"]
                )

                has_new_task = True

            except Exception as e:
                logger.error(f"[监控轮次 {self.round_no}] 处理任务 {task['taskId']} 时出错: {e}")
        return has_new_task

    def run(self):
        """运行监控器"""
        logger.info("任务监控器启动")
        while True:
            try:
                self.round_no += 1
                current_check_time = get_current_time_iso()
                logger.info(f"[监控轮次 {self.round_no}] 当前监控时间: {current_check_time}")
                
                # 获取已完成的任务列表
                tasks = self.api_client.get_completed_tasks(round_no=self.round_no)
                if tasks is None:
                    logger.error(f"[监控轮次 {self.round_no}] API接口获取任务列表失败，跳过本次监控")
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                # 过滤出新的任务
                new_tasks = self._filter_new_tasks(tasks, self.initial_check_time)
                # 处理新任务
                has_new_task = self._process_new_tasks(new_tasks)
                # 仅在有新任务处理或首次监控时保存状态
                if has_new_task:
                    try:
                        save_state(self.state, self.round_no)
                        logger.info(f"[监控轮次 {self.round_no}] 新任务taskId已保存到状态文件，本次监控时间: {current_check_time}")
                    except Exception as e:
                        logger.error(f"[监控轮次 {self.round_no}] 保存状态文件失败: {e}")

                logger.info(f"[监控轮次 {self.round_no}] 本轮监控结束，{CHECK_INTERVAL} 秒后开始下一轮")
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info(f"[监控轮次 {self.round_no}] 收到中断信号，正在退出...")
                break
            except Exception as e:
                logger.error(f"[监控轮次 {self.round_no}] 监控过程中发生未预期的错误: {e}")
                time.sleep(CHECK_INTERVAL)
