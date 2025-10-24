import sys
sys.path.insert(0, r'D:\Learn\data\py25\25-10-20')
try:
    import tkinter as tk
    from dictation_assistant import app
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口，尽量避免打扰
    a = app.DictationApp(root)
    # 尝试更新一次UI以触发潜在的几何管理器错误
    root.update()
    root.destroy()
    print('sanity ok')
except Exception as e:
    import traceback
    traceback.print_exc()
    print('sanity failed')
