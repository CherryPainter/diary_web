import os
import time
import random
import math
from gtts import gTTS
import playsound
import speech_recognition as sr
import tkinter as tk

# 音频缓存目录
AUDIO_CACHE_DIR = "audio_cache"

# 确保缓存目录存在
if not os.path.exists(AUDIO_CACHE_DIR):
    os.makedirs(AUDIO_CACHE_DIR)


def speak(text, max_retries=3):
    """语音合成并播放"""
    # 生成缓存文件名
    cache_filename = os.path.join(AUDIO_CACHE_DIR, f"{text.replace(' ', '_')}.mp3")
    
    # 尝试最多 max_retries 次
    for retry in range(max_retries):
        try:
            # 检查缓存是否存在
            if not os.path.exists(cache_filename):
                # 不存在则创建
                tts = gTTS(text=text, lang='en')
                tts.save(cache_filename)
            
            # 播放音频
            playsound.playsound(cache_filename)
            return True
            
        except Exception as e:
            print(f"语音播放失败 (尝试 {retry+1}/{max_retries}): {e}")
            # 每次失败后稍微延迟一下
            time.sleep(1)
            
            # 如果是最后一次尝试仍失败，尝试删除缓存文件
            if retry == max_retries - 1 and os.path.exists(cache_filename):
                try:
                    os.remove(cache_filename)
                except:
                    pass
    
    return False


def recognize_speech():
    """语音识别 - 改进版UI"""
    recognizer = sr.Recognizer()
    
    # 创建一个现代化的Tk窗口用于显示波形动画
    window = tk.Toplevel()
    window.title("语音输入")
    window.geometry("400x180")
    window.configure(bg="#FFFFFF")  # 使用纯白色背景替代灰色
    window.resizable(False, False)
    
    # 添加圆角效果（通过样式设置）
    window.attributes('-alpha', 0.95)
    
    # 居中窗口
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')
    
    # 创建标题标签
    title_label = tk.Label(window, text="🎤 请开始说话...", 
                          font=("微软雅黑", 16, "bold"), 
                          bg="#F8F9FA", 
                          fg="#FF6B6B")
    title_label.pack(pady=15)
    
    # 创建波形动画画布
    canvas = tk.Canvas(window, width=360, height=80, bg="#F8F9FA", highlightthickness=0)
    canvas.pack(pady=5)
    
    # 创建状态标签
    status_label = tk.Label(window, text="正在聆听...", 
                           font=("微软雅黑", 12), 
                           bg="#F8F9FA", 
                           fg="#4ECDC4")
    status_label.pack(pady=5)
    
    # 创建动画线程控制变量
    is_recording = True
    
    # 定义颜色渐变函数
    def get_gradient_color(index, total_bars):
        # 从红色渐变到青色
        r = int(255 - (255 * index / total_bars))
        g = int(68 + (124 * index / total_bars))
        b = int(205)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    # 开始录音
    with sr.Microphone() as source:
        print("正在录音，请说话...")
        recognizer.adjust_for_ambient_noise(source)
        
        # 在主线程中运行动画
        def animate_waveform():
            if not is_recording:
                window.destroy()
                return
            
            canvas.delete("all")
            center_y = 40
            width = 360
            bar_width = 6
            spacing = 3
            total_bars = (width) // (bar_width + spacing)
            
            # 绘制动画波形
            for i in range(0, width, bar_width + spacing):
                # 创建更有规律的波形，看起来更像真实音频
                height = abs(int(30 * math.sin(i/10 + time.time()*2)) + random.randint(5, 15))
                x1 = i
                y1 = center_y - height // 2
                x2 = i + bar_width
                y2 = center_y + height // 2
                
                # 使用渐变颜色
                color = get_gradient_color(i // (bar_width + spacing), total_bars)
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, radius=3)
            
            # 更新状态文本动画
            status_texts = ["正在聆听...", "请继续说话", "...", "正在聆听..."]
            current_index = int(time.time() * 2) % len(status_texts)
            status_label.config(text=status_texts[current_index])
            
            # 继续动画
            window.after(50, animate_waveform)
        
        # 开始动画
        animate_waveform()
        
        try:
            # 最多识别5秒
            status_label.config(text="处理中...", fg="#FFD43B")
            audio = recognizer.listen(source, timeout=5)
            is_recording = False
            
            # 尝试识别
            text = recognizer.recognize_google(audio, language='en-US')
            print(f"识别结果: {text}")
            return text.lower()
            
        except sr.UnknownValueError:
            print("无法识别语音")
            is_recording = False
            return ""
        except sr.RequestError as e:
            print(f"语音识别服务错误: {e}")
            is_recording = False
            return ""
        except sr.WaitTimeoutError:
            print("录音超时")
            is_recording = False
            return ""
        except Exception as e:
            print(f"语音识别出错: {e}")
            is_recording = False
            return ""