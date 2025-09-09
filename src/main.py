#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 弹幕任务监控器主入口 """

import sys
from .monitor import TaskMonitor
from .utils import setup_logger
logger = setup_logger(__name__)

def main():
    """主函数"""
    try:
        monitor = TaskMonitor()
        monitor.run()
    except KeyboardInterrupt:
        logger.info("程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.exception("程序运行出错")
        sys.exit(1)

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help", "help"):
        print("弹幕任务监控器\n使用方法:  python -m src.main")
        sys.exit(0)
    
    main()
