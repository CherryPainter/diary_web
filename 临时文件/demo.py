import tkinter as tk
from tkinter import messagebox, ttk
import random
import os
import time
from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
import json
import datetime
import re

# ---------------------
# 单词词库
# ---------------------
word_dict = {
    "apple": "苹果",
    "banana": "香蕉",
    "computer": "电脑",
    "language": "语言",
    "freedom": "自由",
    "book": "书",
    "friend": "朋友",
    "school": "学校"
}

# 单词错误权重文件
WEIGHT_FILE = "word_weights.json"

# ---------------------
# 错题记录
# ---------------------
WRONG_FILE = "wrong_words.json"

def save_wrong(word, meaning):
    """保存错题并更新单词权重"""
    # 保存错题到错题集
    wrongs = []
    if os.path.exists(WRONG_FILE):
        try:
            with open(WRONG_FILE, "r", encoding="utf-8") as f:
                wrongs = json.load(f)
        except:
            pass
    
    # 检查是否已存在
    for item in wrongs:
        if word in item:
            return  # 已存在，不重复添加
    
    wrongs.append({word: meaning})
    
    with open(WRONG_FILE, "w", encoding="utf-8") as f:
        json.dump(wrongs, f, ensure_ascii=False, indent=2)
    
    # 更新单词错误权重
    update_word_weight(word)

def update_word_weight(word):
    """更新单词错误权重"""
    weights = load_word_weights()
    weights[word] = weights.get(word, 0) + 1
    
    with open(WEIGHT_FILE, "w", encoding="utf-8") as f:
        json.dump(weights, f, ensure_ascii=False, indent=2)

def load_word_weights():
    """加载单词权重"""
    weights = {}
    if os.path.exists(WEIGHT_FILE):
        try:
            with open(WEIGHT_FILE, "r", encoding="utf-8") as f:
                weights = json.load(f)
        except:
            pass
    return weights

# ---------------------# 播放英语语音# ---------------------
def speak(word, show_status=True):
    # 创建语音缓存目录
    cache_dir = "audio_cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    # 生成缓存文件名
    safe_text = re.sub(r'[^\w]', '_', word)
    filename = os.path.join(cache_dir, f"{safe_text}.mp3")
    
    try:
        # 检查缓存是否存在
        if not os.path.exists(filename):
            # 缓存不存在，生成语音文件
            retries = 3
            for i in range(retries):
                try:
                    tts = gTTS(word, lang='en')
                    tts.save(filename)
                    break  # 成功则跳出重试循环
                except Exception as e:
                    if i == retries - 1:  # 最后一次重试仍然失败
                        raise e
                    if show_status:
                        messagebox.showinfo("提示", f"网络连接失败，正在尝试第{i+2}次连接...")
                    time.sleep(1)
        
        # 播放语音文件
        playsound(filename)
        return True
    except Exception as e:
        error_msg = f"播放语音时出错: {e}"
        print(error_msg)
        # 提供更友好的错误提示
        if show_status:
            if "Failed to connect" in str(e):
                messagebox.showerror("网络连接错误", "无法连接到语音服务。请检查您的网络连接后重试。")
            else:
                messagebox.showerror("错误", f"播放语音失败: {str(e)}")
        return False

