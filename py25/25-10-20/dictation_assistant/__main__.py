import tkinter as tk
import sys
import os
import traceback

# 导入日志模块 - 使用相对导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from logger import logger
    print("成功导入日志模块")
except ImportError as e:
    print(f"警告：无法导入日志模块: {e}")
    # 创建增强版的DummyLogger，支持模块统计数据的存储和加载
    class DummyLogger:
        def __init__(self):
            self.MODULE_STATS_FILE = "module_stats.json"
            # 初始化模块统计数据结构
            self.module_stats = {
                "E2C": {"total": 0, "correct": 0, "wrong": 0},
                "C2E": {"total": 0, "correct": 0, "wrong": 0},
                "LISTEN": {"total": 0, "correct": 0, "wrong": 0},
                "review": {"total": 0, "correct": 0, "wrong": 0}
            }
            # 从文件加载历史统计数据
            self.load_module_stats()
            
            # 为兼容学习统计页面，添加session_log属性
            self.session_log = {
                "module_percentage": {}
            }
        
        def log(self, *args, **kwargs): 
            pass
            
        def log_error(self, *args, **kwargs): 
            pass
        
        def log_answer(self, module, is_correct, word=None):
            """记录答题情况"""
            if module in self.module_stats:
                self.module_stats[module]["total"] += 1
                if is_correct:
                    self.module_stats[module]["correct"] += 1
                else:
                    self.module_stats[module]["wrong"] += 1
                # 保存更新后的数据
                self.save_module_stats()
        
        def save_module_stats(self):
            """保存模块统计数据到文件"""
            try:
                import json
                with open(self.MODULE_STATS_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.module_stats, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存模块统计数据失败: {e}")
        
        def load_module_stats(self):
            """从文件加载模块统计数据"""
            try:
                import os
                import json
                if os.path.exists(self.MODULE_STATS_FILE):
                    with open(self.MODULE_STATS_FILE, "r", encoding="utf-8") as f:
                        saved_stats = json.load(f)
                        # 更新各模块的统计数据
                        for module, stats in saved_stats.items():
                            if module in self.module_stats:
                                self.module_stats[module].update(stats)
            except Exception as e:
                print(f"加载模块统计数据失败: {e}")
        
        def close(self, *args, **kwargs): 
            # 确保程序关闭时保存数据
            self.save_module_stats()
    
    logger = DummyLogger()

# 确保可以正确导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # 尝试绝对导入
    from dictation_assistant.app import DictationApp
except ImportError:
    # 尝试相对导入
    try:
        from .app import DictationApp
    except ImportError:
        # 如果都失败，输出错误信息
        print("错误：无法导入DictationApp类")
        sys.exit(1)


def main():
    """主函数"""
    try:
        root = tk.Tk()
        app = DictationApp(root)
        root.mainloop()
    except Exception as e:
        # 记录未捕获的异常
        error_msg = f"应用程序异常：{str(e)}"
        traceback_info = traceback.format_exc()
        
        # 尝试记录到日志
        try:
            if 'logger' in globals():
                logger.log_error(error_msg)
                logger.log_error(traceback_info)
        except:
            pass
        
        # 同时打印到控制台
        print(error_msg)
        print(traceback_info)
        
        # 显示错误对话框
        tk.messagebox.showerror("应用程序错误", f"应用程序遇到错误：\n{str(e)}")


if __name__ == "__main__":
    # 确保程序退出时保存日志
    try:
        main()
    finally:
        try:
            if 'logger' in globals():
                logger.close()
        except:
            pass