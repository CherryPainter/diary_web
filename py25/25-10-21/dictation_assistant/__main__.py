import tkinter as tk
from tkinter import messagebox
import sys
import os
import traceback

# 简化的诊断信息
print("=== 导入诊断 ===")

# 尝试导入gtts并提供处理方案
gtts_available = False
try:
    import gtts
    gtts_available = True
    print("✓ gtts模块已成功导入")
except ImportError:
    print("✗ gtts模块导入失败，将使用模拟模式")
    # 创建一个模拟的gtts模块，避免程序崩溃
    class MockTTS:
        def __init__(self, *args, **kwargs):
            pass
        def save(self, *args, **kwargs):
            # 创建一个空的音频文件作为占位符
            with open(args[0], 'wb') as f:
                f.write(b'')
    
    # 将模拟类添加到sys.modules中
    import types
    mock_gtts = types.ModuleType('gtts')
    mock_gtts.gTTS = MockTTS
    sys.modules['gtts'] = mock_gtts
    print("  ✓ 已创建gtts模拟模块，程序可以继续运行")

# 尝试导入playsound
try:
    import playsound
    print("✓ playsound模块已成功导入")
except ImportError:
    print("✗ playsound模块导入失败")
    # 创建模拟的playsound模块
    import types
    mock_playsound = types.ModuleType('playsound')
    def mock_playsound_func(*args, **kwargs):
        print(f"  模拟播放音频: {args[0]}")
    mock_playsound.playsound = mock_playsound_func
    sys.modules['playsound'] = mock_playsound
    print("  ✓ 已创建playsound模拟模块")

# 导入日志模块：优先包内，失败回退本地
logger = None
try:
    from dictation_assistant.logger import logger
    print("✓ logger模块已成功导入")
except Exception:
    try:
        from logger import logger
        print("✓ logger模块已从本地成功导入")
    except Exception:
        print("✗ logger模块导入失败")
        # 创建一个简单的模拟logger
        class MockLogger:
            def log(self, *args, **kwargs):
                print(f"[LOG] {' '.join(map(str, args))}")
            def log_error(self, *args, **kwargs):
                print(f"[ERROR] {' '.join(map(str, args))}")
            def close(self):
                pass
        logger = MockLogger()
        print("  ✓ 已创建logger模拟对象")

# 导入应用类：绝对导入优先，失败回退到本地
DictationApp = None
try:
    from dictation_assistant.app import DictationApp
    print("✓ DictationApp类已成功导入")
except ImportError:
    try:
        from app import DictationApp
        print("✓ DictationApp类已从本地成功导入")
    except ImportError as e:
        print(f"✗ DictationApp类导入失败: {e}")
        # 检查app.py文件是否存在
        if os.path.exists('app.py'):
            print("  ⚠️ app.py文件存在，但导入失败。可能是依赖问题或代码错误。")
            print("  💡 建议运行: pip install -r requirements.txt 安装所有依赖")
        else:
            print("  ⚠️ app.py文件不存在，请检查文件是否丢失")


def main():
    """主函数"""
    # 首先检查DictationApp是否已成功导入
    if DictationApp is None:
        print("\n❌ 致命错误: 无法导入DictationApp类，程序无法继续运行")
        print("\n📋 解决步骤:")
        print("  1. 确保所有依赖已安装: pip install -r requirements.txt")
        print("  2. 检查app.py文件是否存在且格式正确")
        print("  3. 检查Python环境是否正常")
        
        # 尝试使用简单的tkinter窗口显示错误消息
        try:
            root = tk.Tk()
            root.title("错误")
            # 创建错误消息标签
            error_label = tk.Label(root, text="无法导入DictationApp类\n请确保所有依赖已正确安装\n并检查app.py文件是否存在", 
                                  font=("SimHei", 12), padx=20, pady=20)
            error_label.pack()
            # 创建退出按钮
            exit_btn = tk.Button(root, text="退出", command=root.destroy, 
                               font=("SimHei", 10), width=10)
            exit_btn.pack(pady=10)
            # 设置窗口大小
            root.geometry("400x200")
            # 居中显示
            root.eval('tk::PlaceWindow . center')
            # 启动主循环
            root.mainloop()
        except Exception:
            pass  # 如果tkinter也失败，则忽略
        
        # 确保日志记录器被关闭
        try:
            if logger:
                logger.log("应用程序因导入错误而退出")
                logger.close()
        except Exception:
            pass  # 忽略日志关闭时的错误
        
        return 1
    
    # 如果DictationApp导入成功，则继续正常流程
    root = tk.Tk()
    root.title("听写助手")
    app = None
    
    try:
        # 创建应用实例
        app = DictationApp(root)
        
        # 启动主循环
        root.mainloop()
        
    except Exception as e:
        # 捕获所有未处理的异常并记录
        error_message = f"应用程序发生未处理异常: {str(e)}"
        print(error_message)
        print(traceback.format_exc())
        
        # 尝试使用tkinter显示错误消息
        try:
            messagebox.showerror("应用程序错误", error_message)
        except Exception:
            pass  # 如果tkinter消息框也失败，则忽略
    finally:
        # 确保日志记录器被关闭
        try:
            if logger:
                logger.log("应用程序退出")
                logger.close()
        except Exception:
            pass  # 忽略日志关闭时的错误
    
    return 0

if __name__ == "__main__":
    sys.exit(main())