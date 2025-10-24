"""英语听写助手 - 简易启动脚本"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入并启动应用
from dictation_assistant.__main__ import main

if __name__ == "__main__":
    main()