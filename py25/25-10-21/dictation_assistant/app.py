import tkinter as tk
from tkinter import messagebox, ttk
import random
import threading
import time
import re
import math
import csv
from datetime import datetime
# 兼容包内与脚本运行的导入：优先包内，失败回退本地
try:
    from dictation_assistant.data_manager import (
        word_dict, save_wrong, load_stats, save_stats,
        log_start_session, log_end_session, load_word_weights, WRONG_FILE,
        adjust_word_weight, meaning_matches, get_today_goal, update_today_progress, reset_all_data, get_history_records,
        load_daily_goals, save_daily_goals
    )
except ImportError:
    from data_manager import (
        word_dict, save_wrong, load_stats, save_stats,
        log_start_session, log_end_session, load_word_weights, WRONG_FILE,
        adjust_word_weight, meaning_matches, get_today_goal, update_today_progress, reset_all_data, get_history_records,
        load_daily_goals, save_daily_goals
    )

try:
    from dictation_assistant.voice_processor import speak, recognize_speech
except ImportError:
    from voice_processor import speak, recognize_speech

try:
    from dictation_assistant.logger import logger
except ImportError:
    from logger import logger

# 可选：优先使用 ttkbootstrap 提供现代主题（如果可用）
try:
    import ttkbootstrap as tb
    TB_AVAILABLE = True
except Exception:
    TB_AVAILABLE = False

# 统计管理器：隔离状态与存储，避免全局污染
class StatsManager:
    def __init__(self, load_stats_func, save_stats_func, get_today_goal_func, update_today_progress_func,
                 reset_all_data_func, get_history_records_func, logger_inst):
        self._load_stats = load_stats_func
        self._save_stats = save_stats_func
        self._get_today_goal = get_today_goal_func
        self._update_today_progress = update_today_progress_func
        self._reset_all_data = reset_all_data_func
        self._get_history_records = get_history_records_func
        self._logger = logger_inst
        # 内部状态隔离
        try:
            self.stats = self._load_stats() or {
                "total_questions": 0,
                "correct_answers": 0,
                "wrong_answers": 0,
                "streak": 0,
                "best_streak": 0
            }
        except Exception:
            self.stats = {
                "total_questions": 0,
                "correct_answers": 0,
                "wrong_answers": 0,
                "streak": 0,
                "best_streak": 0
            }

    def snapshot(self):
        return {
            "total_questions": self.stats.get("total_questions", 0),
            "correct_answers": self.stats.get("correct_answers", 0),
            "wrong_answers": self.stats.get("wrong_answers", 0),
            "streak": self.stats.get("streak", 0),
            "best_streak": self.stats.get("best_streak", 0),
        }

    def accuracy(self):
        tq = self.stats.get("total_questions", 0)
        if tq > 0:
            return round(self.stats.get("correct_answers", 0) / tq * 100, 1)
        return 0

    def update_on_answer(self, is_correct, current_module=None):
        # 更新学习统计
        self.stats["total_questions"] = self.stats.get("total_questions", 0) + 1
        if is_correct:
            self.stats["correct_answers"] = self.stats.get("correct_answers", 0) + 1
            self.stats["streak"] = self.stats.get("streak", 0) + 1
            if self.stats["streak"] > self.stats.get("best_streak", 0):
                self.stats["best_streak"] = self.stats["streak"]
        else:
            self.stats["wrong_answers"] = self.stats.get("wrong_answers", 0) + 1
            self.stats["streak"] = 0
        # 持久化
        try:
            self._save_stats(self.stats)
        except Exception:
            pass
        # 更新今日目标历史
        try:
            self._update_today_progress(is_correct)
        except Exception:
            pass
        # 记录模块统计
        try:
            if self._logger and hasattr(self._logger, 'log_answer') and current_module:
                mod = current_module if current_module != "REVIEW" else "review"
                self._logger.log_answer(mod, is_correct)
        except Exception:
            pass

    def reset_all(self):
        # 重置所有持久化数据
        try:
            written, failed = self._reset_all_data()
            if self._logger:
                self._logger.log(f"reset_all_data wrote: {written}, failed: {failed}")
        except Exception as e:
            if self._logger:
                self._logger.log(f"调用 reset_all_data 失败: {e}")
        # 重置内存统计并保存
        self.stats = {
            "total_questions": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "streak": 0,
            "best_streak": 0
        }
        try:
            self._save_stats(self.stats)
        except Exception:
            pass

    def today_goal(self):
        try:
            return self._get_today_goal()
        except Exception:
            return {"target": 20, "current": 0, "correct": 0, "percentage": 0}

    def module_stats(self):
        try:
            if self._logger and hasattr(self._logger, 'module_stats'):
                return self._logger.module_stats or {}
        except Exception:
            pass
        return {}

    def module_percentages(self):
        ms = self.module_stats()
        total_all = sum(module.get("total", 0) for module in ms.values())
        if total_all > 0:
            return {m: round((s.get("total", 0) / total_all) * 100, 1) for m, s in ms.items()}
        return {m: 0 for m in ms}

    def history_records(self, days=30):
        try:
            return self._get_history_records(days=days)
        except Exception:
            return []


