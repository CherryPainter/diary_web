"""英语听写助手 - 一个帮助学习英语单词的交互式应用程序"""

__version__ = "1.0.0"
__author__ = "Dictation Assistant Team"

from .app import DictationApp
from .data_manager import word_dict, load_stats, save_stats
from .voice_processor import speak, recognize_speech

__all__ = [
    "DictationApp",
    "word_dict",
    "load_stats",
    "save_stats",
    "speak",
    "recognize_speech"
]