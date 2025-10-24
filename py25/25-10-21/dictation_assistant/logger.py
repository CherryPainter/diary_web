import os
import sys
import time
import traceback
from datetime import datetime
import json
import threading
import queue

# 日志文件路径
LOG_FILE_TXT = "app_log.txt"
LOG_FILE_JSON = "app_log.json"

class Logger:
    def __init__(self):
        self.start_time = datetime.now()
        self.session_id = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.is_running = True
        self.exception_occurred = False
        self.total_words = 0
        self.MODULE_STATS_FILE = "module_stats.json"
        self.module_stats = {
            "E2C": {"total": 0, "correct": 0, "wrong": 0},
            "C2E": {"total": 0, "correct": 0, "wrong": 0},
            "LISTEN": {"total": 0, "correct": 0, "wrong": 0},
            "review": {"total": 0, "correct": 0, "wrong": 0}
        }
        # 从文件加载历史统计数据
        self.load_module_stats()
        
        self.session_log = {
            "session_id": self.session_id,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None,
            "duration_seconds": 0,
            "exception_occurred": False,
            "total_words": 0,
            "module_stats": self.module_stats.copy(),
            "module_percentage": {},
            "accuracy_by_module": {}
        }
        self.log("应用程序启动", "INFO")
        # 异步日志队列与工作线程，避免阻塞主流程
        self._log_queue = queue.Queue(maxsize=1000)
        self._worker_stop = threading.Event()
        self._worker = threading.Thread(target=self._worker_loop, name="LoggerWorker", daemon=True)
        self._worker.start()
    
    def _worker_loop(self):
        """后台线程：批量写入文本日志，避免多次打开文件"""
        while not self._worker_stop.is_set() or not self._log_queue.empty():
            entries = []  # 确保finally可用，避免未定义
            try:
                try:
                    entry = self._log_queue.get(timeout=0.2)
                except queue.Empty:
                    continue
                # 批量取最多50条，减少IO
                entries = [entry]
                while len(entries) < 50:
                    try:
                        entries.append(self._log_queue.get_nowait())
                    except queue.Empty:
                        break
                with open(LOG_FILE_TXT, "a", encoding="utf-8") as f:
                    f.writelines(entries)
            except Exception as e:
                # 不影响主流程
                try:
                    print(f"日志写入失败: {e}")
                except Exception:
                    pass
            finally:
                # 标记队列任务完成
                for _ in range(len(entries)):
                    try:
                        self._log_queue.task_done()
                    except Exception:
                        pass
    
    def log(self, message, level="INFO"):
        """记录日志到文本文件（异步）"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        try:
            # 如果队列已满，丢弃最旧的以避免阻塞
            if self._log_queue.full():
                try:
                    self._log_queue.get_nowait()
                    self._log_queue.task_done()
                except Exception:
                    pass
            self._log_queue.put_nowait(log_entry)
        except Exception:
            # 异常时直接降级为同步写入，仍然不抛出
            try:
                with open(LOG_FILE_TXT, "a", encoding="utf-8") as f:
                    f.write(log_entry)
            except Exception as e:
                try:
                    print(f"日志写入失败: {e}")
                    print(log_entry)
                except Exception:
                    pass
    
    def log_answer(self, module, is_correct, word=None):
        """记录答题情况"""
        if module in self.module_stats:
            self.module_stats[module]["total"] += 1
            if is_correct:
                self.module_stats[module]["correct"] += 1
            else:
                self.module_stats[module]["wrong"] += 1
            
            self.total_words += 1
            self.session_log["total_words"] = self.total_words
            
            if word:
                status = "正确" if is_correct else "错误"
                self.log(f"[{module}] 单词 '{word}' 答题{status}", "ANSWER")
            
            # 保存模块统计数据到文件，确保数据持久化
            self.save_module_stats()
    
    def log_exception(self, exception, error_message=None):
        """记录异常情况"""
        self.exception_occurred = True
        self.session_log["exception_occurred"] = True
        
        error_info = str(exception)
        if error_message:
            error_info = f"{error_message}: {error_info}"
        
        stack_trace = traceback.format_exc()
        
        self.log(f"异常发生: {error_info}", "ERROR")
        self.log(f"堆栈跟踪: {stack_trace}", "ERROR")
    
    def log_error(self, message):
        """记录错误信息"""
        self.log(message, "ERROR")
    
    def update_module_stats(self):
        """更新模块统计信息和百分比"""
        total_all = sum(module["total"] for module in self.module_stats.values())
        
        if total_all > 0:
            for module, stats in self.module_stats.items():
                if stats["total"] > 0:
                    percentage = (stats["total"] / total_all) * 100
                    accuracy = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
                    self.session_log["module_percentage"][module] = round(percentage, 1)
                    self.session_log["accuracy_by_module"][module] = round(accuracy, 1)
    
    def save_session_log(self):
        """保存会话日志到JSON文件（容错+原子写），不影响主流程"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        self.session_log["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        self.session_log["duration_seconds"] = round(duration, 2)
        self.session_log["module_stats"] = self.module_stats.copy()
        self.update_module_stats()
        all_logs = []
        if os.path.exists(LOG_FILE_JSON):
            try:
                with open(LOG_FILE_JSON, "r", encoding="utf-8") as f:
                    all_logs = json.load(f)
                if not isinstance(all_logs, list):
                    all_logs = []
            except Exception as e:
                # 备份损坏文件，避免覆盖丢失
                try:
                    backup = LOG_FILE_JSON + ".bak"
                    if os.path.exists(LOG_FILE_JSON):
                        try:
                            os.replace(LOG_FILE_JSON, backup)
                        except Exception:
                            pass
                except Exception:
                    pass
                self.log(f"读取日志文件失败，已备份: {e}", "ERROR")
                all_logs = []
        all_logs.append(self.session_log)
        # 原子写入，先写临时文件再替换
        try:
            tmp_path = LOG_FILE_JSON + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(all_logs, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, LOG_FILE_JSON)
        except Exception as e:
            # 降级写入为NDJSON以保证数据不丢
            try:
                with open(LOG_FILE_JSON + ".ndjson", "a", encoding="utf-8") as f:
                    f.write(json.dumps(self.session_log, ensure_ascii=False) + "\n")
            except Exception:
                pass
            self.log(f"保存会话日志失败: {e}", "ERROR")
    
    def generate_summary(self):
        """生成会话摘要"""
        self.update_module_stats()
        
        summary = []
        summary.append(f"\n===== 会话摘要 =====")
        summary.append(f"会话ID: {self.session_id}")
        summary.append(f"开始时间: {self.session_log['start_time']}")
        summary.append(f"结束时间: {self.session_log['end_time']}")
        summary.append(f"持续时间: {self.session_log['duration_seconds']}秒")
        summary.append(f"异常状态: {'是' if self.exception_occurred else '否'}")
        summary.append(f"总背单词数: {self.total_words}")
        summary.append("")
        summary.append("各模块统计:")
        
        for module, stats in self.module_stats.items():
            if stats["total"] > 0:
                accuracy = round((stats["correct"] / stats["total"]) * 100, 1)
                percentage = self.session_log["module_percentage"].get(module, 0)
                summary.append(f"  {module}: 答题{stats['total']}次 (正确率: {accuracy}%, 占比: {percentage}%)")
        
        summary.append("====================\n")
        return "\n".join(summary)
    
    def load_module_stats(self):
        """从文件加载模块统计数据"""
        try:
            if os.path.exists(self.MODULE_STATS_FILE):
                with open(self.MODULE_STATS_FILE, "r", encoding="utf-8") as f:
                    saved_stats = json.load(f)
                    # 更新各模块的统计数据
                    for module, stats in saved_stats.items():
                        if module in self.module_stats:
                            self.module_stats[module].update(stats)
                    # 重新计算总单词数
                    self.total_words = sum(module["total"] for module in self.module_stats.values())
        except Exception as e:
            print(f"加载模块统计数据失败: {e}")
    
    def save_module_stats(self):
        """保存模块统计数据到文件"""
        try:
            with open(self.MODULE_STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.module_stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模块统计数据失败: {e}")
    
    def close(self):
        """关闭日志，保存会话信息，并优雅停止后台线程"""
        self.is_running = False
        try:
            self.save_session_log()
        except Exception:
            pass
        # 保存模块统计数据
        try:
            self.save_module_stats()
        except Exception:
            pass
        # 生成并记录摘要
        try:
            summary = self.generate_summary()
            self.log(summary, "SUMMARY")
            self.log("应用程序关闭", "INFO")
        except Exception:
            pass
        # 停止后台线程并清空队列
        try:
            self._worker_stop.set()
            # 使用自定义的join_with_timeout函数，避免程序卡死
            self._join_queue_with_timeout(0.5)
            # 给线程一些时间结束，设置超时避免阻塞
            self._worker.join(timeout=0.5)
        except Exception:
            pass
    
    def _join_queue_with_timeout(self, timeout):
        """带超时的队列等待函数，避免无限阻塞"""
        import time
        start_time = time.time()
        remaining = timeout
        
        while remaining > 0 and not self._log_queue.empty():
            time.sleep(0.05)  # 小间隔检查，避免CPU占用过高
            remaining = timeout - (time.time() - start_time)
        
        # 超时后清空队列，避免阻塞
        if not self._log_queue.empty():
            try:
                while not self._log_queue.empty():
                    try:
                        self._log_queue.get_nowait()
                        self._log_queue.task_done()
                    except queue.Empty:
                        break
            except Exception:
                pass

# 创建全局日志实例
logger = Logger()

# 重定向异常处理
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.log_exception(exc_value, "未处理异常")
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception