import sys
import os
import json
import time
# 切换到项目目录
sys.path.insert(0, r"d:\Learn\data\py25\25-10-20\dictation_assistant")

import tkinter as tk
from app import DictationApp
import data_manager

print('cwd=', os.getcwd())
print('stats file exists:', os.path.exists(data_manager.STATS_FILE))
print('module stats file exists:', os.path.exists('module_stats.json'))

print('\n== before load_stats ==')
print(json.dumps(data_manager.load_stats(), ensure_ascii=False, indent=2))

# 启动一个不显示的 tk 实例
root = tk.Tk()
root.withdraw()
app = DictationApp(root)

print('\nCalling update_stats(True)')
app.update_stats(True)

print('\n== after update_stats(True) ==')
print(json.dumps(data_manager.load_stats(), ensure_ascii=False, indent=2))

# 打印 module_stats.json
try:
    with open('module_stats.json', 'r', encoding='utf-8') as f:
        mod = json.load(f)
    print('\nmodule_stats.json content:')
    print(json.dumps(mod, ensure_ascii=False, indent=2))
except Exception as e:
    print('\nmodule_stats.json read error:', e)

# 清理 tk
root.destroy()
print('\nDone')