# ---------------------# 语音识别# ---------------------
def recognize_speech():
    r = sr.Recognizer()
    # 设置识别器参数以提高识别率
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    
    try:
        with sr.Microphone() as source:
            # 显示语音输入界面，带有倒计时
            root = tk.Toplevel()
            root.title("语音输入")
            root.geometry("300x150")
            root.configure(bg="#f0f0f0")
            root.resizable(False, False)
            
            # 居中窗口
            root.update_idletasks()
            width = root.winfo_width()
            height = root.winfo_height()
            x = (root.winfo_screenwidth() // 2) - (width // 2)
            y = (root.winfo_screenheight() // 2) - (height // 2)
            root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            
            # 创建标签
            label = tk.Label(root, text="请开始说话...", font=("微软雅黑", 14), bg="#f0f0f0")
            label.pack(pady=20)
            
            # 创建波形动画
            canvas = tk.Canvas(root, width=200, height=30, bg="#f0f0f0", highlightthickness=0)
            canvas.pack(pady=10)
            bars = []
            for i in range(20):
                bar = canvas.create_rectangle(i*10, 30, i*10+5, 30, fill="#4a7abc")
                bars.append(bar)
            
            # 更新波形动画
            def update_wave():
                for i in range(len(bars)):
                    height = random.randint(5, 30)
                    canvas.coords(bars[i], i*10, 30, i*10+5, 30-height)
                root.after(50, update_wave)
            
            update_wave()
            root.update()
            
            # 调整麦克风
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=8)
            root.destroy()
        
        text = r.recognize_google(audio, language="en-US")
        return text.lower()
    except sr.UnknownValueError:
        if 'root' in locals():
            root.destroy()
        return None
    except sr.RequestError:
        if 'root' in locals():
            root.destroy()
        messagebox.showerror("错误", "无法连接到语音识别服务")
        return None
    except Exception as e:
        if 'root' in locals():
            root.destroy()
        print(f"语音识别错误: {e}")
        return None

# ---------------------# 学习统计# ---------------------
def load_stats():
    STATS_FILE = "learning_stats.json"
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"total_questions": 0, "correct_answers": 0, "wrong_answers": 0, "streak": 0, "best_streak": 0}

def save_stats(stats):
    STATS_FILE = "learning_stats.json"
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

