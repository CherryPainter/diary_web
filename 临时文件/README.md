# 英语听写助手

一个功能齐全的英语单词学习和听写应用程序，帮助用户有效学习英语单词。

## 项目结构

```
py25/25-10-20/
├── dictation_assistant/       # 主包目录
│   ├── __init__.py            # 包初始化文件
│   ├── __main__.py            # 包的主入口
│   ├── data_manager.py        # 数据管理模块
│   ├── voice_processor.py     # 语音处理模块
│   └── app.py                 # 主应用类模块
├── main.py                    # 应用程序主入口
├── start.py                   # 简易启动脚本
└── README.md                  # 项目说明文档
```

## 模块说明

1. **data_manager.py**
   - 单词字典管理
   - 学习统计记录
   - 错题管理
   - 单词权重管理

2. **voice_processor.py**
   - 语音合成（播放单词）
   - 语音识别（语音输入）
   - 音频缓存管理

3. **app.py**
   - GUI界面设计
   - 应用逻辑处理
   - 用户交互管理

4. **__main__.py**
   - 包的主入口点

## 运行方式

### 方法1：使用main.py

```bash
python main.py
```

### 方法2：使用start.py

```bash
python start.py
```

### 方法3：直接运行包

```bash
python -m dictation_assistant
```

## 功能特点

- **多种学习模式**：英译汉、汉译英、听写拼写
- **难度选择**：简单、普通、困难
- **智能复习**：基于错误率的加权重复系统
- **语音功能**：支持语音输入和单词朗读
- **学习统计**：记录学习进度和正确率
- **错题复习**：自动保存错题并提供复习功能
- **用户友好界面**：现代化UI设计，支持按钮悬停效果

## 依赖项

- Python 3.6+
- tkinter (Python标准库)
- gTTS (文本转语音)
- playsound (音频播放)
- SpeechRecognition (语音识别)

## 安装依赖

```bash
pip install gTTS playsound SpeechRecognition
```

## 注意事项

- 语音功能需要网络连接（使用Google的语音服务）
- 首次运行会自动创建必要的目录和文件
- 学习数据保存在当前目录的JSON文件中