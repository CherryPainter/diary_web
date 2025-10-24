"""英语听写助手 - 主程序入口"""

import sys
import os

# 确保可以导入本地包
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dictation_assistant import DictationApp
import tkinter as tk


def main():
    """启动应用程序"""
    print("正在启动英语听写助手...")
    
    # 创建主窗口
    root = tk.Tk()
    
    # 创建应用实例
    app = DictationApp(root)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n应用程序被用户中断")
    except Exception as e:
        print(f"应用程序出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("应用程序已关闭")