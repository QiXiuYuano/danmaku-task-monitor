#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
弹幕任务监控器主入口
"""

import sys
import os

# 处理相对导入问题
if __name__ == "__main__" and __package__ is None:
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取src目录的父目录（项目根目录）
    parent_dir = os.path.dirname(current_dir)
    # 将项目根目录添加到sys.path
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    # 设置包名
    __package__ = "src"

from .monitor import TaskMonitor

def main():
    """主函数"""
    try:
        monitor = TaskMonitor()
        monitor.run()
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help", "help"):
        print("弹幕任务监控器")
        sys.exit(0)
    
    main()