# ---------------------# GUI界面逻辑# ---------------------
class DictationApp:
    def __init__(self, root):
        # 设置主题颜色
        self.theme = {
            "primary": "#4a7abc",
            "secondary": "#f0f0f0",
            "text": "#333333",
            "success": "#4CAF50",
            "error": "#F44336",
            "warning": "#FF9800",
            "background": "#ffffff"
        }
        
        self.root = root
        self.root.title("英语听写助手")
        self.root.geometry("600x500")
        self.root.configure(bg=self.theme["background"])
        self.root.resizable(True, True)
        
        # 配置窗口图标
        # 尝试设置窗口图标（可选）
        try:
            self.root.iconbitmap(default="")
        except:
            pass
        
        # 绑定回车键提交答案
        self.root.bind('<Return>', lambda event: self.check_answer())
        
        # 初始化变量
        self.word = ""
        self.meaning = ""
        self.mode = None
        self.stats = load_stats()
        self.hint_used = False
        self.history = []
        
        # 创建主框架
        self.main_frame = tk.Frame(root, bg=self.theme["background"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建标题标签
        self.title_label = tk.Label(self.main_frame, text="英语听写助手", 
                                  font=("微软雅黑", 20, "bold"), 
                                  bg=self.theme["background"],
                                  fg=self.theme["primary"])
        self.title_label.pack(pady=(0, 15))
        
        # 创建统计信息框架
        stats_frame = tk.Frame(self.main_frame, bg=self.theme["secondary"])
        stats_frame.pack(fill=tk.X, pady=10, padx=20, ipady=5)
        
        self.stats_label = tk.Label(stats_frame, 
                                  text=self.get_stats_text(),
                                  font=("微软雅黑", 10),
                                  bg=self.theme["secondary"])
        self.stats_label.pack(pady=2)
        
        # 创建题目显示标签
        self.label = tk.Label(self.main_frame, 
                           text="请选择学习模式", 
                           font=("微软雅黑", 14), 
                           bg=self.theme["background"],
                           fg=self.theme["text"])
        self.label.pack(pady=20)
        
        # 创建难度选择框架
        self.difficulty_frame = tk.Frame(self.main_frame, bg=self.theme["background"])
        self.difficulty_frame.pack(pady=10)
        
        self.difficulty_var = tk.StringVar(value="normal")
        difficulties = [("简单", "easy"), ("普通", "normal"), ("困难", "hard")]
        
        tk.Label(self.difficulty_frame, text="难度: ", bg=self.theme["background"]).pack(side=tk.LEFT)
        
        for text, value in difficulties:
            btn = tk.Radiobutton(self.difficulty_frame, 
                               text=text, 
                               variable=self.difficulty_var, 
                               value=value,
                               bg=self.theme["background"])
            btn.pack(side=tk.LEFT, padx=5)
        
        # 创建模式选择按钮框架
        mode_frame = tk.Frame(self.main_frame, bg=self.theme["background"])
        mode_frame.pack(pady=10)
        
        button_style = {"font": ("微软雅黑", 12), "width": 12, "bd": 0, "relief": tk.FLAT}
        
        self.btn_e2c = tk.Button(mode_frame, 
                               text="英译汉", 
                               command=self.english_to_chinese,
                               bg=self.theme["primary"],
                               fg="white",
                               **button_style)
        self.btn_e2c.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_c2e = tk.Button(mode_frame, 
                               text="汉译英", 
                               command=self.chinese_to_english,
                               bg=self.theme["primary"],
                               fg="white",
                               **button_style)
        self.btn_c2e.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_listen = tk.Button(mode_frame, 
                                  text="听写拼写", 
                                  command=self.listen_and_spell,
                                  bg=self.theme["primary"],
                                  fg="white",
                                  **button_style)
        self.btn_listen.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 添加按钮悬停效果
        self.add_hover_effect(self.btn_e2c)
        self.add_hover_effect(self.btn_c2e)
        self.add_hover_effect(self.btn_listen)
        
        # 创建输入区域
        input_frame = tk.Frame(self.main_frame, bg=self.theme["background"])
        input_frame.pack(pady=15, fill=tk.X, padx=50)
        
        self.entry = tk.Entry(input_frame, 
                            font=("微软雅黑", 14),
                            bd=2, relief=tk.FLAT, 
                            highlightthickness=1, 
                            highlightbackground=self.theme["primary"])
        self.entry.pack(fill=tk.X, ipady=8)
        
        # 创建操作按钮框架
        action_frame = tk.Frame(self.main_frame, bg=self.theme["background"])
        action_frame.pack(pady=10)
        
        self.btn_submit = tk.Button(action_frame, 
                                  text="提交答案", 
                                  command=self.check_answer,
                                  bg=self.theme["success"],
                                  fg="white",
                                  **button_style)
        self.btn_submit.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_voice = tk.Button(action_frame, 
                                 text="语音回答", 
                                 command=self.voice_answer,
                                 bg=self.theme["warning"],
                                 fg="white",
                                 **button_style)
        self.btn_voice.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_hint = tk.Button(action_frame, 
                                text="提示", 
                                command=self.show_hint,
                                bg=self.theme["secondary"],
                                fg=self.theme["text"],
                                **button_style)
        self.btn_hint.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 添加按钮悬停效果
        self.add_hover_effect(self.btn_submit, "#45a049")
        self.add_hover_effect(self.btn_voice, "#e68900")
        self.add_hover_effect(self.btn_hint, "#e0e0e0")
        
        # 创建底部按钮框架
        bottom_frame = tk.Frame(self.main_frame, bg=self.theme["background"])
        bottom_frame.pack(side=tk.BOTTOM, pady=10)
        
        self.btn_next = tk.Button(bottom_frame, 
                               text="下一题", 
                               command=self.next_question,
                               bg=self.theme["primary"],
                               fg="white",
                               **button_style)
        self.btn_next.pack(side=tk.LEFT, padx=5)
        
        self.btn_review = tk.Button(bottom_frame, 
                                  text="复习错题", 
                                  command=self.review_wrong,
                                  bg=self.theme["error"],
                                  fg="white",
                                  **button_style)
        self.btn_review.pack(side=tk.LEFT, padx=5)
        
        self.btn_exit = tk.Button(bottom_frame, 
                                text="退出", 
                                command=lambda: self.exit_app(),
                                bg=self.theme["secondary"],
                                fg=self.theme["text"],
                                **button_style)
        self.btn_exit.pack(side=tk.RIGHT, padx=5)
        
        # 添加按钮悬停效果
        self.add_hover_effect(self.btn_next)
        self.add_hover_effect(self.btn_review, "#d32f2f")
        self.add_hover_effect(self.btn_exit, "#e0e0e0")
        
        # 初始化禁用下一题按钮
        self.btn_next.config(state=tk.DISABLED)
        self.btn_hint.config(state=tk.DISABLED)
        
        # 添加学习记录
        self.log_start_session()
        
    def add_hover_effect(self, button, hover_color=None):
        """为按钮添加悬停效果"""
        original_color = button.cget("bg")
        if hover_color is None:
            # 自动计算悬停颜色（稍深一些）
            if original_color.startswith("#"):
                r, g, b = int(original_color[1:3], 16), int(original_color[3:5], 16), int(original_color[5:7], 16)
                r, g, b = max(0, r-20), max(0, g-20), max(0, b-20)
                hover_color = f"#{r:02x}{g:02x}{b:02x}"
            else:
                hover_color = "#3a6a9c"  # 默认悬停颜色
        
        def on_enter(event):
            button.config(bg=hover_color)
            
        def on_leave(event):
            button.config(bg=original_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
    def get_stats_text(self):
        """获取统计信息文本"""
        accuracy = 0
        if self.stats["total_questions"] > 0:
            accuracy = round(self.stats["correct_answers"] / self.stats["total_questions"] * 100, 1)
        
        return f"总题数: {self.stats['total_questions']} | 正确率: {accuracy}% | 连续正确: {self.stats['streak']} | 最佳连续: {self.stats['best_streak']}"
        
    def update_stats(self, is_correct):
        """更新学习统计"""
        self.stats["total_questions"] += 1
        
        if is_correct:
            self.stats["correct_answers"] += 1
            self.stats["streak"] += 1
            self.stats["best_streak"] = max(self.stats["best_streak"], self.stats["streak"])
        else:
            self.stats["wrong_answers"] += 1
            self.stats["streak"] = 0
        
        save_stats(self.stats)
        self.stats_label.config(text=self.get_stats_text())
        
    def log_start_session(self):
        """记录学习会话开始时间"""
        LOG_FILE = "learning_log.json"
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except:
                pass
        
        logs.append({
            "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None
        })
        
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        self.session_index = len(logs) - 1
        
    def log_end_session(self):
        """记录学习会话结束时间"""
        LOG_FILE = "learning_log.json"
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
                
                if 0 <= self.session_index < len(logs):
                    logs[self.session_index]["end_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    with open(LOG_FILE, "w", encoding="utf-8") as f:
                        json.dump(logs, f, ensure_ascii=False, indent=2)
            except:
                pass
                
    def exit_app(self):
        """安全退出应用"""
        if messagebox.askyesno("确认退出", "确定要退出英语听写助手吗？"):
            self.log_end_session()
            self.root.quit()

    def english_to_chinese(self):
        self.mode = "E2C"
        self.hint_used = False
        self.word = self.get_word_by_difficulty()
        self.meaning = word_dict[self.word]
        self.label.config(text=f"英文：{self.word}", fg=self.theme["text"])
        self.btn_hint.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)
        self.entry.focus_set()
        
    def chinese_to_english(self):
        self.mode = "C2E"
        self.hint_used = False
        self.word, self.meaning = self.get_word_pair_by_difficulty()
        self.label.config(text=f"中文：{self.meaning}", fg=self.theme["text"])
        self.btn_hint.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)
        self.entry.focus_set()
    
    def get_word_by_difficulty(self):
        """根据难度获取单词"""
        difficulty = self.difficulty_var.get()
        words = list(word_dict.keys())
        
        if difficulty == "easy":
            # 简单模式：只选择短单词（4个字母以下）
            easy_words = [w for w in words if len(w) <= 4]
            if easy_words:
                words = easy_words
        elif difficulty == "hard":
            # 困难模式：只选择长单词（6个字母以上）
            hard_words = [w for w in words if len(w) >= 6]
            if hard_words:
                words = hard_words
        
        return random.choice(words)
    
    def get_word_pair_by_difficulty(self):
        """根据难度获取单词对"""
        difficulty = self.difficulty_var.get()
        word_pairs = list(word_dict.items())
        
        if difficulty == "easy":
            # 简单模式：只选择短单词（4个字母以下）
            easy_pairs = [(w, m) for w, m in word_pairs if len(w) <= 4]
            if easy_pairs:
                word_pairs = easy_pairs
        elif difficulty == "hard":
            # 困难模式：只选择长单词（6个字母以上）
            hard_pairs = [(w, m) for w, m in word_pairs if len(w) >= 6]
            if hard_pairs:
                word_pairs = hard_pairs
        
        return random.choice(word_pairs)
    
    def show_hint(self):
        """显示提示"""
        if not self.hint_used:
            self.hint_used = True
            if self.mode == "E2C":
                hint = f"提示：{self.meaning[0]}..."  # 显示中文意思的第一个字
            elif self.mode == "C2E":
                hint = f"提示：{self.word[0].upper()}{'_' * (len(self.word) - 1)}"  # 显示首字母和下划线
            else:  # LISTEN
                hint = f"提示：{self.word[0].upper()}{'_' * (len(self.word) - 1)}"  # 显示首字母和下划线
            
            self.label.config(fg=self.theme["warning"])
            messagebox.showinfo("提示", hint)

    def chinese_to_english(self):
        self.mode = "C2E"
        self.word, self.meaning = random.choice(list(word_dict.items()))
        self.label.config(text=f"中文：{self.meaning}")

    def listen_and_spell(self):
        try:
            self.mode = "LISTEN"
            self.hint_used = False
            self.word = self.get_word_by_difficulty()
            self.meaning = word_dict[self.word]
            self.label.config(text="请听单词并输入拼写：", fg=self.theme["text"])
            self.btn_hint.config(state=tk.NORMAL)
            self.btn_next.config(state=tk.DISABLED)
            
            # 创建一个按钮让用户控制是否播放语音
            if hasattr(self, 'play_button'):
                self.play_button.destroy()
            
            # 创建播放按钮
            self.play_button = tk.Button(self.main_frame, 
                                       text="🔊 播放单词", 
                                       command=lambda: self.play_word_audio(),
                                       bg=self.theme["primary"],
                                       fg="white",
                                       font=("微软雅黑", 12),
                                       width=15, 
                                       bd=0, 
                                       relief=tk.FLAT)
            self.play_button.pack(pady=10)
            
            # 添加悬停效果
            self.add_hover_effect(self.play_button)
            
            # 同时自动播放一次
            self.play_word_audio()
            
            self.entry.focus_set()
        except Exception as e:
            print(f"听写模式初始化出错: {e}")
            messagebox.showerror("错误", f"听写模式初始化失败: {str(e)}")
    
    def play_word_audio(self):
        """播放单词音频"""
        # 禁用按钮防止重复点击
        self.play_button.config(state=tk.DISABLED, text="🔊 播放中...")
        self.root.update()
        
        # 播放语音
        success = speak(self.word)
        
        # 恢复按钮状态
        self.play_button.config(state=tk.NORMAL, text="🔊 播放单词")
        return success
    
    def next_question(self):
        """下一题"""
        if self.mode == "E2C":
            self.english_to_chinese()
        elif self.mode == "C2E":
            self.chinese_to_english()
        elif self.mode == "LISTEN":
            self.listen_and_spell()
    
    def review_wrong(self):
        """复习错题"""
        if os.path.exists(WRONG_FILE):
            try:
                with open(WRONG_FILE, "r", encoding="utf-8") as f:
                    wrongs = json.load(f)
                
                if not wrongs:
                    messagebox.showinfo("提示", "没有错题记录！")
                    return
                
                # 随机选择一道错题
                wrong_item = random.choice(wrongs)
                word = list(wrong_item.keys())[0]
                meaning = wrong_item[word]
                
                self.word = word
                self.meaning = meaning
                self.mode = "REVIEW"
                self.hint_used = False
                
                # 随机选择复习模式
                review_type = random.choice(["E2C", "C2E", "LISTEN"])
                
                if review_type == "E2C":
                    self.label.config(text=f"[复习] 英文：{word}", fg=self.theme["error"])
                elif review_type == "C2E":
                    self.label.config(text=f"[复习] 中文：{meaning}", fg=self.theme["error"])
                else:  # LISTEN
                    self.label.config(text="[复习] 请听单词并输入拼写：", fg=self.theme["error"])
                    # 播放单词
                    speak(word)
                
                self.btn_hint.config(state=tk.NORMAL)
                self.btn_next.config(state=tk.DISABLED)
                self.entry.focus_set()
                
            except Exception as e:
                print(f"复习错题出错: {e}")
                messagebox.showerror("错误", "加载错题记录失败")
        else:
            messagebox.showinfo("提示", "没有错题记录！")

    def check_answer(self):
        ans = self.entry.get().strip().lower()
        if not ans:
            messagebox.showwarning("提示", "请先输入答案！")
            return
        
        if not self.mode:
            messagebox.showinfo("提示", "请先选择学习模式！")
            return
        
        is_correct = False
        correct_answer = ""
        
        # 根据模式检查答案
        if self.mode == "E2C" or (self.mode == "REVIEW" and ans == self.meaning):
            is_correct = (ans == self.meaning)
            correct_answer = self.meaning
        elif self.mode == "C2E" or self.mode == "LISTEN" or (self.mode == "REVIEW" and ans == self.word.lower()):
            is_correct = (ans == self.word.lower())
            correct_answer = self.word
        
        # 更新统计信息
        self.update_stats(is_correct)
        
        # 显示结果
        if is_correct:
            # 显示成功动画
            self.show_success_animation()
            messagebox.showinfo("结果", f"✅ 正确！{self.get_streak_message()}")
        else:
            messagebox.showerror("结果", f"❌ 错误！正确答案：{correct_answer}")
            # 保存错题
            save_wrong(self.word, self.meaning)
        
        # 清空输入框，启用下一题按钮
        self.entry.delete(0, tk.END)
        self.btn_next.config(state=tk.NORMAL)
        self.btn_next.focus_set()
    
    def show_success_animation(self):
        """显示成功动画效果"""
        # 闪烁标签文字颜色
        original_color = self.label.cget("fg")
        
        def flash():
            for _ in range(2):
                self.label.config(fg=self.theme["success"])
                self.root.update()
                time.sleep(0.1)
                self.label.config(fg=original_color)
                self.root.update()
                time.sleep(0.1)
        
        # 在非主线程中运行动画
        import threading
        thread = threading.Thread(target=flash)
        thread.daemon = True
        thread.start()
    
    def get_streak_message(self):
        """获取连续正确的鼓励信息"""
        if self.stats["streak"] >= 10:
            return "太棒了！连续正确10次！"
        elif self.stats["streak"] >= 5:
            return "真不错！继续保持！"
        elif self.stats["streak"] >= 3:
            return "很好！再接再厉！"
        return ""
    
    def voice_answer(self):
        text = recognize_speech()
        if not text:
            messagebox.showerror("错误", "没听清楚，再试一次吧～")
            return
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        # 自动检查答案
        self.check_answer()

    def voice_answer(self):
        text = recognize_speech()
        if not text:
            messagebox.showerror("错误", "没听清楚，再试一次吧～")
            return
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.check_answer()

# ---------------------
# 启动程序
# ---------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DictationApp(root)
    root.mainloop()
