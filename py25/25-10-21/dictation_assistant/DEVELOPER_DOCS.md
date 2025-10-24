# 听写助手开发者文档

## 项目概述

听写助手是一个用于英语单词学习的桌面应用程序，主要功能包括英语-中文、中文-英语单词练习，听力练习和错误单词复习。应用提供了友好的用户界面和语音交互功能，帮助用户更有效地记忆单词。

## 项目架构

项目采用模块化设计，各模块职责明确，通过清晰的接口进行交互。整体架构如下：

```
├── __main__.py        # 程序入口点
├── app.py             # 主应用程序类和UI实现
├── data_manager.py    # 数据管理和持久化
├── voice_processor.py # 语音处理（合成和识别）
├── logger.py          # 日志系统
└── 数据文件目录
```

### 模块职责

| 模块 | 主要职责 | 文件位置 |
|------|---------|----------|
| 应用入口 | 程序启动、依赖检查和异常处理 | <mcfile name="__main__.py" path="d:\Learn\data\py25\25-10-21\dictation_assistant\__main__.py"></mcfile> |
| 主应用程序 | UI实现、用户交互逻辑、学习模式切换 | <mcfile name="app.py" path="d:\Learn\data\py25\25-10-21\dictation_assistant\app.py"></mcfile> |
| 数据管理器 | 词典加载、统计数据管理、错误单词记录 | <mcfile name="data_manager.py" path="d:\Learn\data\py25\25-10-21\dictation_assistant\data_manager.py"></mcfile> |
| 语音处理器 | 文本转语音、语音识别功能 | <mcfile name="voice_processor.py" path="d:\Learn\data\py25\25-10-21\dictation_assistant\voice_processor.py"></mcfile> |
| 日志系统 | 应用日志记录、性能统计 | <mcfile name="logger.py" path="d:\Learn\data\py25\25-10-21\dictation_assistant\logger.py"></mcfile> |

## 核心类与API

### 1. DictationApp (app.py)

主应用程序类，负责整个应用的UI和交互逻辑。

**主要成员函数：**
- `__init__(self, root)`: 初始化应用界面和状态
- `setup_ui()`: 设置用户界面组件
- `load_word_dict()`: 加载单词词典
- `switch_mode()`: 切换不同的学习模式
- `generate_question()`: 生成练习题
- `check_answer()`: 检查用户答案
- `speak_word()`: 播放单词发音
- `voice_input()`: 语音输入功能

### 2. StatsManager (app.py)

统计管理器，负责学习数据的统计和持久化。

**主要成员函数：**
- `__init__(self, load_stats_func, save_stats_func, ...)`: 初始化统计管理器
- `snapshot()`: 获取当前统计数据快照
- `accuracy()`: 计算正确率
- `update_on_answer(self, is_correct, current_module=None)`: 根据答题情况更新统计

### 3. 数据管理模块 (data_manager.py)

**主要函数：**
- `load_word_dict()`: 加载单词词典
- `save_wrong(word, answer, correct_answer)`: 保存错误单词记录
- `load_stats()`: 加载学习统计数据
- `save_stats(stats)`: 保存学习统计数据
- `adjust_word_weight(word, is_correct)`: 根据答题情况调整单词权重
- `get_today_goal()`: 获取今日学习目标
- `update_today_progress()`: 更新今日学习进度

### 4. 语音处理模块 (voice_processor.py)

**主要函数：**
- `speak(text, max_retries=3)`: 文本转语音并播放
- `recognize_speech()`: 语音识别功能

### 5. 日志系统 (logger.py)

**主要功能：**
- 记录应用使用日志
- 统计模块使用情况
- 异常错误记录
- 会话结束时生成摘要报告

## 数据文件结构

| 文件名 | 用途 | 位置 |
|-------|------|------|
| word_dict.json | 单词词典 | <mcfile name="word_dict.json" path="d:\Learn\data\py25\25-10-21\dictation_assistant\word_dict.json"></mcfile> |
| wrong_words.json | 错误单词记录 | <mcfile name="wrong_words.json" path="d:\Learn\data\py25\25-10-21\dictation_assistant\wrong_words.json"></mcfile> |
| app_log.json/app_log.txt | 应用日志 | <mcfile name="app_log.json" path="d:\Learn\data\py25\25-10-21\dictation_assistant\app_log.json"></mcfile> |
| module_stats.json | 模块使用统计 | <mcfile name="module_stats.json" path="d:\Learn\data\py25\25-10-21\dictation_assistant\module_stats.json"></mcfile> |
| daily_goals.json | 每日学习目标 | <mcfile name="daily_goals.json" path="d:\Learn\data\py25\25-10-21\dictation_assistant\daily_goals.json"></mcfile> |

## 依赖项

项目依赖以下Python包：

- **ttkbootstrap>=0.5.0**：现代化UI主题（可选）
- **playsound>=1.3.0**：音频播放
- **gTTS>=2.2.2**：文本转语音
- **SpeechRecognition>=3.8.1**：语音识别

详见 <mcfile name="requirements.txt" path="d:\Learn\data\py25\25-10-21\dictation_assistant\requirements.txt"></mcfile>

## 开发指南

### 环境设置

1. 克隆代码库
2. 安装依赖：`pip install -r requirements.txt`
3. 运行应用：`python __main__.py`

### 添加新功能

1. **添加新的学习模式**
   - 在`app.py`中扩展`switch_mode()`方法
   - 添加相应的UI组件和逻辑处理函数

2. **修改词典结构**
   - 编辑`word_dict.json`文件
   - 词典格式：`{"word": "meaning"}` 或 `{"word": ["meaning1", "meaning2"]}`

3. **添加新的数据统计功能**
   - 在`StatsManager`类中添加新的统计指标
   - 更新数据持久化逻辑

### 调试技巧

1. **日志查看**：检查`app_log.txt`文件获取详细日志
2. **模块统计**：`module_stats.json`包含各功能模块的使用统计
3. **错误单词记录**：`wrong_words.json`记录用户错误的单词

## 代码规范

- 使用4个空格进行缩进
- 遵循PEP 8命名规范
- 关键函数添加文档字符串
- 使用try-except处理可能的异常
- 优先使用相对导入，同时提供绝对导入兼容

## 已知问题与解决方案

1. **日志系统关闭卡死问题**
   - 问题：应用程序关闭时可能因日志队列阻塞导致卡死
   - 解决方案：已通过添加超时机制和队列清空功能修复

2. **依赖缺失问题**
   - 问题：缺少gtts等依赖时程序无法启动
   - 解决方案：添加了模拟模块机制，确保程序在缺少部分依赖时仍可运行

## 贡献指南

1. Fork项目仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add some amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 打开Pull Request

## 版本历史

- v1.0.0：初始版本，实现基本的听写功能
- v1.1.0：添加语音输入功能和统计功能
- v1.2.0：优化UI界面，添加多种学习模式
- v1.3.0：修复日志系统卡死问题，增强错误处理机制