class DictationApp:
    def __init__(self, root):
        # 全新现代UI主题颜色方案 - 移除灰色元素
        self.theme = {
            "primary": "#4361EE",  # 主色调：深邃蓝
            "primary_light": "#4895EF",  # 亮蓝色
            "primary_dark": "#3A0CA3",  # 深蓝色
            "secondary": "#4CC9F0",  # 辅助色：浅蓝色
            "secondary_light": "#8FEFFF",  # 辅助色亮度
            "accent": "#F72585",  # 强调色：亮粉色
            "text": "#2B2D42",  # 深色文本
            "text_light": "#4361EE",  # 使用主色调替代灰色文本
            "success": "#4CAF50",  # 成功绿色
            "error": "#EF233C",  # 错误红色
            "warning": "#FF9F1C",  # 警告橙色
            "background": "#FFFFFF",  # 纯白色背景
            "card_bg": "#FFFFFF",  # 卡片背景
            "shadow": "#A89F9F",  # 阴影色
            "border": "#FFFFFF",  # 隐藏边框
            "hover": "#F0F4FF"  # 使用浅蓝色悬停效果替代灰色
        }
        
        self.root = root
        self.root.title("英语听写助手")
        self.root.geometry("1024x768")  # 更大的窗口尺寸
        self.root.minsize(800, 600)
        self.root.configure(bg=self.theme["background"])
        
        # 设置窗口图标和视觉效果
        self.root.attributes('-alpha', 1.0)  # 完全不透明
        
        # 绑定回车键提交答案
        self.root.bind('<Return>', lambda event: self.check_answer())
        
        # 初始化变量
        self.word = ""
        self.meaning = ""
        self.mode = None
        # 记录应用启动
        logger.log("应用启动")
        # 初始化统计管理器并加载（隔离状态，避免全局污染）
        try:
            self.stats_manager = StatsManager(
                load_stats, save_stats, get_today_goal, update_today_progress, reset_all_data,
                lambda days=7: get_history_records(days=days), logger
            )
            self.stats = self.stats_manager.snapshot()
            logger.log(f"加载统计信息: {self.stats}")
        except Exception as e:
            logger.log_error(f"加载统计信息失败: {str(e)}")
            self.stats_manager = None
            # 回退到与 data_manager.load_stats() 相同的默认结构
            self.stats = {
                "total_questions": 0,
                "correct_answers": 0,
                "wrong_answers": 0,
                "streak": 0,
                "best_streak": 0
            }
        
        self.hint_used = False
        self.history = []
        self.session_index = None
        self.current_page = None
        self.page_stack = []
        
        # 设置ttk主题样式
        self._setup_ttk_theme()

        # 创建可滚动页面容器（Canvas + inner frame），支持小窗口垂直滚动
        class ScrollableFrame(ttk.Frame):
            def __init__(self, master, **kw):
                super().__init__(master, **kw)
                self.canvas = tk.Canvas(self, bg=master['bg'], highlightthickness=0)
                self.v_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
                self.canvas.configure(yscrollcommand=self.v_scroll.set)
                # 内部承载 Frame，通过 create_window 嵌入到 canvas
                self.inner = ttk.Frame(self.canvas)
                self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor='nw')

                self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

                # 更新滚动区域并根据内容高度自动显示/隐藏滚动条
                def _on_inner_config(event):
                    # 更新 scrollregion
                    try:
                        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
                    except Exception:
                        pass
                    # 尝试根据内容高度决定是否显示滚动条
                    try:
                        bbox = self.canvas.bbox('all')
                        if bbox:
                            content_height = bbox[3] - bbox[1]
                            canvas_h = self.canvas.winfo_height()
                            if content_height <= canvas_h:
                                # 内容高度不超过可见区域 -> 隐藏滚动条
                                try:
                                    self.v_scroll.pack_forget()
                                except Exception:
                                    pass
                            else:
                                # 内容高度超过 -> 显示滚动条
                                try:
                                    self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
                                except Exception:
                                    pass
                    except Exception:
                        pass

                self.inner.bind('<Configure>', _on_inner_config)

                # 当 canvas 大小变化时，确保内层 window 的宽度与 canvas 一致
                def _on_canvas_config(event):
                    try:
                        # 使内层 frame 宽度等于 canvas 可见宽度，避免内容只占左侧窄列
                        self.canvas.itemconfigure(self.inner_id, width=event.width)
                    except Exception:
                        pass
                    # 触发一次内容高度检查（会由 inner 的 configure 调用）
                self.canvas.bind('<Configure>', _on_canvas_config)

                # 支持鼠标滚轮（Windows/Mac/Linux）
                def _on_mousewheel(event):
                    if event.delta:
                        self.canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
                    else:
                        # Linux
                        if event.num == 4:
                            self.canvas.yview_scroll(-1, 'units')
                        elif event.num == 5:
                            self.canvas.yview_scroll(1, 'units')

                # 只绑定到 canvas，这样多个滚动条不会互相冲突
                self.canvas.bind_all('<MouseWheel>', _on_mousewheel)
                self.canvas.bind_all('<Button-4>', _on_mousewheel)
                self.canvas.bind_all('<Button-5>', _on_mousewheel)

        self.container = ScrollableFrame(self.root, style="TFrame")
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建导航栏
        self._create_navigation_bar()

        # 创建所有页面（放到滚动容器的 inner 中）
        self._create_pages()

        # 添加学习记录
        self.session_index = log_start_session()

        # 显示欢迎页
        self.show_page("welcome")

        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

        # 初始化样式引用（由 _setup_ttk_theme 已设置为 self.style）
        # 绑定窗口 resize 事件用于响应式调整（带防抖）
        try:
            self._resize_after_id = None
            self.root.bind('<Configure>', self._schedule_resize)
        except Exception:
            pass

        # 内层白色卡片样式（放在 CardShadow 的上层）
        try:
            self.style.configure(
                "InnerCard.TFrame",
                background=self.theme["card_bg"],
                relief="flat",
                padding=16
            )
        except Exception:
            pass
        
    def wrap_in_inner_card(self, parent, outer_style="CardShadow.TFrame"):
        """创建外部浅色底（outer_style）并在其中放置一个白色内卡片，返回内卡片 frame"""
        outer = ttk.Frame(parent, style=outer_style)
        outer.pack(fill=tk.BOTH, padx=8, pady=8)
        inner = ttk.Frame(outer, style="InnerCard.TFrame")
        inner.pack(fill=tk.BOTH, padx=10, pady=10)
        return inner

    def _schedule_resize(self, event):
        """调度 resize 处理，防抖处理避免频繁更新样式"""
        try:
            if getattr(self, '_resize_after_id', None):
                try:
                    self.root.after_cancel(self._resize_after_id)
                except Exception:
                    pass
            self._resize_after_id = self.root.after(160, self._apply_resize)
        except Exception:
            pass

    def _apply_resize(self):
        """根据窗口宽度应用响应式样式调整（阈值与映射更平滑）"""
        try:
            width = max(200, self.root.winfo_width())

            # 更明确的断点：窄屏、标准、大屏、更大屏
            if width < 800:
                scale = 0.85
            elif width < 1024:
                scale = 0.95
            elif width < 1400:
                scale = 1.05
            else:
                scale = 1.18

            # 字体与尺寸计算
            base_font_size = max(10, int(12 * scale))
            heading_size = max(20, int(34 * scale))
            subheading_size = max(14, int(20 * scale))
            button_font = max(10, int(12 * scale))
            mode_button_font = max(12, int(14 * scale))

            # padding / 间距
            card_outer_pad = int(6 * scale)
            card_inner_pad = int(12 * scale)
            statcard_pad = int(12 * scale)
            mode_button_pad = int(12 * scale)

            # 应用样式更改
            try:
                self.style.configure("TLabel", font=('微软雅黑', base_font_size))
                self.style.configure("Heading.TLabel", font=('微软雅黑', heading_size, 'bold'))
                self.style.configure("Subheading.TLabel", font=('微软雅黑', subheading_size, 'bold'))

                self.style.configure("TButton", font=('微软雅黑', button_font), padding=10)
                self.style.configure("Mode.TButton", font=('微软雅黑', mode_button_font), padding=mode_button_pad)

                # 卡片外层/内层 padding
                self.style.configure("CardShadow.TFrame", padding=card_outer_pad)
                self.style.configure("InnerCard.TFrame", padding=card_inner_pad)
                self.style.configure("StatCard.TFrame", padding=statcard_pad)
                # 历史记录表格行样式
                self.style.configure("RowEven.TFrame", background=self.theme["bg_light"])
                self.style.configure("RowOdd.TFrame", background=self.theme["bg_dark"])

                # 进度条厚度
                try:
                    self.style.configure("Accent.Horizontal.TProgressbar", thickness=max(8, int(12 * scale)))
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            pass
        
    def _create_todo_list_page(self):
        """创建待办事项页面，显示每日学习目标和进度"""
        page = self.pages["todo"]

        # 主容器占满页面宽度，内部使用 grid 管理具体布局
        main_container = ttk.Frame(page, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 设置 main_container 的网格布局
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=5)
        main_container.grid_rowconfigure(2, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # 创建标题
        title_label = ttk.Label(
            main_container,
            text="📝 每日学习目标",
            style="Heading.TLabel"
        )
        title_label.grid(row=0, column=0, pady=(20, 10), sticky="N")

        # 创建统计卡片容器
        content_container = ttk.Frame(main_container, style="CardShadow.TFrame")
        content_container.grid(row=1, column=0, pady=15, padx=30, sticky="NSEW")
        content_container.grid_rowconfigure(0, weight=2)
        content_container.grid_rowconfigure(1, weight=1)
        content_container.grid_columnconfigure(0, weight=1)

        # 创建进度显示区域
        progress_frame = ttk.Frame(content_container, style="TFrame")
        progress_frame.grid(row=0, column=0, padx=30, pady=20, sticky="NSEW")
        
        ttk.Label(progress_frame, text="今日学习进度", font=("微软雅黑", 18, "bold"), foreground=self.theme["text"]).pack(pady=(0, 20))
        
        # 获取今日目标数据
        try:
            from data_manager import get_today_goal
            today_goal = get_today_goal()
            current = today_goal["current"]
            target = today_goal["target"]
            percentage = today_goal["percentage"]
        except Exception:
            current = 0
            target = 20
            percentage = 0
        
        # 创建进度条
        self.todo_progress_var = tk.DoubleVar(value=percentage)
        progress_bar = ttk.Progressbar(progress_frame, variable=self.todo_progress_var, maximum=100, length=400, style="Accent.Horizontal.TProgressbar")
        progress_bar.pack(pady=20, fill=tk.X)
        
        # 显示进度文本
        progress_text_frame = ttk.Frame(progress_frame)
        progress_text_frame.pack(fill=tk.X, pady=10)
        
        # 当前进度
        progress_left_frame = ttk.Frame(progress_text_frame)
        progress_left_frame.pack(side=tk.LEFT, anchor="w")
        ttk.Label(progress_left_frame, text="当前进度:", font=("微软雅黑", 14), foreground=self.theme["text_light"]).pack(side=tk.LEFT)
        self.todo_current_label = ttk.Label(progress_left_frame, text=str(current), font=("微软雅黑", 24, "bold"), foreground=self.theme["primary"])
        self.todo_current_label.pack(side=tk.LEFT, padx=10)
        ttk.Label(progress_left_frame, text="个单词", font=("微软雅黑", 14), foreground=self.theme["text_light"]).pack(side=tk.LEFT)
        
        # 目标数量
        progress_right_frame = ttk.Frame(progress_text_frame)
        progress_right_frame.pack(side=tk.RIGHT, anchor="e")
        ttk.Label(progress_right_frame, text="目标:", font=("微软雅黑", 14), foreground=self.theme["text_light"]).pack(side=tk.LEFT)
        self.todo_target_label = ttk.Label(progress_right_frame, text=str(target), font=("微软雅黑", 24, "bold"), foreground=self.theme["accent"])
        self.todo_target_label.pack(side=tk.LEFT, padx=10)
        ttk.Label(progress_right_frame, text="个单词", font=("微软雅黑", 14), foreground=self.theme["text_light"]).pack(side=tk.LEFT)
        
        # 显示百分比
        percentage_label = ttk.Label(progress_frame, text=f"进度: {percentage}%", font=("微软雅黑", 16, "bold"), foreground=self.theme["success"])
        percentage_label.pack(pady=(20, 10))

        # 创建目标设置区域
        settings_frame = ttk.Frame(content_container, style="TFrame")
        settings_frame.grid(row=1, column=0, padx=30, pady=20, sticky="NSEW")
        
        ttk.Label(settings_frame, text="设置每日目标", font=("微软雅黑", 16, "bold"), foreground=self.theme["text"]).pack(anchor="w", pady=(0, 20))
        
        # 目标输入框
        input_frame = ttk.Frame(settings_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="每日单词目标:", font=("微软雅黑", 14), foreground=self.theme["text"]).pack(side=tk.LEFT, padx=(0, 15))
        
        # 目标输入框变量
        self.target_var = tk.StringVar(value=str(target))
        target_entry = ttk.Entry(input_frame, textvariable=self.target_var, width=10, font=("微软雅黑", 14), style="Custom.TEntry")
        target_entry.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(input_frame, text="个单词", font=("微软雅黑", 14), foreground=self.theme["text"]).pack(side=tk.LEFT)
        
        # 保存按钮
        def save_target():
            try:
                new_target = int(self.target_var.get())
                if new_target <= 0:
                    messagebox.showerror("错误", "请输入有效的目标数量（大于0）")
                    return
                
                from data_manager import update_daily_target
                update_daily_target(new_target)
                
                # 更新显示
                today_goal = get_today_goal()
                self.todo_target_label.config(text=str(today_goal["target"]))
                self.todo_progress_var.set(today_goal["percentage"])
                
                messagebox.showinfo("成功", f"每日目标已更新为 {new_target} 个单词")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
            except Exception as e:
                messagebox.showerror("错误", f"保存目标失败: {str(e)}")
        
        save_btn = ttk.Button(input_frame, text="保存", command=save_target, style="Primary.TButton")
        save_btn.pack(side=tk.RIGHT, padx=20)

        # 维护今日进度区域
        ttk.Label(settings_frame, text="维护今日进度", font=("微软雅黑", 16, "bold"), foreground=self.theme["text"]).pack(anchor="w", pady=(20, 10))
        maintain_frame = ttk.Frame(settings_frame)
        maintain_frame.pack(fill=tk.X, pady=10)

        def refresh_today_goal_ui():
            try:
                from data_manager import get_today_goal
                tg = get_today_goal()
                if hasattr(self, 'todo_progress_var'):
                    try:
                        self.todo_progress_var.set(tg.get('percentage', 0))
                    except Exception:
                        pass
                if hasattr(self, 'todo_current_label'):
                    self.todo_current_label.config(text=str(tg.get('current', 0)))
                if hasattr(self, 'todo_target_label'):
                    self.todo_target_label.config(text=str(tg.get('target', 20)))
                # 同步统计页的进度卡片（如果存在）
                try:
                    if hasattr(self, 'daily_progress_var'):
                        current = tg.get('current', 0)
                        target = tg.get('target', 20)
                        percentage = min(100, (current / target) * 100) if target > 0 else 0
                        self.daily_progress_var.set(percentage)
                    if hasattr(self, 'daily_goal_label'):
                        self.daily_goal_label.config(text=f"{tg.get('current',0)}/{tg.get('target',20)} 个单词")
                except Exception:
                    pass
            except Exception:
                pass

        def inc_correct():
            try:
                from data_manager import adjust_today_progress
                adjust_today_progress(delta_total=1, delta_correct=1)
                refresh_today_goal_ui()
            except Exception as e:
                messagebox.showerror("错误", f"更新今日进度失败: {e}")

        def inc_wrong():
            try:
                from data_manager import adjust_today_progress
                adjust_today_progress(delta_total=1, delta_correct=0)
                refresh_today_goal_ui()
            except Exception as e:
                messagebox.showerror("错误", f"更新今日进度失败: {e}")

        def dec_correct():
            try:
                from data_manager import adjust_today_progress
                adjust_today_progress(delta_total=-1, delta_correct=-1)
                refresh_today_goal_ui()
            except Exception as e:
                messagebox.showerror("错误", f"更新今日进度失败: {e}")

        def dec_wrong():
            try:
                from data_manager import adjust_today_progress
                adjust_today_progress(delta_total=-1, delta_correct=0)
                refresh_today_goal_ui()
            except Exception as e:
                messagebox.showerror("错误", f"更新今日进度失败: {e}")

        def reset_today():
            try:
                from data_manager import reset_today_history
                reset_today_history()
                refresh_today_goal_ui()
                messagebox.showinfo("成功", "今日进度已重置")
            except Exception as e:
                messagebox.showerror("错误", f"重置今日进度失败: {e}")

        ttk.Button(maintain_frame, text="进度+1（正确）", command=inc_correct, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(maintain_frame, text="进度+1（错误）", command=inc_wrong, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(maintain_frame, text="撤销1（正确）", command=dec_correct, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(maintain_frame, text="撤销1（错误）", command=dec_wrong, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(maintain_frame, text="重置今日进度", command=reset_today, style="Danger.TButton").pack(side=tk.RIGHT, padx=5)

        # 创建按钮区域
        buttons_frame = ttk.Frame(main_container, style="TFrame")
        buttons_frame.grid(row=2, column=0, pady=20, sticky="S")
        
        # 返回按钮
        back_btn = ttk.Button(buttons_frame, text="返回首页", command=lambda: self.show_page("welcome"), style="Primary.TButton")
        back_btn.pack(pady=10)
    
    def toggle_history_table(self):
        """跳转到历史记录页面"""
        # 直接跳转到新的历史记录页面
        self.show_page("history")
    
    def _create_history_page(self):
        """创建历史记录页面，显示每日学习数据"""
        page = self.pages["history"]
        # 清空旧内容以支持刷新
        try:
            for child in page.winfo_children():
                try:
                    child.destroy()
                except Exception:
                    pass
        except Exception:
            pass

        # 主容器占满页面宽度，内部使用 grid 管理具体布局
        main_container = ttk.Frame(page, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 设置 main_container 的网格布局
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=10)
        main_container.grid_rowconfigure(2, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # 创建标题
        title_label = ttk.Label(
            main_container,
            text="📊 历史学习记录",
            style="Heading.TLabel"
        )
        title_label.grid(row=0, column=0, pady=(20, 10), sticky="N")

        # 创建内容卡片容器
        content_container = ttk.Frame(main_container, style="CardShadow.TFrame")
        content_container.grid(row=1, column=0, pady=15, padx=30, sticky="NSEW")
        
        # 创建说明文字
        desc_label = ttk.Label(
            content_container,
            text="以下是您的每日学习记录，数据以每日结束或最后一次关闭应用为准",
            font=("微软雅黑", 12),
            foreground=self.theme["text_light"]
        )
        desc_label.pack(pady=15, padx=20, anchor="w")
        
        # 创建表格区域，使用带滚动条的框架
        table_frame = ttk.Frame(content_container, style="TFrame")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建水平和垂直滚动条
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # 创建画布，设置滚动条命令
        canvas = tk.Canvas(
            table_frame,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # 配置滚动条
        v_scrollbar.config(command=canvas.yview)
        h_scrollbar.config(command=canvas.xview)
        
        # 创建可滚动框架
        scrollable_frame = ttk.Frame(canvas)
        
        # 创建窗口，确保框架可以水平扩展，并保存窗口ID
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # 当可滚动框架大小改变时，更新画布的滚动区域
        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 确保画布至少和视口一样宽
            if scrollable_frame.winfo_width() < canvas.winfo_width():
                canvas.itemconfig(window_id, width=canvas.winfo_width())
        
        scrollable_frame.bind("<Configure>", update_scrollregion)
        
        # 当画布大小改变时，检查是否需要调整窗口宽度
        def on_canvas_configure(event):
            # 确保画布宽度适应表格框架
            width = event.width
            # 更新窗口宽度以适应画布，使用保存的窗口ID
            canvas.itemconfig(window_id, width=width)
            # 更新滚动区域
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        # 放置滚动条和画布
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 确保表格有最小宽度
        min_width = 600  # 设置最小宽度以确保三列内容合理显示
        scrollable_frame.grid_columnconfigure(0, minsize=min_width)
        
        # 创建表格头部 - 三列布局：日期、每日答题数、准确率
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建一个固定宽度的容器，确保表格列对齐
        table_width = 600  # 表格总宽度
        col_widths = {0: 200, 1: 200, 2: 200}  # 各列宽度
        
        # 设置三列布局，保持适当的宽度比例
        header_frame.grid_columnconfigure(0, minsize=col_widths[0])  # 日期列
        header_frame.grid_columnconfigure(1, minsize=col_widths[1])  # 每日答题数列
        header_frame.grid_columnconfigure(2, minsize=col_widths[2])  # 准确率列
        
        # 日期列标题
        ttk.Label(
            header_frame,
            text="日期",
            font=("微软雅黑", 14, "bold"),
            foreground=self.theme["text"]
        ).grid(row=0, column=0, padx=15, pady=10, sticky="W")
        
        # 每日答题数列标题
        ttk.Label(
            header_frame,
            text="每日答题数",
            font=("微软雅黑", 14, "bold"),
            foreground=self.theme["text"]
        ).grid(row=0, column=1, padx=15, pady=10, sticky="W")
        
        # 准确率列标题
        ttk.Label(
            header_frame,
            text="准确率",
            font=("微软雅黑", 14, "bold"),
            foreground=self.theme["text"]
        ).grid(row=0, column=2, padx=15, pady=10, sticky="W")
        
        # 绘制分割线
        separator = ttk.Separator(scrollable_frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=5)
        
        try:
            if getattr(self, 'stats_manager', None):
                history_records = self.stats_manager.history_records(days=30)
            else:
                history_records = get_history_records(days=30)
            
            # 按日期倒序排列（最新的在前）
            history_records.sort(key=lambda x: x["date"], reverse=True)
            
            # 填充数据行
            for row_idx, record in enumerate(history_records):
                # 为交替行设置不同的背景色
                row_style = "RowEven.TFrame" if row_idx % 2 == 0 else "RowOdd.TFrame"
                row_frame = ttk.Frame(scrollable_frame, style=row_style)
                row_frame.pack(fill=tk.X, pady=2, padx=5)
                
                # 设置行内三列布局，保持与表头一致的宽度比例
                row_frame.grid_columnconfigure(0, minsize=col_widths[0])
                row_frame.grid_columnconfigure(1, minsize=col_widths[1])
                row_frame.grid_columnconfigure(2, minsize=col_widths[2])
                
                # 日期
                ttk.Label(
                    row_frame,
                    text=record["date"],
                    font=("微软雅黑", 14),
                    foreground=self.theme["text"]
                ).grid(row=0, column=0, padx=15, pady=12, sticky="W")
                
                # 每日答题数
                ttk.Label(
                    row_frame,
                    text=str(record["total"]),
                    font=("微软雅黑", 14, "bold"),
                    foreground=self.theme["primary"]
                ).grid(row=0, column=1, padx=15, pady=12, sticky="W")
                
                # 准确率
                accuracy_color = self.theme["success"] if record["accuracy"] >= 80 else \
                                self.theme["warning"] if record["accuracy"] >= 60 else self.theme["error"]
                ttk.Label(
                    row_frame,
                    text=f"{record['accuracy']}%",
                    font=("微软雅黑", 14, "bold"),
                    foreground=accuracy_color
                ).grid(row=0, column=2, padx=15, pady=12, sticky="W")
            
            # 如果没有历史记录
            if not history_records:
                empty_frame = ttk.Frame(scrollable_frame)
                empty_frame.pack(fill=tk.BOTH, expand=True, pady=40)
                ttk.Label(
                    empty_frame,
                    text="暂无历史学习记录",
                    font=("微软雅黑", 16),
                    foreground=self.theme["text_light"]
                ).pack()
                ttk.Label(
                    empty_frame,
                    text="开始学习后，系统将自动记录您的每日学习数据",
                    font=("微软雅黑", 12),
                    foreground=self.theme["text_light"]
                ).pack(pady=10)
        
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            error_frame = ttk.Frame(scrollable_frame)
            error_frame.pack(fill=tk.BOTH, expand=True, pady=40)
            ttk.Label(
                error_frame,
                text="加载历史记录失败",
                font=("微软雅黑", 14),
                foreground=self.theme["error"]
            ).pack()
        
        # 按钮区域
        buttons_frame = ttk.Frame(main_container, style="TFrame")
        buttons_frame.grid(row=2, column=0, pady=20, sticky="S")
        
        # 返回按钮
        back_btn = ttk.Button(
            buttons_frame,
            text="返回统计页面",
            command=lambda: self.show_page("stats"),
            style="Primary.TButton",
            padding=12
        )
        back_btn.pack(pady=10)
        self.add_hover_effect(back_btn)
    
    def _create_stats_page(self):
        """创建统计页面"""
        # 使用全局 logger 实例（在模块顶层已导入）
        global logger
        page = self.pages["stats"]

        # 主容器占满页面宽度，内部使用 grid 管理具体布局
        main_container = ttk.Frame(page, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 设置 main_container 的网格布局
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=10)
        main_container.grid_rowconfigure(2, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # 标题
        title_label = ttk.Label(main_container, text="📊 学习统计", style="Heading.TLabel")
        title_label.grid(row=0, column=0, pady=(20, 10), sticky="N")

        # 统计卡片容器
        stats_container = ttk.Frame(main_container, style="CardShadow.TFrame")
        stats_container.grid(row=1, column=0, pady=15, padx=30, sticky="NSEW")
        stats_container.grid_rowconfigure(0, weight=1)
        stats_container.grid_rowconfigure(1, weight=3)
        stats_container.grid_rowconfigure(2, weight=3)
        stats_container.grid_rowconfigure(3, weight=4)
        stats_container.grid_columnconfigure(0, weight=1)
        stats_container.grid_columnconfigure(1, weight=1)

        # 主统计标题（可更新）
        self.stats_label = ttk.Label(stats_container, text=self.get_stats_text(), style="Subheading.TLabel")
        self.stats_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="N")

        # 基础统计卡片
        basic_stats_frame = ttk.Frame(stats_container)
        basic_stats_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="NSEW")
        basic_stats_frame.grid_columnconfigure(0, weight=1)
        basic_stats_frame.grid_columnconfigure(1, weight=1)

        # 卡片1 - 总答题数与正确率
        card1 = ttk.Frame(basic_stats_frame, style="StatCard.TFrame")
        card1.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")
        ttk.Label(card1, text="总答题数", font=("微软雅黑", 14, "bold"), foreground=self.theme["text"]).pack(pady=5)
        self.total_questions_label = ttk.Label(card1, text=str(self.stats.get('total_questions', 0)), font=("微软雅黑", 28, "bold"), foreground=self.theme["primary"]) 
        self.total_questions_label.pack(pady=5)

        # 正确率
        accuracy = 0
        if self.stats.get("total_questions", 0) > 0:
            accuracy = round(self.stats.get("correct_answers", 0) / self.stats.get("total_questions", 1) * 100, 1)
        accuracy_frame = ttk.Frame(card1)
        accuracy_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(accuracy_frame, text="正确率", font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(anchor="w")
        self.accuracy_progress_var = tk.DoubleVar(value=accuracy)
        self.accuracy_progress_bar = ttk.Progressbar(accuracy_frame, variable=self.accuracy_progress_var, maximum=100, style="Accent.Horizontal.TProgressbar")
        self.accuracy_progress_bar.pack(fill=tk.X, pady=5)
        self.accuracy_percent_label = ttk.Label(accuracy_frame, text=f"{accuracy}%", font=("微软雅黑", 12, "bold"), foreground=self.theme["success"]) 
        self.accuracy_percent_label.pack(anchor="e")

        # 卡片2 - 详细数字
        card2 = ttk.Frame(basic_stats_frame, style="StatCard.TFrame")
        card2.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")

        # 保存可更新标签
        stats_frame_inner = ttk.Frame(card2)
        stats_frame_inner.pack(fill=tk.X, padx=20, pady=8)
        ttk.Label(stats_frame_inner, text="正确答案", font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(side=tk.LEFT)
        self.correct_label = ttk.Label(stats_frame_inner, text=str(self.stats.get('correct_answers', 0)), font=("微软雅黑", 18, "bold"), foreground=self.theme["success"]) 
        self.correct_label.pack(side=tk.RIGHT)

        stats_frame_inner2 = ttk.Frame(card2)
        stats_frame_inner2.pack(fill=tk.X, padx=20, pady=8)
        ttk.Label(stats_frame_inner2, text="错误答案", font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(side=tk.LEFT)
        self.wrong_label = ttk.Label(stats_frame_inner2, text=str(self.stats.get('wrong_answers', 0)), font=("微软雅黑", 18, "bold"), foreground=self.theme["error"]) 
        self.wrong_label.pack(side=tk.RIGHT)

        stats_frame_inner3 = ttk.Frame(card2)
        stats_frame_inner3.pack(fill=tk.X, padx=20, pady=8)
        ttk.Label(stats_frame_inner3, text="当前连续正确", font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(side=tk.LEFT)
        self.streak_label = ttk.Label(stats_frame_inner3, text=str(self.stats.get('streak', 0)), font=("微软雅黑", 18, "bold"), foreground=self.theme["primary"]) 
        self.streak_label.pack(side=tk.RIGHT)

        stats_frame_inner4 = ttk.Frame(card2)
        stats_frame_inner4.pack(fill=tk.X, padx=20, pady=8)
        ttk.Label(stats_frame_inner4, text="最高连续正确", font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(side=tk.LEFT)
        self.best_streak_label = ttk.Label(stats_frame_inner4, text=str(self.stats.get('best_streak', 0)), font=("微软雅黑", 18, "bold"), foreground=self.theme["accent"]) 
        self.best_streak_label.pack(side=tk.RIGHT)

        # 使用时间与单词统计卡片
        time_words_frame = ttk.Frame(stats_container)
        time_words_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="NSEW")
        time_words_frame.grid_columnconfigure(0, weight=1)
        time_words_frame.grid_columnconfigure(1, weight=1)

        # 卡片3 - 使用时间
        card3 = ttk.Frame(time_words_frame, style="StatCard.TFrame")
        card3.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")
        ttk.Label(card3, text="使用时间统计", font=("微软雅黑", 14, "bold"), foreground=self.theme["text"]).pack(pady=10)
        if logger and hasattr(logger, 'session_log'):
            try:
                duration = logger.session_log.get('duration_seconds', 0)
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{int(hours)}小时 {int(minutes)}分钟"
                time_items = [
                    {"label": "本次会话时长", "value": time_str},
                    {"label": "开始时间", "value": logger.session_log.get('start_time', '未知')}
                ]
                for item in time_items:
                    item_frame = ttk.Frame(card3)
                    item_frame.pack(fill=tk.X, padx=20, pady=8)
                    ttk.Label(item_frame, text=item["label"], font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(side=tk.LEFT, anchor="w")
                    ttk.Label(item_frame, text=str(item["value"]), font=("微软雅黑", 12, "bold"), foreground=self.theme["primary"]).pack(side=tk.LEFT, padx=10, anchor="w")
            except Exception:
                ttk.Label(card3, text="暂无使用时间数据", font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(pady=20)
        else:
            ttk.Label(card3, text="暂无使用时间数据", font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(pady=20)

        # 卡片4 - 单词统计
        card4 = ttk.Frame(time_words_frame, style="StatCard.TFrame")
        card4.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")
        ttk.Label(card4, text="单词统计", font=("微软雅黑", 14, "bold"), foreground=self.theme["text"]).pack(pady=10)
        total_words = 0
        if logger and hasattr(logger, 'total_words'):
            total_words = logger.total_words
        today_words = total_words
        word_items = [
            {"label": "总背单词数", "value": total_words, "color": self.theme["primary"]},
            {"label": "当日背单词数", "value": today_words, "color": self.theme["success"]}
        ]

        # 当日进度条（提前获取今日目标数据）
        try:
            today_goal = get_today_goal()
            target_words = today_goal.get("target", 20)
            today_progress = today_goal.get("current", 0)
        except Exception:
            target_words = 20
            today_progress = today_words

        percentage = min(100, (today_progress / target_words) * 100) if target_words > 0 else 0

        # 进度条区域
        bar_frame = ttk.Frame(card4)
        bar_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(bar_frame, text="今日进度", font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(anchor="w", pady=(0, 5))
        self.daily_progress_var = tk.DoubleVar(value=percentage)
        self.daily_progress_bar = ttk.Progressbar(bar_frame, variable=self.daily_progress_var, maximum=100, style="Accent.Horizontal.TProgressbar")
        self.daily_progress_bar.pack(fill=tk.X, pady=5)
        self.daily_goal_label = ttk.Label(bar_frame, text=f"{today_progress}/{target_words} 个单词", font=("微软雅黑", 12), foreground=self.theme["primary"]) 
        self.daily_goal_label.pack(anchor="e")

        for item in word_items:
            item_frame = ttk.Frame(card4)
            item_frame.pack(fill=tk.X, padx=20, pady=8)
            ttk.Label(item_frame, text=item["label"], font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(side=tk.LEFT)
            ttk.Label(item_frame, text=str(item["value"]), font=("微软雅黑", 18, "bold"), foreground=item["color"]).pack(side=tk.RIGHT)

        # 更多按钮
        more_button_frame = ttk.Frame(card4)
        more_button_frame.pack(fill=tk.X, padx=20, pady=10)
        self.history_table_shown = False
        self.history_frame = None
        self.btn_show_more = ttk.Button(more_button_frame, text="显示更多", style="Secondary.TButton", command=self.toggle_history_table, padding=5)
        self.btn_show_more.pack(anchor="e")

        # 模块统计容器，保存为实例属性以便更新
        self.module_stats_frame = ttk.Frame(stats_container)
        self.module_stats_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="NSEW")
        self.module_stats_title = ttk.Label(self.module_stats_frame, text="各模块使用统计", font=("微软雅黑", 16, "bold"), foreground=self.theme["text"])
        self.module_stats_title.pack(pady=10, anchor="w")

        # 渲染模块统计（统一来源：优先使用 logger.module_stats，否则为空）
        try:
            module_stats = {}
            if logger and hasattr(logger, 'module_stats'):
                module_stats = logger.module_stats or {}

            # 计算总数与百分比
            total_all = sum(m.get("total", 0) for m in module_stats.values()) if module_stats else 0
            module_percentage = {}
            if total_all > 0:
                for module, stats in module_stats.items():
                    module_percentage[module] = round((stats.get("total", 0) / total_all) * 100, 1)
            else:
                module_percentage = {module: 0 for module in module_stats}

            module_names = {"E2C": "英译汉", "C2E": "汉译英", "LISTEN": "听写拼写", "review": "错题复习"}

            for module, stats in (module_stats or {}).items():
                perc = module_percentage.get(module, 0)
                module_frame = ttk.Frame(self.module_stats_frame, style="StatCard.TFrame")
                module_frame.pack(fill=tk.X, padx=10, pady=8)

                # 左侧：模块名称与小信息
                left_frame = ttk.Frame(module_frame)
                left_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.X, expand=True)
                module_name = module_names.get(module, module)
                ttk.Label(left_frame, text=module_name, font=("微软雅黑", 14, "bold"), foreground=self.theme["text"]).pack(anchor="w")
                total = stats.get("total", 0)
                correct = stats.get("correct", 0)
                accuracy = round((correct / total) * 100, 1) if total > 0 else 0
                ttk.Label(left_frame, text=f"答题: {total} 次 | 正确率: {accuracy}%", font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(anchor="w", pady=(2, 0))

                # 右侧：大号百分比样式（粉色/强调色）
                right_frame = ttk.Frame(module_frame)
                right_frame.pack(side=tk.RIGHT, padx=20, pady=10)
                ttk.Label(right_frame, text=f"{perc}%", font=("微软雅黑", 20, "bold"), foreground=self.theme["accent"]).pack(anchor="e")
        except Exception:
            # 如果任何步骤失败，静默失败以不影响页面其它内容
            pass
            
            # 比例进度条
            progress_var = tk.DoubleVar(value=percentage)
            # 创建一个进度条容器，增加进度条的视觉高度和居中效果
            progress_container = ttk.Frame(module_frame)
            # 增加上方间距（更往下），减少左右内边距（更长）
            progress_container.pack(fill=tk.X, padx=0, pady=(20, 15))
            # 在容器中放置进度条，增加高度和更好的居中显示
            progress_bar = ttk.Progressbar(progress_container, variable=progress_var, maximum=100, style="Accent.Horizontal.TProgressbar")
            progress_bar.pack(fill=tk.X, expand=True, pady=5)
        
        # 按钮区域（放在 main_container 中以避免与 page 的 pack 冲突）
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.grid(row=2, column=0, pady=20)
        
        # 创建重置按钮
        reset_button = ttk.Button(
            buttons_frame,
            text="🔄 重置统计",
            command=self.reset_stats,
            style="Danger.TButton",
            padding=15
        )
        reset_button.pack(side=tk.LEFT, padx=15)
        
        # 创建返回首页按钮
        back_button = ttk.Button(
            buttons_frame,
            text="🏠 返回首页",
            style="Primary.TButton",
            padding=15,
            command=lambda: self.show_page("welcome")
        )
        back_button.pack(side=tk.LEFT, padx=15)
        
        # 添加按钮悬停效果
        self.add_hover_effect(reset_button)
        self.add_hover_effect(back_button)
    
    def set_mode(self, mode):
        """设置学习模式"""
        self.mode = mode
    
    def show_page(self, page_name):
        """显示指定页面，实现平滑的页面切换效果"""
        if page_name in self.pages:
            # 隐藏当前页面
            if self.current_page:
                # 添加淡出动画
                for i in range(10, -1, -1):
                    opacity = i / 10
                    self.pages[self.current_page].configure(style=f"Transparent{i}.TFrame")
                    self.root.update()
                    time.sleep(0.02)
                
                self.pages[self.current_page].pack_forget()
                
                # 如果不是直接跳转到首页，才将当前页加入堆栈
                if page_name != "welcome":
                    self.page_stack.append(self.current_page)
                else:
                    # 跳转到首页时清空堆栈
                    self.page_stack = []
            else:
                self.page_stack = []
            
            # 更新当前页面
            self.current_page = page_name
            
            # 显示新页面（放到滚动容器的 inner）
            self.pages[page_name].pack(in_=self.container.inner, fill=tk.BOTH, expand=True)
            
            # 添加淡入动画
            for i in range(0, 11):
                opacity = i / 10
                self.pages[page_name].configure(style=f"Transparent{i}.TFrame")
                self.root.update()
                time.sleep(0.02)
            
            # 更新导航栏
            self.btn_back.config(state=tk.NORMAL if page_name != "welcome" else tk.DISABLED)
            
            # 更新导航标题
            titles = {
                "welcome": "英语听写助手",
                "learn": f"学习模式 - {self._get_mode_name()}",
                "review": "错题复习",
                "stats": "学习统计",
                "view_wrongs": "错题单词列表"
            }
            self.nav_title.config(text=titles.get(page_name, "英语听写助手"))
            
            # 页面特定初始化
            if page_name == "view_wrongs":
                # 加载错题数据到表格
                self.load_wrong_words_table()
            elif page_name == "learn":
                self._init_learn_page()
            elif page_name == "history":
                # 进入历史记录页时重建内容以加载最新数据
                try:
                    self._create_history_page()
                except Exception:
                    pass
            elif page_name == "stats":
                # 优化更新统计页面 - 只更新必要的数据而不是完全重建页面
                # 先检查是否存在stats_label属性（页面是否已创建）
                if hasattr(self, 'stats_label'):
                    # 更新主统计标签
                    self.stats_label.config(text=self.get_stats_text())
                    
                    # 尝试更新其他统计相关的数据，避免完全重建页面
                    # 这样可以避免每次进入页面时的刷新效果
                    self._update_stats_data()
    
    def _update_stats_data(self):
        """更新统计页面的数据，而不是完全重建页面"""
        try:
            # 更新准确率统计（如果存在相关标签）
            accuracy = 0
            try:
                if getattr(self, 'stats_manager', None):
                    accuracy = self.stats_manager.accuracy()
                else:
                    if self.stats["total_questions"] > 0:
                        accuracy = round(self.stats["correct_answers"] / self.stats["total_questions"] * 100, 1)
            except Exception:
                accuracy = 0
            
            # 更新每日目标相关数据（如果存在）
            if hasattr(self, 'daily_goal_label'):
                try:
                    tg = get_today_goal()
                    today_progress = tg.get('current', 0)
                    target_words = tg.get('target', 20)
                except Exception:
                    today_progress = 0
                    target_words = 20
                self.daily_goal_label.config(text=f"今日目标: {today_progress}/{target_words} 个单词")
            
            # 同步更新统计卡片上的各项数值（进入统计页时也要即时刷新）
            try:
                if hasattr(self, 'total_questions_label'):
                    self.total_questions_label.config(text=str(self.stats.get('total_questions', 0)))
                if hasattr(self, 'correct_label'):
                    self.correct_label.config(text=str(self.stats.get('correct_answers', 0)))
                if hasattr(self, 'wrong_label'):
                    self.wrong_label.config(text=str(self.stats.get('wrong_answers', 0)))
                if hasattr(self, 'streak_label'):
                    self.streak_label.config(text=str(self.stats.get('streak', 0)))
                if hasattr(self, 'best_streak_label'):
                    self.best_streak_label.config(text=str(self.stats.get('best_streak', 0)))
                if hasattr(self, 'accuracy_progress_var'):
                    try:
                        self.accuracy_progress_var.set(accuracy)
                    except Exception:
                        pass
                if hasattr(self, 'accuracy_percent_label'):
                    self.accuracy_percent_label.config(text=f"{accuracy}%")
                # 立即刷新界面，确保数值及时呈现
                if hasattr(self, 'root'):
                    try:
                        self.root.update_idletasks()
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            pass

        # 更新模块统计数据（统计页）
        try:
            if hasattr(self, 'module_stats_frame'):
                module_stats = {}
                module_percentage = {}
                try:
                    if logger and hasattr(logger, 'module_stats'):
                        module_stats = logger.module_stats
                        total_all = sum(module.get("total", 0) for module in module_stats.values())
                        if total_all > 0:
                            module_percentage = {m: round((s.get("total", 0) / total_all) * 100, 1) for m, s in module_stats.items()}
                        else:
                            module_percentage = {m: 0 for m in module_stats}
                except Exception:
                    pass

                # 清除现有模块统计标签
                for widget in self.module_stats_frame.winfo_children():
                    if widget != getattr(self, 'module_stats_title', None):
                        widget.destroy()
                
                # 重新创建模块统计标签（左侧为名称与小文字，右侧为大号百分比）
                if module_stats:
                    module_names = {
                        "E2C": "英译汉",
                        "C2E": "汉译英",
                        "LISTEN": "听写拼写",
                        "review": "错题复习"
                    }
                    for module, pct in module_percentage.items():
                        stats = module_stats.get(module, {})
                        module_frame = ttk.Frame(self.module_stats_frame, style="StatCard.TFrame")
                        module_frame.pack(fill=tk.X, padx=10, pady=8)

                        left_frame = ttk.Frame(module_frame)
                        left_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.X, expand=True)
                        module_display_name = module_names.get(module, module)
                        ttk.Label(left_frame, text=module_display_name, font=("微软雅黑", 14, "bold"), foreground=self.theme["text"]).pack(anchor="w")

                        total = stats.get("total", 0)
                        correct = stats.get("correct", 0)
                        accuracy = round((correct / total) * 100, 1) if total > 0 else 0
                        ttk.Label(left_frame, text=f"答题: {total} 次 | 正确率: {accuracy}%", font=("微软雅黑", 12), foreground=self.theme["text_light"]).pack(anchor="w", pady=(2,0))

                        right_frame = ttk.Frame(module_frame)
                        right_frame.pack(side=tk.RIGHT, padx=20, pady=10)
                        ttk.Label(right_frame, text=f"{pct}%", font=("微软雅黑", 20, "bold"), foreground=self.theme["accent"]).pack(anchor="e")
        except Exception:
            # 如果更新失败，保持原样，避免页面崩溃
            pass
    
    def go_back(self):
        """返回上一页"""
        if self.page_stack:
            previous_page = self.page_stack.pop()
            self.show_page(previous_page)
        else:
            self.show_page("welcome")
    
    def _get_mode_name(self):
        """获取当前模式的中文名称"""
        mode_names = {
            "E2C": "英译汉",
            "C2E": "汉译英",
            "LISTEN": "听写拼写",
            "REVIEW": "错题复习"
        }
        return mode_names.get(self.mode, "未知模式")
    
    def _init_learn_page(self):
        """初始化学习页面"""
        self.hint_used = False
        self.btn_hint.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_submit.config(state=tk.NORMAL)
        self.entry.delete(0, tk.END)
        self.entry.focus_set()
        
        # 隐藏听写模式的播放按钮（在各模式方法中根据需要显示）
        self.play_button.pack_forget()
        
        # 确保question_label有正确的前景色
        self.question_label.config(foreground=self.theme["text"])
        
        # 更新当前统计显示
        if hasattr(self, 'current_stats_label'):
            accuracy = 0
            if self.stats["total_questions"] > 0:
                accuracy = round(self.stats["correct_answers"] / self.stats["total_questions"] * 100, 1)
            self.current_stats_label.config(
                text=f"总题数: {self.stats['total_questions']} | 正确率: {accuracy}% | 连续正确: {self.stats['streak']}"
            )
        
        # 初始化模块使用率统计显示
        if hasattr(self, 'module_usage_label'):
            try:
                global logger
                # 获取当前模块名称
                current_module = self.mode if self.mode != "REVIEW" else "review"
                # 获取各模块统计数据
                total_all = sum(module["total"] for module in logger.module_stats.values())
                current_percentage = 0
                if total_all > 0:
                    current_module_total = logger.module_stats.get(current_module, {}).get("total", 0)
                    current_percentage = round((current_module_total / total_all) * 100, 1)
                self.module_usage_label.config(
                    text=f"当前模块使用率: {current_percentage}%"
                )
            except Exception:
                # 如果获取失败，保持默认显示
                self.module_usage_label.config(text="当前模块使用率: 0%")
        
        # 根据模式初始化
        if self.mode == "E2C":
            self.english_to_chinese()
        elif self.mode == "C2E":
            self.chinese_to_english()
        elif self.mode == "LISTEN":
            self.listen_and_spell()
        # 清除反馈标签（如果存在）
        try:
            if hasattr(self, 'feedback_label') and self.feedback_label.winfo_exists():
                self.feedback_label.destroy()
        except Exception:
            pass
    
    def _create_view_wrongs_page(self):
        """创建查看所有错题页面，以表格形式展示"""
        page = self.pages["view_wrongs"]

        # 主容器占满页面宽度
        main_container = ttk.Frame(page, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 设置主容器的网格布局
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=0)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_rowconfigure(2, weight=0)
        
        # 标题区域
        title_frame = ttk.Frame(main_container, style="TFrame")
        title_frame.grid(row=0, column=0, sticky="EW", pady=(0, 15))
        
        title_label = ttk.Label(
            title_frame,
            text="错题单词列表",
            font=('微软雅黑', 24, 'bold'),
            foreground=self.theme["primary"]
        )
        title_label.pack(anchor=tk.W)
        
        # 表格区域，使用带滚动条的框架
        table_frame = ttk.Frame(main_container, style="CardShadow.TFrame")
        table_frame.grid(row=1, column=0, sticky="NSEW", pady=(0, 15))
        
        # 设置表格区域的网格布局
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # 创建滚动条
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # 创建表格（Treeview）
        self.wrong_words_tree = ttk.Treeview(
            table_frame,
            columns=("word", "meaning"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        # 设置列标题
        self.wrong_words_tree.heading("word", text="英语单词")
        self.wrong_words_tree.heading("meaning", text="中文翻译")
        
        # 设置列宽
        self.wrong_words_tree.column("word", width=200, anchor=tk.CENTER)
        self.wrong_words_tree.column("meaning", width=300, anchor=tk.CENTER)
        
        # 放置表格和滚动条
        self.wrong_words_tree.grid(row=0, column=0, sticky="NSEW")
        scrollbar_y.grid(row=0, column=1, sticky="NS")
        scrollbar_x.grid(row=1, column=0, sticky="EW")
        
        # 配置滚动条
        scrollbar_y.config(command=self.wrong_words_tree.yview)
        scrollbar_x.config(command=self.wrong_words_tree.xview)
        
        # 按钮区域
        buttons_frame = ttk.Frame(main_container, style="TFrame")
        buttons_frame.grid(row=2, column=0, sticky="EW")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        
        # 刷新按钮
        btn_refresh = ttk.Button(
            buttons_frame,
            text="刷新列表",
            style="Secondary.TButton",
            padding=15,
            command=self.load_wrong_words_table
        )
        btn_refresh.grid(row=0, column=0, sticky="EW", padx=(0, 10))
        self.add_hover_effect(btn_refresh)
        
        # 导出CSV按钮
        btn_export_csv = ttk.Button(
            buttons_frame,
            text="导出为CSV",
            style="Primary.TButton",
            padding=15,
            command=self.export_wrong_words_to_csv
        )
        btn_export_csv.grid(row=0, column=1, sticky="EW", padx=(10, 10))
        self.add_hover_effect(btn_export_csv)
        
        # 清除错题数据按钮
        btn_clear_wrongs = ttk.Button(
            buttons_frame,
            text="清除错题数据",
            style="Danger.TButton",
            padding=15,
            command=self.clear_wrong_words_data
        )
        btn_clear_wrongs.grid(row=0, column=2, sticky="EW", padx=(10, 0))
        self.add_hover_effect(btn_clear_wrongs)
    
    def load_wrong_words_table(self):
        import os
        import json
        """加载错题单词到表格中"""
        # 清空现有数据
        for item in self.wrong_words_tree.get_children():
            self.wrong_words_tree.delete(item)
        
        # 加载错题数据
        wrong_words = []
        try:
            # 确保文件存在并且不为空
            if os.path.exists(WRONG_FILE) and os.path.getsize(WRONG_FILE) > 0:
                with open(WRONG_FILE, "r", encoding="utf-8") as f:
                    wrong_words = json.load(f)
                    # 确保加载的数据是列表类型
                    if not isinstance(wrong_words, list):
                        wrong_words = []
            
            # 填充表格
            if wrong_words:
                for i, item in enumerate(wrong_words, 1):
                    # 安全地获取键值对
                    if isinstance(item, dict) and item:
                        word = list(item.keys())[0]
                        meaning = item[word]
                        # 处理meaning可能是列表的情况
                        if isinstance(meaning, list) and meaning:
                            meaning = meaning[0]
                        elif isinstance(meaning, list):
                            meaning = "暂无翻译"
                        self.wrong_words_tree.insert("", tk.END, values=(word, meaning))
                    else:
                        self.wrong_words_tree.insert("", tk.END, values=("数据格式错误", "忽略此项"))
            else:
                # 如果没有错题，显示提示信息
                self.wrong_words_tree.insert("", tk.END, values=("暂无错题记录", "继续努力学习吧！"))
        except json.JSONDecodeError:
            messagebox.showerror("错误", "错题文件格式错误")
            self.wrong_words_tree.insert("", tk.END, values=("文件格式错误", "请检查错题文件"))
        except Exception as e:
            messagebox.showerror("错误", f"加载错题数据失败: {str(e)}")
            self.wrong_words_tree.insert("", tk.END, values=("加载失败", str(e)))
    
    def export_wrong_words_to_csv(self):
        import os
        import json
        from tkinter import filedialog
        """导出错题单词为CSV文件"""
        # 加载错题数据
        wrong_words = []
        try:
            # 确保文件存在并且不为空
            if os.path.exists(WRONG_FILE) and os.path.getsize(WRONG_FILE) > 0:
                with open(WRONG_FILE, "r", encoding="utf-8") as f:
                    wrong_words = json.load(f)
                    # 确保加载的数据是列表类型
                    if not isinstance(wrong_words, list):
                        wrong_words = []
            
            if not wrong_words:
                messagebox.showinfo("提示", "没有错题记录可导出")
                return
            
            # 让用户选择CSV文件保存位置
            csv_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
                title="导出错题记录",
                initialfile="wrong_words_export.csv"
            )
            
            # 处理用户取消保存的情况
            if not csv_file:
                return
            
            # 写入CSV文件
            with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(["序号", "英语单词", "中文翻译"])
                # 写入数据
                valid_count = 0
                for i, item in enumerate(wrong_words, 1):
                    # 安全地获取键值对
                    if isinstance(item, dict) and item:
                        word = list(item.keys())[0]
                        meaning = item[word]
                        # 处理meaning可能是列表的情况
                        if isinstance(meaning, list) and meaning:
                            meaning = meaning[0]
                        elif isinstance(meaning, list):
                            meaning = "暂无翻译"
                        writer.writerow([i, word, meaning])
                        valid_count += 1
            
            if valid_count > 0:
                messagebox.showinfo("成功", f"错题单词已成功导出到 {csv_file}\n共导出 {valid_count} 条记录")
            else:
                messagebox.showinfo("提示", "没有有效的错题记录可导出")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "错题文件格式错误，请检查文件内容")
        except PermissionError:
            messagebox.showerror("错误", "没有权限写入文件，请关闭可能占用该文件的程序")
        except Exception as e:
            messagebox.showerror("错误", f"导出CSV文件失败: {str(e)}")
    
    def clear_wrong_words_data(self):
        """清除错题数据"""
        if messagebox.askyesno("确认", "确定要清除所有错题数据吗？此操作不可恢复。"):
            try:
                import os
                import json
                
                # 清空错题文件
                if os.path.exists(WRONG_FILE):
                    with open(WRONG_FILE, "w", encoding="utf-8") as f:
                        json.dump([], f, ensure_ascii=False, indent=2)
                    logger.log("错题记录已清空")
                
                # 更新表格显示
                # 清空现有表格数据
                for item in self.wrong_words_tree.get_children():
                    self.wrong_words_tree.delete(item)
                # 添加空状态提示
                self.wrong_words_tree.insert("", tk.END, values=("暂无错题记录", "继续努力学习吧！"))
                
                messagebox.showinfo("成功", "错题数据已成功清除")
            except Exception as e:
                messagebox.showerror("错误", f"清除错题数据失败: {str(e)}")
    
    def start_review(self):
        """开始错题复习"""
        import json
        import os
        
        if os.path.exists(WRONG_FILE):
            try:
                with open(WRONG_FILE, "r", encoding="utf-8") as f:
                    wrongs = json.load(f)
                
                if not wrongs:
                    messagebox.showinfo("提示", "没有错题记录！")
                    return
                
                # 从错题本中随机选择一个单词
                wrong_item = random.choice(wrongs)
                word = list(wrong_item.keys())[0]
                meaning = wrong_item[word]
                self.review_word = {"word": word, "translation": meaning}
                
                # 设置复习模式和问题
                self.review_mode = random.choice(["E2C", "C2E"])
                # 确保统计记录为复习模块
                self.mode = "REVIEW"
                
                # 清空复习卡片
                for widget in self.review_card.winfo_children():
                    widget.destroy()
                
                # 重新设置卡片内部布局权重
                self.review_card.grid_rowconfigure(0, weight=1)
                self.review_card.grid_rowconfigure(1, weight=1)
                self.review_card.grid_rowconfigure(2, weight=1)
                # 确保卡片内列能水平扩展
                self.review_card.grid_columnconfigure(0, weight=1)
                
                if self.review_mode == "E2C":
                    self.review_label = ttk.Label(
                        self.review_card,
                        text=f"英译汉: {word}",
                        font=("微软雅黑", 16),
                        foreground=self.theme["text"]
                    )
                else:
                    self.review_label = ttk.Label(
                        self.review_card,
                        text=f"汉译英: {meaning}",
                        font=("微软雅黑", 16),
                        foreground=self.theme["text"]
                    )
                
                # 标签使用EW粘性以适应水平宽度
                self.review_label.grid(row=0, column=0, pady=20, sticky="NEW")
                
                # 创建输入区域 - 使用grid布局，适配视口宽度
                input_frame = ttk.Frame(self.review_card)
                # 使用EW粘性并减少左右边距以便更好地利用宽度
                input_frame.grid(row=1, column=0, pady=15, padx=20, sticky="EW")
                input_frame.grid_columnconfigure(0, weight=1)
                
                self.review_entry = ttk.Entry(
                    input_frame,
                    style="Custom.TEntry"
                )
                # 输入框完全扩展以适应父容器宽度
                self.review_entry.grid(row=0, column=0, sticky="EW", padx=5, pady=5)
                
                # 操作按钮 - 使用grid布局，适配视口宽度
                action_frame = ttk.Frame(self.review_card)
                action_frame.grid(row=2, column=0, pady=15, padx=20, sticky="EW")
                # 确保两列权重相等，按钮能对称分布
                action_frame.grid_columnconfigure(0, weight=1)
                action_frame.grid_columnconfigure(1, weight=1)
                
                self.review_submit = ttk.Button(
                    action_frame,
                    text="提交答案",
                    style="Primary.TButton",
                    command=self.check_review_answer,
                    width=15
                )
                self.review_submit.grid(row=0, column=0, padx=10, sticky="E")
                
                self.review_next = ttk.Button(
                    action_frame,
                    text="下一题",
                    style="Secondary.TButton",
                    command=self.start_review,
                    state=tk.DISABLED,
                    width=15
                )
                self.review_next.grid(row=0, column=1, padx=10, sticky="W")
                
                # 添加窗口大小变化时的绑定，确保内容始终适配宽度
                def on_configure(event):
                    try:
                        # 刷新布局以确保元素位置正确
                        self.review_card.update_idletasks()
                    except Exception:
                        pass
                
                # 绑定窗口大小变化事件
                try:
                    self.review_card.bind('<Configure>', on_configure)
                except Exception:
                    pass
                
            except Exception as e:
                print(f"复习错题出错: {e}")
                messagebox.showerror("错误", "加载错题记录失败")
        else:
            messagebox.showinfo("提示", "没有错题记录！")
    
    def check_review_answer(self):
        """检查复习答案"""
        user_answer = self.review_entry.get().strip()
        if not user_answer:
            messagebox.showwarning("提示", "请输入答案")
            return

        if self.review_mode == "E2C":
            correct_answer = self.review_word["translation"]
            # 处理correct_answer可能是列表的情况
            if isinstance(correct_answer, list):
                correct_answer_str = " ".join(correct_answer)
            else:
                correct_answer_str = str(correct_answer)
            user_answer_str = user_answer.lower()
            is_correct = user_answer_str in correct_answer_str.lower() or correct_answer_str.lower() in user_answer_str
        else:
            correct_answer = self.review_word["word"]
            # 确保correct_answer是字符串
            correct_answer_str = str(correct_answer)
            is_correct = user_answer.lower() == correct_answer_str.lower()

        if is_correct:
            # 显示成功动画效果
            original_color = self.theme["text"]
            success_color = self.theme["success"]
            
            def blink():
                for _ in range(3):
                    self.review_label.config(foreground=success_color)
                    self.root.update()
                    time.sleep(0.1)
                    self.review_label.config(foreground=original_color)
                    self.root.update()
                    time.sleep(0.1)
            
            threading.Thread(target=blink, daemon=True).start()
            
            # 现代UI反馈：添加成功标签而不是简单的消息框
            success_label = ttk.Label(
                self.review_card,
                text="🎉 恭喜，回答正确！",
                style="Subheading.TLabel",
                foreground=self.theme["success"]
            )
            # 反馈标签使用EW粘性以适应水平宽度
            success_label.grid(row=3, column=0, pady=10, padx=20, sticky="NEW")
            
            # 从错题本中移除已掌握的单词（异常不影响后续UI状态）
            import json
            import os
            try:
                with open(WRONG_FILE, "r", encoding="utf-8") as f:
                    wrongs = json.load(f)
                
                for i, item in enumerate(wrongs):
                    if list(item.keys())[0] == self.review_word["word"]:
                        wrongs.pop(i)
                        break
                
                with open(WRONG_FILE, "w", encoding="utf-8") as f:
                    json.dump(wrongs, f, ensure_ascii=False, indent=2)
            except Exception as e:
                try:
                    print(f"更新错题本失败: {e}")
                except Exception:
                    pass
        else:
            # 现代UI反馈：添加错误标签而不是简单的消息框
            error_label = ttk.Label(
                self.review_card,
                text=f"❌ 回答错误！正确答案是：{correct_answer}",
                style="Subheading.TLabel",
                foreground=self.theme["error"]
            )
            # 反馈标签使用EW粘性以适应水平宽度
            error_label.grid(row=3, column=0, pady=10, padx=20, sticky="NEW")

        # 更新统计信息
        self.update_stats(is_correct)
        
        # 更新按钮状态，符合现代UI设计
        self.review_entry.delete(0, tk.END)
        self.review_submit.config(state=tk.DISABLED, style="Custom.TButton")
        self.review_next.config(state=tk.NORMAL, style="Primary.TButton")
        self.review_next.focus_set()
    
    def _setup_ttk_theme(self):
        """设置ttk主题样式 - 全新现代UI设计"""
        # 如果 ttkbootstrap 可用，优先使用其 Style（提供现代主题）
        if TB_AVAILABLE:
            try:
                style = tb.Style(theme='flatly')
            except Exception:
                style = ttk.Style()
        else:
            style = ttk.Style()

        # 保存到实例，方便其它函数使用（例如 add_hover_effect）
        self.style = style

        # 如果不是使用 ttkbootstrap，选择一个干净的内置主题
        if not TB_AVAILABLE:
            if 'clam' not in style.theme_names():
                style.theme_use('default')
            else:
                style.theme_use('clam')
        
        # 配置默认标签样式
        style.configure(
            "TLabel",
            font=('微软雅黑', 12),
            foreground=self.theme["text"],
            background=self.theme["background"]
        )

        # 配置默认框架背景 -> 确保 ttk.Frame 使用纯白背景，替代系统灰色
        style.configure(
            "TFrame",
            background=self.theme["background"]
        )

        # 导航栏样式
        style.configure(
            "Nav.TFrame",
            background=self.theme["background"],
            relief="flat",
            padding=(8, 6)
        )

        # 导航标题样式
        style.configure(
            "NavTitle.TLabel",
            font=('微软雅黑', 20, 'bold'),
            foreground=self.theme["primary"],
            background=self.theme["background"]
        )
        
        # 配置标题样式
        style.configure(
            "Heading.TLabel",
            font=('微软雅黑', 36, 'bold'),
            foreground=self.theme["primary"],
            background="#FFFFFF",
            padding=(0, 20, 0, 15)
        )
        
        style.configure(
            "Subheading.TLabel",
            font=('微软雅黑', 24, 'bold'),
            foreground=self.theme["text"],
            background=self.theme["background"],
            padding=(0, 10, 0, 10)
        )
        
        # 配置卡片样式 - 添加阴影效果
        style.configure(
            "Card.TFrame",
            background=self.theme["card_bg"],
            relief="flat",
            padding=25
        )
        
        # 配置带阴影的卡片样式 - 使用纯白色背景
        style.configure(
            "CardShadow.TFrame",
            # 使用浅色背景模拟阴影，内部使用白色卡片提升层次
            background=self.theme["hover"],
            relief="flat",
            borderwidth=0,
            padding=10
        )
        
        # 配置统计卡片样式 - 使用纯白色背景
        style.configure(
            "StatCard.TFrame",
            background="#FFFFFF",
            relief="groove",
            borderwidth=1,
            padding=16
        )
        
        # 配置主按钮样式 - 更现代的设计
        style.configure(
            "Primary.TButton",
            font=('微软雅黑', 14, 'bold'),
            padding=15,
            background=self.theme["primary"],
            foreground="white",
            borderwidth=0
        )

        # 基础按钮统一样式
        style.configure(
            "TButton",
            font=('微软雅黑', 12),
            padding=10,
            relief='flat'
        )

        # 模式按钮样式（更大更醒目）
        style.configure(
            "Mode.TButton",
            font=('微软雅黑', 14, 'bold'),
            padding=18,
            background=self.theme["primary"],
            foreground='white'
        )
        style.map(
            "Mode.TButton",
            background=[('active', self.theme['primary_dark'])],
            foreground=[('active', 'white')]
        )
        
        # 添加按钮悬停效果
        style.map(
            "Primary.TButton",
            background=[("active", self.theme["primary_dark"])],
            foreground=[("active", "white")],
            relief=[("pressed", "sunken")]
        )
        
        # 配置次要按钮样式
        style.configure(
            "Secondary.TButton",
            font=('微软雅黑', 14),
            padding=15,
            background=self.theme["secondary"],
            foreground="white",
            borderwidth=0
        )
        
        style.map(
            "Secondary.TButton",
            background=[("active", self.theme["primary_light"])],
            foreground=[("active", "white")],
            relief=[("pressed", "sunken")]
        )
        
        # 配置危险按钮样式（用于重置等操作）
        style.configure(
            "Danger.TButton",
            font=('微软雅黑', 14),
            padding=15,
            background=self.theme["error"],
            foreground="white",
            borderwidth=0
        )
        
        style.map(
            "Danger.TButton",
            background=[("active", "#C1121F")],
            foreground=[("active", "white")],
            relief=[("pressed", "sunken")]
        )
        
        # 配置普通按钮样式
        style.configure(
            "Custom.TButton",
            font=('微软雅黑', 14),
            padding=15,
            background="white",
            foreground=self.theme["text"],
            bordercolor=self.theme["border"],
            relief="solid",
            borderwidth=1
        )
        
        style.map(
            "Custom.TButton",
            background=[("active", self.theme["hover"])],
            foreground=[("active", self.theme["primary"])],
            bordercolor=[("active", self.theme["primary"])]
        )
        
        # 配置输入框样式 - 更现代的设计
        style.configure(
            "Custom.TEntry",
            font=('微软雅黑', 40),
            padding=15,
            fieldbackground="white",
            foreground=self.theme["text"],
            bordercolor=self.theme["border"],
            relief="solid",
            borderwidth=1
        )
        
        style.map(
            "Custom.TEntry",
            bordercolor=[("focus", self.theme["primary"])],
            fieldbackground=[("disabled", self.theme["background"])]  # 使用背景色隐藏禁用状态
        )
        
        # 配置单选按钮样式
        style.configure(
            "TRadiobutton",
            font=('微软雅黑', 14),
            foreground=self.theme["text"],
            background=self.theme["background"]
        )
        
        style.map(
            "TRadiobutton",
            foreground=[("active", self.theme["primary"])],
            indicatorcolor=[("selected", self.theme["primary"])]
        )
        
        # 配置进度条样式 - 移除灰色背景
        style.configure(
            "Accent.Horizontal.TProgressbar",
            troughcolor=self.theme["background"],  # 使用背景色隐藏进度条背景
            background=self.theme["accent"],
            relief="flat",
            thickness=15
        )
        
        # 为页面切换动画创建透明框架样式
        for i in range(0, 11):
            style.configure(
                f"Transparent{i}.TFrame",
                background=self.theme["background"]
            )
    
    def _create_navigation_bar(self):
        """创建顶部导航栏 - 更现代的设计"""
        # 创建导航栏容器，使用更现代的样式
        nav_frame = ttk.Frame(self.root, style="CardShadow.TFrame")
        nav_frame.pack(fill=tk.X, side=tk.TOP, padx=0, pady=0)
        
        # 设置导航栏高度和间距
        nav_frame.grid_columnconfigure(0, weight=0)
        nav_frame.grid_columnconfigure(1, weight=1)
        nav_frame.grid_columnconfigure(2, weight=0)
        
        # 返回按钮 - 改进样式
        self.btn_back = ttk.Button(
            nav_frame,
            text="← 返回",
            style="Custom.TButton",
            command=self.go_back,
            state=tk.DISABLED,
            padding=10
        )
        self.btn_back.grid(row=0, column=0, sticky=tk.W, padx=(20, 15), pady=10)
        
        # 导航标题 - 更大更醒目的字体
        self.nav_title = ttk.Label(
            nav_frame,
            text="英语听写助手",
            font=('微软雅黑', 20, 'bold'),
            foreground=self.theme["primary"]
        )
        self.nav_title.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        # 右侧导航按钮容器
        right_buttons = ttk.Frame(nav_frame)
        right_buttons.grid(row=0, column=2, sticky=tk.E, padx=20, pady=10)
        
        # 返回首页按钮 - 新增
        self.btn_home = ttk.Button(
            right_buttons,
            text="🏠 首页",
            style="Primary.TButton",
            command=lambda: self.show_page("welcome"),
            padding=10
        )
        self.btn_home.pack(side=tk.RIGHT, padx=10)
        
        # 学习统计按钮
        self.btn_nav_stats = ttk.Button(
            right_buttons,
            text="📊 学习统计",
            style="Secondary.TButton",
            command=lambda: self.show_page("stats"),
            padding=10
        )
        self.btn_nav_stats.pack(side=tk.RIGHT, padx=10)
        
        # 复习错题按钮
        self.btn_nav_review = ttk.Button(
            right_buttons,
            text="📝 复习错题",
            style="Primary.TButton",
            command=lambda: self.show_page("review"),
            padding=10
        )
        self.btn_nav_review.pack(side=tk.RIGHT, padx=10)
        
        # 查看所有错题按钮
        self.btn_nav_view_wrongs = ttk.Button(
            right_buttons,
            text="❌ 错题列表",
            style="Secondary.TButton",
            command=lambda: self.show_page("view_wrongs"),
            padding=10
        )
        self.btn_nav_view_wrongs.pack(side=tk.RIGHT, padx=10)
        
        # 待办事项按钮
        self.btn_nav_todo = ttk.Button(
            right_buttons,
            text="📝 每日目标",
            style="Primary.TButton",
            command=lambda: self.show_page("todo"),
            padding=10
        )
        self.btn_nav_todo.pack(side=tk.RIGHT, padx=10)
        
        # 添加按钮悬停效果
        self.add_hover_effect(self.btn_back)
        self.add_hover_effect(self.btn_home)  # 添加首页按钮的悬停效果
        self.add_hover_effect(self.btn_nav_stats)
        self.add_hover_effect(self.btn_nav_review)
        self.add_hover_effect(self.btn_nav_view_wrongs)
        self.add_hover_effect(self.btn_nav_todo)  # 添加待办事项按钮的悬停效果
    
    def _create_pages(self):
        """创建所有页面框架"""
        self.pages = {}
        
        # 创建欢迎页（放到滚动容器 inner）
        self.pages["welcome"] = ttk.Frame(self.container.inner)
        self._create_welcome_page()

        # 创建学习页面
        self.pages["learn"] = ttk.Frame(self.container.inner)
        self._create_learn_page()

        # 创建复习页面
        self.pages["review"] = ttk.Frame(self.container.inner)
        
        # 创建查看所有错题页面
        self.pages["view_wrongs"] = ttk.Frame(self.container.inner)
        self._create_view_wrongs_page()
        self._create_review_page()

        # 创建统计页面
        self.pages["stats"] = ttk.Frame(self.container.inner)
        self._create_stats_page()  # 确保调用创建统计页面的方法
        
        # 创建待办事项页面
        self.pages["todo"] = ttk.Frame(self.container.inner)
        self._create_todo_list_page()  # 创建待办事项页面
        
        # 创建历史记录页面
        self.pages["history"] = ttk.Frame(self.container.inner)
        self._create_history_page()  # 创建历史记录页面
    
    def _create_welcome_page(self):
        """创建欢迎页面 - 全新现代设计"""
        page = self.pages["welcome"]

        # 主容器，居中布局（使用 place 居中，固定宽度以避免内容被拉伸）
        main_container = ttk.Frame(page, style="TFrame")
        # 主容器占满视口宽度，元素随窗口宽度伸缩
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 顶部标题区域 - 更醒目的设计
        # 创建标题容器（居中）
        title_section = ttk.Frame(main_container, style="TFrame")
        title_section.pack(pady=30, fill=tk.X)

        # 标题
        title_label = ttk.Label(
            title_section,
            text="英语听写助手",
            style="Heading.TLabel"
        )
        title_label.pack(pady=10)

        # 副标题 - 更大的字体和更好的视觉效果
        subtitle_label = ttk.Label(
            title_section,
            text="提升英语能力，从今天开始",
            font=('微软雅黑', 18),
            foreground=self.theme["text_light"]
        )
        subtitle_label.pack(pady=(15, 30))

        # 内容卡片容器
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.pack(expand=True, fill=tk.BOTH)

        # 难度选择卡片 - 使用带阴影的卡片样式，增加内边距与圆角视觉（白底）
        difficulty_card = ttk.Frame(content_frame, style="CardShadow.TFrame")
        difficulty_card.pack(fill=tk.X, pady=(0, 25), padx=10)

        # 难度选择标题
        diff_title = ttk.Label(
            difficulty_card,
            text="选择难度级别",
            font=('微软雅黑', 18, 'bold'),
            foreground=self.theme["text"]
        )
        diff_title.pack(anchor=tk.W, pady=(0, 20))

        # 难度选择单选按钮 - 更美观的布局
        difficulty_frame = ttk.Frame(difficulty_card, style="TFrame")
        difficulty_frame.pack(fill=tk.X, padx=10)

        self.difficulty_var = tk.StringVar(value="normal")
        difficulties = [("简单", "easy", "适合初学者"), ("普通", "normal", "标准难度"), ("困难", "hard", "挑战自我")]

        # 创建难度选项卡片
        for i, (text, value, hint) in enumerate(difficulties):
            # 创建包含标签和单选按钮的容器 - 使用卡片样式
            option_frame = ttk.Frame(difficulty_frame, style="StatCard.TFrame")
            option_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=8, pady=5)

            # 根据难度设置不同的颜色
            if value == "easy":
                color = self.theme["success"]
            elif value == "normal":
                color = self.theme["primary"]
            else:
                color = self.theme["warning"]

            # 创建带颜色的单选按钮和标签
            rb_frame = ttk.Frame(option_frame, style="TFrame")
            rb_frame.pack(fill=tk.X, pady=10)

            rb = ttk.Radiobutton(
                rb_frame,
                text=text,
                variable=self.difficulty_var,
                value=value,
                style="TRadiobutton",
                width=6
            )
            rb.pack(side=tk.LEFT, padx=10)

            # 添加样式提示标签 - 更大更醒目
            hint_label = ttk.Label(
                rb_frame,
                text=hint,
                font=('微软雅黑', 12, 'italic'),
                foreground=color
            )
            hint_label.pack(side=tk.LEFT, padx=5)

        # 模式选择卡片 - 使用带阴影的卡片样式
        modes_card = ttk.Frame(content_frame, style="CardShadow.TFrame")
        modes_card.pack(expand=True, fill=tk.BOTH, pady=(10, 0))

        # 模式选择标题
        modes_title = ttk.Label(
            modes_card,
            text="选择学习模式",
            font=('微软雅黑', 18, 'bold'),
            foreground=self.theme["text"]
        )
        modes_title.pack(anchor=tk.W, pady=(0, 25))

        # 模式按钮网格布局 - 使用更现代的卡片式布局
        modes_container = ttk.Frame(modes_card, style="TFrame")
        modes_container.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # 模式按钮配置
        mode_configs = [
            {"text": "📝 英译汉", "mode": "E2C", "description": "根据英文写出中文意思", "color": self.theme["primary"]},
            {"text": "📖 汉译英", "mode": "C2E", "description": "根据中文写出英文单词", "color": self.theme["primary_light"]},
            {"text": "🔊 听写拼写", "mode": "LISTEN", "description": "听发音写出正确拼写", "color": self.theme["secondary"]}
        ]

        # 创建模式按钮卡片 - 使用更好的视觉效果
        for i, config in enumerate(mode_configs):
            # 创建按钮卡片 - 使用统计卡片样式
            button_card = ttk.Frame(modes_container, style="StatCard.TFrame")
            button_card.pack(fill=tk.X, pady=15, padx=5)

            # 创建主按钮 - 更醒目的设计
            btn = ttk.Button(
                button_card,
                text=config["text"],
                style="Mode.TButton",
                padding=20,
                command=lambda m=config["mode"]: [self.set_mode(m), self.show_page("learn")]
            )
            btn.pack(fill=tk.X)

            # 添加描述标签 - 改进样式
            desc_label = ttk.Label(
                button_card,
                text=config["description"],
                font=('微软雅黑', 14),
                foreground=self.theme["text_light"],
                anchor=tk.CENTER
            )
            desc_label.pack(pady=(12, 5))

            # 添加按钮悬停效果
            self.add_hover_effect(btn)
    
    def _create_learn_page(self):
        """创建学习页面 - 全新现代设计"""
        page = self.pages["learn"]

        # 主容器占满页面宽度，内部使用 grid 管理具体布局
        main_container = ttk.Frame(page, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 使用网格布局管理器（在 main_container 内）
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=0)
        main_container.grid_rowconfigure(1, weight=3)
        main_container.grid_rowconfigure(2, weight=1)
        main_container.grid_rowconfigure(3, weight=0)

        # 进度和统计信息区域 - 使用带阴影的卡片
        stats_bar = ttk.Frame(main_container, style="CardShadow.TFrame")
        stats_bar.grid(row=0, column=0, sticky=tk.EW, padx=20, pady=(10, 15))
        stats_bar.grid_columnconfigure(0, weight=1)
        stats_bar.grid_columnconfigure(1, weight=0)
        
        # 左侧：简单统计显示 - 更大的字体
        self.current_stats_label = ttk.Label(
            stats_bar,
            text="准备开始学习...",
            font=('微软雅黑', 14),
            foreground=self.theme["text"]
        )
        self.current_stats_label.grid(row=0, column=0, sticky='w', pady=8, padx=10)
        
        # 右侧：模块使用率统计
        self.module_usage_label = ttk.Label(
            stats_bar,
            text="使用率: 0%",
            font=('微软雅黑', 14, 'bold'),
            foreground=self.theme["accent"]
        )
        self.module_usage_label.grid(row=0, column=1, sticky='e', pady=8, padx=10)
        
        # 自动下一题设置控件（记住偏好）
        # 从 stats 中读取已有设置，默认自动下一题开启，延迟1200ms
        auto_next_default = True
        auto_delay_default = 1200
        try:
            auto_next_default = bool(self.stats.get('auto_next', True))
            auto_delay_default = int(self.stats.get('auto_next_delay', 1200))
        except Exception:
            auto_next_default = True
            auto_delay_default = 1200

        settings_frame = ttk.Frame(stats_bar)
        settings_frame.grid(row=1, column=0, columnspan=2, pady=4, sticky='ew')

        self.auto_next_var = tk.BooleanVar(value=auto_next_default)
        auto_cb = ttk.Checkbutton(settings_frame, text='自动下一题', variable=self.auto_next_var, style='TRadiobutton')
        auto_cb.pack(side=tk.LEFT, padx=(0,8))

        ttk.Label(settings_frame, text='延迟(ms):', font=('微软雅黑', 10)).pack(side=tk.LEFT)
        self.auto_delay_var = tk.StringVar(value=str(auto_delay_default))
        self.auto_delay_entry = ttk.Entry(settings_frame, width=6, textvariable=self.auto_delay_var, style='Custom.TEntry')
        self.auto_delay_entry.pack(side=tk.LEFT, padx=(6,0))

        # 保存设置按钮（小型）
        def _save_auto_settings():
            try:
                self.stats['auto_next'] = bool(self.auto_next_var.get())
                try:
                    val = int(self.auto_delay_var.get())
                    if val < 200:
                        val = 200
                except Exception:
                    val = 1200
                self.stats['auto_next_delay'] = int(val)
                save_stats(self.stats)
                # 轻微提示
                self.current_stats_label.config(text=f"准备开始学习... (自动下一题={'开' if self.stats['auto_next'] else '关'})")
            except Exception:
                pass

        save_btn = ttk.Button(settings_frame, text='保存', command=_save_auto_settings, style='Custom.TButton')
        save_btn.pack(side=tk.LEFT, padx=(8,0))
        
        # 问题卡片 - 使用带阴影的卡片样式
        question_card = ttk.Frame(main_container, style="CardShadow.TFrame")
        question_card.grid(row=1, column=0, sticky=tk.NSEW, padx=20, pady=10)
        
        # 问题卡片内部布局
        question_card.grid_columnconfigure(0, weight=1)
        question_card.grid_rowconfigure(0, weight=1)
        question_card.grid_rowconfigure(1, weight=0)
        
        # 问题显示标签 - 更醒目的设计
        self.question_label = ttk.Label(
            question_card,
            text="加载中...",
            font=("微软雅黑", 28, 'bold'),
            wraplength=800,
            foreground=self.theme["text"],
            anchor=tk.CENTER,
            justify=tk.CENTER
        )
        self.question_label.grid(row=0, column=0, sticky=tk.NSEW, pady=40)
        
        # 播放按钮容器 - 听写模式使用
        self.play_button_container = ttk.Frame(question_card)
        self.play_button_container.grid(row=1, column=0, pady=30)
        
        # 播放按钮 - 更大更突出的设计
        self.play_button = ttk.Button(
            self.play_button_container,
            text="🔊 播放单词",
            style="Secondary.TButton",
            command=self.play_word_audio,
            padding=20
        )
        
        # 输入区域 - 更美观的设计
        self.input_section = ttk.Frame(main_container)
        self.input_section.grid(row=2, column=0, sticky=tk.EW, padx=40, pady=20)

        # 输入框标签 - 更大的字体
        input_label = ttk.Label(
            self.input_section,
            text="请输入您的答案：",
            font=('微软雅黑', 16, 'bold'),
            foreground=self.theme["text"]
        )
        input_label.pack(anchor=tk.W, pady=(0, 15))

        # 输入框容器 - 使用卡片样式
        self.input_frame = ttk.Frame(self.input_section, style="Card.TFrame")
        self.input_frame.pack(fill=tk.X, pady=5)

        # 主要输入框 - 更大的字体和内边距
        self.entry = ttk.Entry(
            self.input_frame,
            style="Custom.TEntry"
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, pady=10)

        # 语音输入按钮 - 更大更醒目
        self.btn_voice = ttk.Button(
            self.input_frame,
            text="🎤 语音输入",
            style="Secondary.TButton",
            command=self.voice_answer,
            padding=15
        )
        self.btn_voice.pack(side=tk.LEFT, padx=15, pady=10)
        
        # 按钮区域 - 改进布局
        self.buttons_section = ttk.Frame(main_container)
        self.buttons_section.grid(row=3, column=0, sticky=tk.EW, padx=20, pady=20)

        # 创建更现代的按钮布局 - 增大间距和尺寸
        self.btn_frame = ttk.Frame(self.buttons_section)
        self.btn_frame.pack(fill=tk.X)

        # 左侧按钮（提示）
        self.btn_hint = ttk.Button(
            self.btn_frame,
            text="💡 提示",
            style="Custom.TButton",
            command=self.show_hint,
            padding=15,
            width=15
        )
        self.btn_hint.pack(side=tk.LEFT, padx=20)

        # 中间按钮（提交）
        self.btn_submit = ttk.Button(
            self.btn_frame,
            text="✅ 提交答案",
            style="Primary.TButton",
            command=self.check_answer,
            padding=15,
            width=20
        )
        self.btn_submit.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=20)

        # 右侧按钮（下一题）
        self.btn_next = ttk.Button(
            self.btn_frame,
            text="➡ 下一题",
            style="Primary.TButton",
            command=self.next_question,
            padding=15,
            width=15
        )
        self.btn_next.pack(side=tk.RIGHT, padx=20)

        # 添加按钮悬停效果
        self.add_hover_effect(self.btn_hint)
        self.add_hover_effect(self.btn_submit)
        self.add_hover_effect(self.btn_next)
        self.add_hover_effect(self.btn_voice)
    
    def _create_review_page(self):
        """创建复习页面 - 全新现代设计"""
        page = self.pages["review"]

        # 主容器占满页面宽度，内部使用 grid 管理具体布局
        main_container = ttk.Frame(page, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 设置主容器的列权重，使内容能水平扩展
        main_container.grid_columnconfigure(0, weight=1)

        # 创建复习卡片 - 使用带阴影的卡片样式（放在 main_container）
        self.review_card = ttk.Frame(main_container, style="CardShadow.TFrame")
        # 使用sticky="EW"确保卡片宽度随窗口变化而适配
        self.review_card.grid(row=0, column=0, pady=30, padx=30, sticky="NSEW")
        
        # 设置卡片内部布局
        self.review_card.grid_rowconfigure(0, weight=1)
        self.review_card.grid_rowconfigure(1, weight=1)
        self.review_card.grid_rowconfigure(2, weight=1)
        # 确保卡片内列能水平扩展
        self.review_card.grid_columnconfigure(0, weight=1)
        
        # 创建复习问题标签 - 更醒目的设计
        self.review_label = ttk.Label(
            self.review_card, 
            text="📝 错题复习",
            style="Heading.TLabel"
        )
        self.review_label.grid(row=0, column=0, pady=(50, 30), sticky="N")
        
        # 创建复习说明 - 更友好的排版
        review_desc = ttk.Label(
            self.review_card,
            text="通过复习错题来巩固你的知识。\n点击下方按钮开始复习最近做错的题目。",
            font=("微软雅黑", 18),
            foreground=self.theme["text_light"],
            justify=tk.CENTER
        )
        review_desc.grid(row=1, column=0, pady=20, sticky="N")
        
        # 创建开始复习按钮 - 更大更醒目的设计
        start_button = ttk.Button(
            self.review_card,
            text="🚀 开始复习",
            command=self.start_review,
            style="Primary.TButton",
            padding=25,
            width=20
        )
        start_button.grid(row=2, column=0, pady=60, sticky="S")
        
        # 保存按钮引用
        self.start_button = start_button
        
        # 添加按钮悬停效果
        self.add_hover_effect(self.start_button)
    
    def add_hover_effect(self, button, hover_color=None):
        """为按钮添加悬停效果"""
        try:
            # 获取当前按钮的样式
            original_style = button.cget("style")
            
            # 创建一个临时的悬停样式名
            hover_style_name = f"{original_style}.Hover"
            
            # 尝试配置悬停样式
            try:
                # 为不同类型的按钮设置不同的悬停颜色
                if original_style == "Primary.TButton":
                    self.style.configure(hover_style_name, background=self.theme["primary_light"])
                elif original_style == "Secondary.TButton":
                    self.style.configure(hover_style_name, background=self.theme["secondary_light"])
                else:
                    # 对于其他按钮，使用默认的悬停颜色
                    if hover_color:
                        self.style.configure(hover_style_name, background=hover_color)
                    else:
                        self.style.configure(hover_style_name, background=self.theme["primary_light"])
            except:
                # 如果无法配置样式，静默失败
                pass
            
            # 绑定鼠标进入和离开事件
            def on_enter(event):
                try:
                    button.config(style=hover_style_name)
                except:
                    # 如果设置样式失败，静默失败
                    pass
            
            def on_leave(event):
                try:
                    button.config(style=original_style)
                except:
                    # 如果设置样式失败，静默失败
                    pass
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        except Exception as e:
            # 如果出现任何错误，我们就跳过悬停效果，而不是让程序崩溃
            print(f"无法为按钮添加悬停效果: {e}")
    
    def get_stats_text(self):
        """获取统计信息文本"""
        accuracy = 0
        if self.stats["total_questions"] > 0:
            accuracy = round(self.stats["correct_answers"] / self.stats["total_questions"] * 100, 1)
        
        return f"总题数: {self.stats['total_questions']} | 正确率: {accuracy}% | 连续正确: {self.stats['streak']} | 最佳连续: {self.stats['best_streak']}"
    
    def reset_stats(self):
        """重置统计信息、单词统计、历史学习记录和清除错题数据"""
        if not messagebox.askyesno("确认", "确定要重置所有统计数据、单词统计、历史学习记录和清除错题数据吗？此操作不可恢复。"):
            return

        # 优先使用 StatsManager 统一重置，保持状态隔离
        try:
            if getattr(self, 'stats_manager', None):
                self.stats_manager.reset_all()
                self.stats = self.stats_manager.snapshot()
            else:
                # 旧路径：直接调用 data_manager
                written, failed = reset_all_data()
                logger.log(f"reset_all_data wrote: {written}, failed: {failed}")
                # 在内存中重置 self.stats 并保存一份
                self.stats = {
                    "total_questions": 0,
                    "correct_answers": 0,
                    "wrong_answers": 0,
                    "streak": 0,
                    "best_streak": 0
                }
                try:
                    save_stats(self.stats)
                except Exception:
                    pass
        except Exception as e:
            logger.log(f"调用重置失败: {e}")

        # 同步清空模块统计的内存状态并保存到文件，确保统计页完全归零
        try:
            if hasattr(logger, 'module_stats'):
                logger.module_stats = {
                    "E2C": {"total": 0, "correct": 0, "wrong": 0},
                    "C2E": {"total": 0, "correct": 0, "wrong": 0},
                    "LISTEN": {"total": 0, "correct": 0, "wrong": 0},
                    "review": {"total": 0, "correct": 0, "wrong": 0}
                }
                if hasattr(logger, 'save_module_stats'):
                    logger.save_module_stats()
                if hasattr(logger, 'session_log'):
                    try:
                        logger.session_log["module_percentage"] = {}
                        logger.session_log["accuracy_by_module"] = {}
                    except Exception:
                        pass
        except Exception:
            pass

        # 刷新 UI（错题、历史、今日进度、模块统计等）
        try:
            if hasattr(self, 'wrong_words_tree'):
                try:
                    self.load_wrong_words_table()
                except Exception:
                    # 清空 treeview
                    try:
                        for i in self.wrong_words_tree.get_children():
                            self.wrong_words_tree.delete(i)
                    except Exception:
                        pass
        except Exception:
            pass

        try:
            if hasattr(self, 'pages') and 'history' in self.pages:
                for widget in self.pages['history'].winfo_children():
                    try:
                        widget.destroy()
                    except Exception:
                        pass
                try:
                    self._create_history_page()
                except Exception:
                    pass
        except Exception:
            pass

        # 更新统计显示与今日进度
        try:
            if hasattr(self, 'stats_label'):
                self.stats_label.config(text=self.get_stats_text())
            if hasattr(self, 'current_stats_label'):
                self.current_stats_label.config(text=f"总题数: 0 | 正确率: 0.0% | 连续正确: 0")
            if hasattr(self, 'module_usage_label'):
                self.module_usage_label.config(text="当前模块使用率: 0%")

            from data_manager import get_today_goal
            today_goal = get_today_goal()
            if hasattr(self, 'todo_progress_var'):
                try:
                    self.todo_progress_var.set(today_goal.get('percentage', 0))
                except Exception:
                    pass
            if hasattr(self, 'todo_current_label'):
                try:
                    self.todo_current_label.config(text=str(today_goal.get('current', 0)))
                except Exception:
                    pass
            if hasattr(self, 'todo_target_label'):
                try:
                    self.todo_target_label.config(text=str(today_goal.get('target', 20)))
                except Exception:
                    pass
        except Exception:
            pass

        # 刷新统计页的今日进度卡片
        try:
            if hasattr(self, 'daily_progress_var'):
                try:
                    self.daily_progress_var.set(0)
                except Exception:
                    pass
            if hasattr(self, 'daily_goal_label'):
                try:
                    target = 20
                    try:
                        from data_manager import get_today_goal
                        tg = get_today_goal().get('target', None)
                        if tg:
                            target = tg
                    except Exception:
                        pass
                    self.daily_goal_label.config(text=f"0/{target} 个单词")
                except Exception:
                    pass
        except Exception:
            pass

        # 在统计页上刷新模块列表等其它数据
        try:
            self._update_stats_data()
        except Exception:
            pass

        # 刷新历史记录页面数据
        try:
            if hasattr(self, 'pages') and 'history' in self.pages:
                self._create_history_page()
        except Exception:
            pass

        # 操作完成提示
        messagebox.showinfo("成功", "统计数据、单词统计、历史学习记录和错题记录已全部重置，应用将重启以应用更改。")
        try:
            # 尝试优雅关闭会话和日志
            try:
                if self.session_index is not None:
                    log_end_session(self.session_index)
            except Exception:
                pass
            try:
                logger.close()
            except Exception:
                pass
            # 先销毁窗口，避免重启时残留界面
            try:
                self.root.destroy()
            except Exception:
                pass
            # 尝试重启应用（替换当前进程）
            import sys, os
            try:
                os.execl(sys.executable, sys.executable, "-m", "dictation_assistant")
            except Exception:
                # 回退：新开进程，退出当前进程
                try:
                    import subprocess
                    subprocess.Popen([sys.executable, "-m", "dictation_assistant"])
                except Exception:
                    pass
                # 退出当前应用
                try:
                    self.root.quit()
                except Exception:
                    pass
                try:
                    sys.exit(0)
                except Exception:
                    pass
        except Exception:
            # 即使重启失败也不让应用崩溃
            pass
        
    def update_stats(self, is_correct):
        """更新学习统计并同步刷新所有相关UI"""
        # 优先通过 StatsManager 更新并持久化，保持状态隔离
        if getattr(self, 'stats_manager', None):
            try:
                self.stats_manager.update_on_answer(is_correct, current_module=self.mode)
                self.stats = self.stats_manager.snapshot()
                accuracy = self.stats_manager.accuracy()
            except Exception:
                # 兜底计算准确率
                accuracy = 0
                try:
                    tq = self.stats.get("total_questions", 0)
                    if tq > 0:
                        accuracy = round(self.stats.get("correct_answers", 0) / tq * 100, 1)
                except Exception:
                    pass
        else:
            # 旧路径：直接更新 self.stats 并持久化
            self.stats["total_questions"] += 1
            if is_correct:
                self.stats["correct_answers"] += 1
                self.stats["streak"] += 1
                self.stats["best_streak"] = max(self.stats["best_streak"], self.stats["streak"])
            else:
                self.stats["wrong_answers"] += 1
                self.stats["streak"] = 0
            try:
                save_stats(self.stats)
            except Exception:
                pass
            # 记录答题日志
            module_arg = self.mode
            if isinstance(module_arg, str) and module_arg.upper() == 'REVIEW':
                module_arg = 'review'
            try:
                logger.log_answer(module_arg, is_correct, getattr(self, 'word', None))
            except Exception:
                pass
            # 更新每日学习进度
            try:
                update_today_progress(is_correct)
            except Exception:
                pass
            # 计算准确率
            accuracy = 0
            if self.stats["total_questions"] > 0:
                accuracy = round(self.stats["correct_answers"] / self.stats["total_questions"] * 100, 1)
        
        # 更新主统计标签
        if hasattr(self, 'stats_label'):
            try:
                self.stats_label.config(text=self.get_stats_text())
            except Exception:
                pass
        
        # 更新学习页当前统计（右上角）
        if hasattr(self, 'current_stats_label'):
            self.current_stats_label.config(
                text=f"总题数: {self.stats['total_questions']} | 正确率: {accuracy}% | 连续正确: {self.stats['streak']}"
            )
        
        # 更新统计页面的卡片数值（若页面已创建）
        try:
            if hasattr(self, 'total_questions_label'):
                self.total_questions_label.config(text=str(self.stats.get('total_questions', 0)))
            if hasattr(self, 'correct_label'):
                self.correct_label.config(text=str(self.stats.get('correct_answers', 0)))
            if hasattr(self, 'wrong_label'):
                self.wrong_label.config(text=str(self.stats.get('wrong_answers', 0)))
            if hasattr(self, 'accuracy_progress_var'):
                try:
                    self.accuracy_progress_var.set(accuracy)
                except Exception:
                    pass
            if hasattr(self, 'accuracy_percent_label'):
                self.accuracy_percent_label.config(text=f"{accuracy}%")
        except Exception:
            pass
        
        # 更新模块使用率统计（基于 logger.module_stats）
        if hasattr(self, 'module_usage_label'):
            try:
                current_module = self.mode if self.mode != "REVIEW" else "review"
                total_all = 0
                current_percentage = 0
                if logger and hasattr(logger, 'module_stats'):
                    total_all = sum(module.get("total", 0) for module in logger.module_stats.values())
                    if total_all > 0:
                        current_module_total = logger.module_stats.get(current_module, {}).get("total", 0)
                        current_percentage = round((current_module_total / total_all) * 100, 1)
                self.module_usage_label.config(text=f"当前模块使用率: {current_percentage}%")
            except Exception:
                pass
        
        # 更新待办事项页面进度（今日目标）
        try:
            today_goal = get_today_goal()
            if hasattr(self, 'todo_progress_var'):
                try:
                    self.todo_progress_var.set(today_goal.get('percentage', 0))
                except Exception:
                    pass
            if hasattr(self, 'todo_current_label'):
                self.todo_current_label.config(text=str(today_goal.get('current', 0)))
            if hasattr(self, 'todo_target_label'):
                self.todo_target_label.config(text=str(today_goal.get('target', 20)))
        except Exception:
            pass
        
        # 更新统计页面的每日进度条与目标文本
        try:
            if hasattr(self, 'daily_progress_var') or hasattr(self, 'daily_goal_label'):
                tg = get_today_goal()
                current = tg.get('current', 0)
                target = tg.get('target', 20)
                percentage = min(100, (current / target) * 100) if target > 0 else 0
                if hasattr(self, 'daily_progress_var'):
                    try:
                        self.daily_progress_var.set(percentage)
                    except Exception:
                        pass
                if hasattr(self, 'daily_goal_label'):
                    self.daily_goal_label.config(text=f"{current}/{target} 个单词")
        except Exception:
            pass
        
        # 刷新统计页的模块列表等其它数据
        try:
            self._update_stats_data()
        except Exception:
            pass
    
    def exit_app(self):
        """安全退出应用"""
        if messagebox.askyesno("确认退出", "确定要退出英语听写助手吗？"):
            # 确保最终保存一次每日学习统计数据
            try:
                # 重新加载并保存一次，确保数据完整性（使用已导入的函数）
                goals = load_daily_goals()
                save_daily_goals(goals)
            except Exception as e:
                print(f"保存每日统计数据时出错: {e}")
                
            if self.session_index is not None:
                log_end_session(self.session_index)
            # 保存并关闭日志
            logger.close()
            self.root.quit()

    def english_to_chinese(self):
        self.mode = "E2C"
        logger.log("切换到英译汉模式")
        self.hint_used = False
        self.word = self.get_word_by_difficulty()
        self.meaning = word_dict[self.word]
        self.question_label.config(text=f"英文：{self.word}", foreground=self.theme["text"])
        self.btn_hint.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)
        self.entry.focus_set()
        
    def chinese_to_english(self):
        self.mode = "C2E"
        logger.log("切换到汉译英模式")
        self.hint_used = False
        self.word, self.meaning = self.get_word_pair_by_difficulty()
        self.question_label.config(text=f"中文：{self.meaning}", foreground=self.theme["text"])
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
        
        # 使用权重采样并避免最近重复
        weights = load_word_weights()
        recent = getattr(self, 'recent_words', [])[-6:]
        candidates = [w for w in words if w not in recent]
        if not candidates:
            candidates = words

        if weights:
            # 兼容结构化权重和旧数值权重
            def _wgt(x):
                v = weights.get(x)
                if isinstance(v, dict):
                    return int(v.get('weight', 1))
                try:
                    return int(v)
                except Exception:
                    return 1

            total_weight = sum(_wgt(w) for w in candidates)
            if total_weight > 0:
                r = random.uniform(0, total_weight)
                cumulative = 0
                for w in candidates:
                    cumulative += _wgt(w)
                    if r <= cumulative:
                        self.recent_words = getattr(self, 'recent_words', []) + [w]
                        return w

        choice = random.choice(candidates)
        self.recent_words = getattr(self, 'recent_words', []) + [choice]
        return choice
    
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
        
        # 使用权重采样并避免最近重复
        weights = load_word_weights()
        recent = getattr(self, 'recent_words', [])[-6:]
        candidates = [(w, m) for w, m in word_pairs if w not in recent]
        if not candidates:
            candidates = word_pairs

        if weights:
            def _wgt(x):
                v = weights.get(x)
                if isinstance(v, dict):
                    return int(v.get('weight', 1))
                try:
                    return int(v)
                except Exception:
                    return 1

            total_weight = sum(_wgt(w) for w, _ in candidates)
            if total_weight > 0:
                r = random.uniform(0, total_weight)
                cumulative = 0
                for w, m in candidates:
                    cumulative += _wgt(w)
                    if r <= cumulative:
                        self.recent_words = getattr(self, 'recent_words', []) + [w]
                        return w, m

        pair = random.choice(candidates)
        self.recent_words = getattr(self, 'recent_words', []) + [pair[0]]
        return pair
    
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
            
            # 使用新的question_label
            self.question_label.config(foreground=self.theme["warning"])
            messagebox.showinfo("提示", hint)

    def listen_and_spell(self):
        try:
            self.mode = "LISTEN"
            logger.log("切换到听写模式")
            self.hint_used = False
            self.word = self.get_word_by_difficulty()
            self.meaning = word_dict[self.word]
            
            # 更新问题标签样式，使其更突出
            self.question_label.config(
                text="🔊 请听单词并输入拼写：", 
                foreground=self.theme["primary"],
                font=("微软雅黑", 24, "bold")
            )
            self.btn_hint.config(state=tk.NORMAL)
            self.btn_next.config(state=tk.DISABLED)
            self.btn_submit.config(state=tk.NORMAL)
            
            # 确保播放按钮正确显示在问题卡片中
            if hasattr(self, 'play_button'):
                # 改进播放按钮样式和位置
                self.play_button.config(
                    text="🔊 播放单词音频",
                    style="Secondary.TButton",
                    padding=15
                )
                # 确保在question_label之后显示
                self.play_button.pack(pady=20)
                
                # 同时自动播放一次
                self.play_word_audio()
            
            # 改进输入框样式，使其在听写模式下更突出
            self.entry.focus_set()
        except Exception as e:
            print(f"听写模式初始化出错: {e}")
            messagebox.showerror("错误", f"听写模式初始化失败: {str(e)}")
    
    def play_word_audio(self):
        """播放单词音频"""
        # 禁用按钮防止重复点击
        self.play_button.config(state=tk.DISABLED, text="🔊 播放中...")
        self.root.update()
        
        # 添加视觉反馈 - 临时改变问题标签颜色
        original_color = self.question_label.cget("foreground")
        self.question_label.config(foreground=self.theme["secondary"])
        self.root.update()
        
        # 播放语音
        success = speak(self.word)
        
        # 恢复原始颜色
        self.question_label.config(foreground=original_color)
        
        # 恢复按钮状态
        self.play_button.config(state=tk.NORMAL, text="🔊 播放单词音频")
        return success
    
    def next_question(self):
        """下一题"""
        # 取消任何未完成的自动跳题定时器，防止重复或被覆盖
        try:
            if getattr(self, '_auto_next_id', None):
                try:
                    self.root.after_cancel(self._auto_next_id)
                except Exception:
                    pass
                self._auto_next_id = None
        except Exception:
            pass

        # 隐藏上一次可能存在的结果面板，恢复输入区
        try:
            self._hide_result_panel()
        except Exception:
            pass
        # 清空输入框
        self.entry.delete(0, tk.END)
        
        # 根据模式切换
        if self.mode == "E2C":
            self.english_to_chinese()
        elif self.mode == "C2E":
            self.chinese_to_english()
        elif self.mode == "LISTEN":
            # 听写模式不需要先隐藏播放按钮，因为listen_and_spell会处理
            self.listen_and_spell()
        else:
            # 其他模式隐藏播放按钮
            if hasattr(self, 'play_button'):
                self.play_button.pack_forget()
        
        self.btn_submit.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.DISABLED)

    def _show_result_panel(self, meanings):
        """隐藏输入并在题卡下方显示释义/结果面板。"""
        try:
            # 隐藏输入区
            try:
                if hasattr(self, 'input_section'):
                    self.input_section.grid_remove()
                if hasattr(self, 'buttons_section'):
                    self.buttons_section.grid_remove()
            except Exception:
                pass

            # 优先把结果面板放到 main_container（也就是 input_section 的父容器），
            # 这样 panel 会占据输入区原来的位置，布局更稳定；如果不可用再回退到 question_card
            parent = None
            if hasattr(self, 'input_section'):
                try:
                    parent = self.input_section.master
                except Exception:
                    parent = None
            if parent is None and hasattr(self, 'question_label'):
                try:
                    parent = self.question_label.master
                except Exception:
                    parent = None
            if parent is None:
                parent = self.root

            # 创建 panel
            try:
                self.result_panel = ttk.Frame(parent, style='InnerCard.TFrame')
                self.result_panel.grid(row=2, column=0, sticky='ew', padx=20, pady=(8, 12))
            except Exception:
                self.result_panel = ttk.Frame(parent, style='InnerCard.TFrame')
                self.result_panel.pack(fill=tk.X, pady=10)

            # 标题样式
            ttk.Label(self.result_panel, text='解释', font=('微软雅黑', 14, 'bold'), foreground=self.theme['primary']).pack(anchor='w', padx=8, pady=(6,4))

            for m in meanings:
                item = ttk.Label(self.result_panel, text=str(m), wraplength=800, font=('微软雅黑', 12), foreground=self.theme['text'])
                item.pack(anchor='w', padx=8, pady=3)

            # 添加下一题按钮
            btns = ttk.Frame(self.result_panel)
            btns.pack(fill=tk.X, padx=8, pady=(8,4))
            nxt = ttk.Button(btns, text='下一题', style='Primary.TButton', command=self.next_question)
            nxt.pack(side=tk.RIGHT)
        except Exception:
            pass

    def _hide_result_panel(self):
        try:
            if hasattr(self, 'result_panel') and self.result_panel.winfo_exists():
                try:
                    self.result_panel.destroy()
                except Exception:
                    pass
            # 恢复输入模块
            try:
                if hasattr(self, 'input_section'):
                    self.input_section.grid()
                if hasattr(self, 'buttons_section'):
                    self.buttons_section.grid()
            except Exception:
                pass
        except Exception:
            pass
    
    def review_wrong(self):
        """复习错题"""
        import json
        import os
        
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
                logger.log("进入错题复习模式")
                self.hint_used = False
                
                # 随机选择复习模式
                review_type = random.choice(["E2C", "C2E", "LISTEN"])
                
                # 更新问题标签样式，使其与现代UI设计一致
                if review_type == "E2C":
                    self.question_label.config(text=f"[复习] 英文：{word}", foreground=self.theme["primary"], font=('微软雅黑', 24, 'bold'))
                elif review_type == "C2E":
                    self.question_label.config(text=f"[复习] 中文：{meaning}", foreground=self.theme["primary"], font=('微软雅黑', 24, 'bold'))
                else:  # LISTEN
                    self.question_label.config(text="[复习] 请听单词并输入拼写：", foreground=self.theme["primary"], font=('微软雅黑', 24, 'bold'))
                    # 播放单词
                    speak(word)
                
                # 更新按钮状态和样式
                self.btn_hint.config(state=tk.NORMAL, style="Custom.TButton")
                self.btn_next.config(state=tk.DISABLED, style="Primary.TButton")
                self.btn_submit.config(state=tk.NORMAL, style="Primary.TButton")
                
                # 重置输入框样式
                self.entry.delete(0, tk.END)
                self.entry.focus_set()
                
            except Exception as e:
                print(f"复习错题出错: {e}")
                messagebox.showerror("错误", "加载错题记录失败")
        else:
            messagebox.showinfo("提示", "没有错题记录！")

    def check_answer(self):
        """检查用户答案是否正确"""
        user_answer = self.entry.get().strip()
        if not user_answer:
            self._show_feedback("请输入答案", error=True)
            return

        # 计算是否正确：对于 E2C/REVIEW 使用 meaning_matches 支持一词多义与模糊匹配
        if self.mode == "E2C":
            # meaning 在 data_manager 中现在是 list-of-meanings
            meaning_list = self.meaning if isinstance(self.meaning, list) else [self.meaning]
            matched, matched_meaning = meaning_matches(user_answer, meaning_list)
            is_correct = matched
            correct_answer = matched_meaning or (meaning_list[0] if meaning_list else "")
        elif self.mode == "C2E":
            correct_answer = self.word
            is_correct = user_answer.strip().lower() == correct_answer.lower()
        elif self.mode == "LISTEN":
            correct_answer = self.word
            is_correct = user_answer.strip().lower() == correct_answer.lower()
        elif self.mode == "REVIEW":
            # REVIEW 可能是英译汉或汉译英，这里优先尝试用 meaning_matches
            meaning_list = self.meaning if isinstance(self.meaning, list) else [self.meaning]
            matched, matched_meaning = meaning_matches(user_answer, meaning_list)
            if matched:
                is_correct = True
                correct_answer = matched_meaning or meaning_list[0]
            else:
                # 也可能用户输入的是英文单词（C2E 类型）
                is_correct = user_answer.strip().lower() == self.word.lower()
                correct_answer = self.word if is_correct else (meaning_list[0] if meaning_list else "")
        else:
            is_correct = False
            correct_answer = ""

        # 处理结果：嵌入式反馈，调整权重，自动跳题（答对）或显示正确答案（答错）
        if is_correct:
            self._show_success_animation()
            self._show_feedback(f"✅ 正确！ {self.get_streak_message()}", success=True)
            try:
                adjust_word_weight(self.word, correct=True)
            except Exception:
                pass
            # 更新统计并显示结果面板，然后稍作停顿再下一题
            self.update_stats(True)
            self.entry.delete(0, tk.END)
            self.btn_submit.config(state=tk.DISABLED)
            try:
                meaning_list = self.meaning if isinstance(self.meaning, list) else [self.meaning]
                self._show_result_panel(meaning_list)
            except Exception:
                pass
            # 稍作停顿再下一题（使用受控定时器，保存 id 以便手动下一题时取消）
            try:
                # 根据用户设置决定是否自动下一题
                auto_next_enabled = bool(self.stats.get('auto_next', True))
                auto_delay = int(self.stats.get('auto_next_delay', 1200)) if auto_next_enabled else None

                if auto_next_enabled:
                    # 取消已有的自动跳题（若存在）再设定新的
                    if getattr(self, '_auto_next_id', None):
                        try:
                            self.root.after_cancel(self._auto_next_id)
                        except Exception:
                            pass
                        self._auto_next_id = None

                    # 强制最小延迟 200ms
                    try:
                        auto_delay = max(200, int(auto_delay))
                    except Exception:
                        auto_delay = 1200

                    self._auto_next_id = self.root.after(auto_delay, lambda: self._do_auto_next())
                else:
                    # 用户禁用自动下一题：不设定定时器
                    pass
            except Exception:
                # 作为后备，如果自动开启则使用默认延迟
                try:
                    if self.stats.get('auto_next', True):
                        self._auto_next_id = self.root.after(1200, self._do_auto_next)
                except Exception:
                    pass
            return
        else:
            self._show_feedback(f"❌ 错误！正确答案：{correct_answer}", error=True)
            try:
                save_wrong(self.word, self.meaning)
            except Exception:
                pass
            try:
                adjust_word_weight(self.word, correct=False)
            except Exception:
                pass
            # 更新统计但不立即跳题，用户可查看答案后手动下一题
            self.update_stats(False)
            self.entry.delete(0, tk.END)
            self.btn_submit.config(state=tk.DISABLED)
            self.btn_next.config(state=tk.NORMAL)
            try:
                self.btn_next.focus_set()
            except Exception:
                pass

    def _show_feedback(self, text, success=False, error=False):
        """在页面内显示结果反馈，而不是使用弹窗。"""
        try:
            # 如果已有 feedback_label 则更新文本
            if hasattr(self, 'feedback_label') and self.feedback_label.winfo_exists():
                self.feedback_label.config(text=text, foreground=(self.theme['success'] if success else (self.theme['error'] if error else self.theme['text'])))
                return
        except Exception:
            pass

        try:
            # 优先放到 question_card 中（保证固定位置）
            parent = None
            if hasattr(self, 'question_label'):
                try:
                    parent = self.question_label.master
                except Exception:
                    parent = None
            if parent is None:
                parent = self.entry.master if hasattr(self, 'entry') else self.root

            self.feedback_label = ttk.Label(parent, text=text, font=('微软雅黑', 12, 'bold'))
            # 如果 parent 支持 grid（question_card 使用 grid），则使用 grid 放置在 row=2
            try:
                if hasattr(parent, 'grid_rowconfigure'):
                    self.feedback_label.grid(row=2, column=0, pady=(6, 0), sticky='n')
                else:
                    self.feedback_label.pack(pady=6)
            except Exception:
                try:
                    self.feedback_label.pack(pady=6)
                except Exception:
                    pass

            if success:
                self.root.after(1800, lambda: (self.feedback_label.destroy() if getattr(self, 'feedback_label', None) and self.feedback_label.winfo_exists() else None))
        except Exception:
            pass
    
    def _show_success_animation(self):
        """显示成功动画效果（适配新UI）"""
        # 使用标签闪烁效果替代按钮闪烁
        original_color = self.theme["text"]
        success_color = self.theme["success"]
        
        def blink():
            for _ in range(3):
                self.question_label.config(foreground=success_color)
                self.root.update()
                time.sleep(0.1)
                self.question_label.config(foreground=original_color)
                self.root.update()
                time.sleep(0.1)
        
        # 在主线程中执行动画
        threading.Thread(target=blink, daemon=True).start()

    def _do_auto_next(self):
        """由自动定时器调用以执行下一题并清理定时器标志。"""
        try:
            # 清理定时器 id
            if getattr(self, '_auto_next_id', None):
                self._auto_next_id = None
        except Exception:
            pass

        try:
            # 调用 next_question 切换到下一题
            self.next_question()
        except Exception:
            pass
    
    def show_success_animation(self):
        """显示成功动画效果"""
        # 闪烁标签文字颜色 - 使用新的question_label
        original_color = self.question_label.cget("foreground")
        
        def flash():
            for _ in range(2):
                self.question_label.config(foreground=self.theme["success"])
                self.root.update()
                time.sleep(0.1)
                self.question_label.config(foreground=original_color)
                self.root.update()
                time.sleep(0.1)
        
        # 在非主线程中运行动画
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
        # 临时改变按钮状态以提供视觉反馈
        self.btn_voice.config(state=tk.DISABLED, text="🎤 正在聆听...")
        self.root.update()
        
        # 调用语音识别
        text = recognize_speech()
        
        # 恢复按钮状态
        self.btn_voice.config(state=tk.NORMAL, text="🎤 语音输入")
        
        if not text:
            messagebox.showerror("错误", "没听清楚，再试一次吧～")
            return
        
        # 插入识别结果并提供视觉反馈
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        
        # 短暂高亮输入框以提示用户已识别内容
        original_bg = self.entry.cget("fieldbackground")
        self.entry.config(fieldbackground="#E3F2FD")
        self.root.update()
        self.root.after(500, lambda: self.entry.config(fieldbackground=original_bg))
        
        self.check_answer()