import json
import os
from datetime import datetime, timedelta
# 导入日志模块
try:
    from dictation_assistant.logger import logger
except ImportError:
    try:
        from logger import logger
    except ImportError:
        print("警告：在data_manager.py中无法导入日志模块")
        # 创建增强版的DummyLogger，支持模块统计数据的存储和加载
        class DummyLogger:
            def __init__(self):
                self.MODULE_STATS_FILE = "module_stats.json"
                # 初始化模块统计数据结构
                self.module_stats = {
                    "E2C": {"total": 0, "correct": 0, "wrong": 0},
                    "C2E": {"total": 0, "correct": 0, "wrong": 0},
                    "LISTEN": {"total": 0, "correct": 0, "wrong": 0},
                    "review": {"total": 0, "correct": 0, "wrong": 0}
                }
                # 从文件加载历史统计数据
                self.load_module_stats()
                
                # 为兼容学习统计页面，添加session_log属性
                self.session_log = {
                    "module_percentage": {}
                }
            
            def log(self, *args, **kwargs): 
                pass
                
            def log_error(self, *args, **kwargs): 
                pass
            
            def log_answer(self, module, is_correct, word=None):
                """记录答题情况"""
                if module in self.module_stats:
                    self.module_stats[module]["total"] += 1
                    if is_correct:
                        self.module_stats[module]["correct"] += 1
                    else:
                        self.module_stats[module]["wrong"] += 1
                    # 保存更新后的数据
                    self.save_module_stats()
            
            def save_module_stats(self):
                """保存模块统计数据到文件"""
                try:
                    import json
                    with open(self.MODULE_STATS_FILE, "w", encoding="utf-8") as f:
                        json.dump(self.module_stats, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"保存模块统计数据失败: {e}")
            
            def load_module_stats(self):
                """从文件加载模块统计数据"""
                try:
                    import os
                    import json
                    if os.path.exists(self.MODULE_STATS_FILE):
                        with open(self.MODULE_STATS_FILE, "r", encoding="utf-8") as f:
                            saved_stats = json.load(f)
                            # 更新各模块的统计数据
                            for module, stats in saved_stats.items():
                                if module in self.module_stats:
                                    self.module_stats[module].update(stats)
                except Exception as e:
                    print(f"加载模块统计数据失败: {e}")
            
            def close(self, *args, **kwargs): 
                # 确保程序关闭时保存数据
                self.save_module_stats()
        
        logger = DummyLogger()

# 默认内置词典（作为 fallback）
_default_word_dict = {
    "freedom": "自由",
    "knowledge": "知识",
    "success": "成功",
    "challenge": "挑战",
    "opportunity": "机会",
    "determination": "决心",
    "creativity": "创造力",
    "inspiration": "灵感"
}

# 支持从 JSON 文件加载词典（允许一词多义：值可以是字符串或字符串列表）
WORD_FILE = "word_dict.json"


def load_word_dict():
    """加载词典 JSON，返回 {word: [meaning,...]} 格式。
    如果文件不存在，返回内置默认词典，且把单义字符串包装成列表。
    """
    data = {}
    if os.path.exists(WORD_FILE):
        try:
            with open(WORD_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            # 允许两种格式：{word: meaning} 或 {word: [meanings]}
            for k, v in raw.items():
                if isinstance(v, list):
                    data[k] = [str(x) for x in v]
                else:
                    data[k] = [str(v)]
            if data:
                return data
        except Exception:
            pass

    # 退回到默认词典
    for k, v in _default_word_dict.items():
        data[k] = [v]
    return data


# 导出变量：word_dict（值为 list-of-meanings），便于其它模块直接使用
word_dict = load_word_dict()

# 文件常量
WRONG_FILE = "wrong_words.json"
STATS_FILE = "learning_stats.json"
WEIGHT_FILE = "word_weights.json"
LOG_FILE = "learning_log.json"
DAILY_GOALS_FILE = "daily_goals.json"


def _write_json_if_possible(path, value):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"写入文件失败 {path}: {e}")
        return False


def reset_all_data(base_dirs=None):
    """集中清空/重置所有用户可变的持久化数据。
    会尝试在提供的 base_dirs 列表（或当前应用目录与其父目录）中写入默认结构。
    返回成功写入的文件路径列表和失败列表。
    """
    app_dir = os.path.dirname(os.path.abspath(__file__))
    bases = base_dirs or [app_dir, os.path.dirname(app_dir), os.getcwd()]

    # 重置目标集合：包括模块统计文件，确保“学习统计”页面完全归零
    targets = {
        WORD_FILE: load_word_dict(),  # 不清空词典，保留已有词典（fallback 会使用默认）
        WRONG_FILE: [],
        STATS_FILE: {
            "total_questions": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "streak": 0,
            "best_streak": 0
        },
        WEIGHT_FILE: {},
        LOG_FILE: [],
        DAILY_GOALS_FILE: {"daily_target": 20, "date": datetime.now().strftime('%Y-%m-%d'), "history": {}},
        # 新增：模块统计文件也归零
        "module_stats.json": {
            "E2C": {"total": 0, "correct": 0, "wrong": 0},
            "C2E": {"total": 0, "correct": 0, "wrong": 0},
            "LISTEN": {"total": 0, "correct": 0, "wrong": 0},
            "review": {"total": 0, "correct": 0, "wrong": 0}
        }
    }

    written = []
    failed = []

    for base in bases:
        for fname, default in targets.items():
            path = os.path.join(base, fname)
            try:
                # 如果目标是词典，我们不覆盖现有文件；仅确保文件存在
                if fname == WORD_FILE:
                    if not os.path.exists(path):
                        _write_json_if_possible(path, default)
                        written.append(path)
                    continue

                ok = _write_json_if_possible(path, default)
                if ok:
                    written.append(path)
                else:
                    failed.append(path)
            except Exception as e:
                failed.append(path)

    # 保留模块使用统计，不在此处重置；仅返回写入结果
    return written, failed


def save_wrong(word, meaning):
    """保存错题记录"""
    wrongs = []
    if os.path.exists(WRONG_FILE):
        try:
            with open(WRONG_FILE, "r", encoding="utf-8") as f:
                wrongs = json.load(f)
        except:
            pass
    
    # 检查是否已存在相同的错题
    exists = False
    for item in wrongs:
        if word in item and item[word] == meaning:
            exists = True
            break
    
    if not exists:
        wrongs.append({word: meaning})
        
        try:
            with open(WRONG_FILE, "w", encoding="utf-8") as f:
                json.dump(wrongs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存错题失败: {e}")
    
    # 更新单词权重
    update_word_weight(word)


def update_word_weight(word):
    """更新单词权重（出错越多权重越高）"""
    # 兼容旧接口：将其视为一次错误反馈
    try:
        adjust_word_weight(word, correct=False)
    except Exception:
        # 最后手段：回退到简单写入
        try:
            weights = load_word_weights()
            if isinstance(weights.get(word), dict):
                entry = weights.get(word)
                entry['weight'] = int(entry.get('weight', 1)) + 1
                weights[word] = entry
                save_word_weights(weights)
            else:
                weights[word] = weights.get(word, 0) + 1
                with open(WEIGHT_FILE, "w", encoding="utf-8") as f:
                    json.dump(weights, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"更新单词权重失败: {e}")


def adjust_word_weight(word, correct=True, min_weight=1, max_weight=20):
    """根据答题正确性调整单词权重。
    correct=True 时表示答对，适当降低权重；答错则增加权重。
    权重范围限制在 [min_weight, max_weight]。默认最小为1。
    """
    # 使用结构化权重：{word: {'weight': int, 'interval': int, 'last_seen': iso, 'next_due': iso}}
    now = datetime.now()
    weights = load_word_weights()
    entry = weights.get(word) or {
        'weight': 1,
        'interval': 1,
        'last_seen': None,
        'next_due': None
    }

    if isinstance(entry, (int, float)):
        # 兼容旧数值格式
        entry = {
            'weight': max(1, int(entry)),
            'interval': 1,
            'last_seen': None,
            'next_due': None
        }

    if correct:
        # 答对：降低权重并延长间隔（简单倍增策略）
        entry['weight'] = max(min_weight, int(entry.get('weight', 1)) - 1)
        interval = max(1, int(entry.get('interval', 1)))
        interval = min(60, interval * 2)
        entry['interval'] = interval
        entry['last_seen'] = now.strftime('%Y-%m-%d %H:%M:%S')
        next_due = now + timedelta(days=interval)
        entry['next_due'] = next_due.strftime('%Y-%m-%d %H:%M:%S')
    else:
        # 答错：增加权重并重置间隔到 1 天
        entry['weight'] = min(max_weight, int(entry.get('weight', 1)) + 1)
        entry['interval'] = 1
        entry['last_seen'] = now.strftime('%Y-%m-%d %H:%M:%S')
        entry['next_due'] = now.strftime('%Y-%m-%d %H:%M:%S')

    weights[word] = entry
    try:
        save_word_weights(weights)
    except Exception as e:
        print(f"调整单词权重失败: {e}")


def load_word_weights():
    """加载单词权重"""
    if os.path.exists(WEIGHT_FILE):
        try:
            with open(WEIGHT_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            normalized = {}
            for w, v in (raw or {}).items():
                if isinstance(v, dict):
                    normalized[w] = v
                else:
                    try:
                        iv = int(v)
                    except Exception:
                        iv = 1
                    normalized[w] = {
                        'weight': max(1, iv),
                        'interval': 1,
                        'last_seen': None,
                        'next_due': None
                    }
            return normalized
        except Exception:
            pass
    return {}


def save_word_weights(weights: dict):
    """将结构化的权重字典保存到文件。"""
    try:
        with open(WEIGHT_FILE, 'w', encoding='utf-8') as f:
            json.dump(weights, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存单词权重失败: {e}")


def levenshtein(a: str, b: str) -> int:
    """计算两个字符串的 Levenshtein 编辑距离（简单实现）。"""
    a = a or ""
    b = b or ""
    if a == b:
        return 0
    la = len(a)
    lb = len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    # 使用动态规划，空间优化为一维
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i] + [0] * lb
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            curr[j] = min(prev[j] + 1, curr[j-1] + 1, prev[j-1] + cost)
        prev = curr
    return prev[lb]


from typing import Tuple


def meaning_matches(user: str, meaning_list) -> Tuple[bool, str]:
    """判断用户输入是否与 meanings 列表中的任一意义匹配。
    返回 (matched: bool, matched_meaning: str_or_empty)。匹配策略：
    - 标准化小写、去首尾空白
    - 精确匹配或包含关系（用户输入包含词典释义或反之）
    - 若以上不成立，使用 Levenshtein 编辑距离作为模糊匹配，阈值基于长度
    """
    if not user:
        return False, ""
    u = str(user).strip().lower()
    for m in (meaning_list or []):
        mm = str(m).strip().lower()
        if not mm:
            continue
        if u == mm:
            return True, m
        if u in mm or mm in u:
            return True, m
        # 模糊匹配阈值：对于短词使用较小阈值，对于长句子使用相对比例
        dist = levenshtein(u, mm)
        if len(mm) <= 6:
            if dist <= 1:
                return True, m
        else:
            # 允许约 15% 的编辑距离
            if dist <= max(1, int(len(mm) * 0.15)):
                return True, m
    return False, ""


def load_stats():
    """加载学习统计信息"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    
    # 返回默认统计信息
    return {
        "total_questions": 0,
        "correct_answers": 0,
        "wrong_answers": 0,
        "streak": 0,
        "best_streak": 0
    }


def save_stats(stats):
    """保存学习统计信息"""
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存统计信息失败: {e}")


def log_start_session():
    """记录学习会话开始时间（兼容旧接口）"""
    logger.log("学习会话开始")
    return 0

def log_end_session(session_index):
    """记录学习会话结束时间（兼容旧接口）"""
    pass


def load_daily_goals():
    """加载每日学习目标"""
    if os.path.exists(DAILY_GOALS_FILE):
        try:
            with open(DAILY_GOALS_FILE, "r", encoding="utf-8") as f:
                goals = json.load(f)
                # 确保包含所有必要字段
                if "daily_target" not in goals:
                    goals["daily_target"] = 20  # 默认每日目标20个单词
                if "date" not in goals:
                    goals["date"] = datetime.now().strftime("%Y-%m-%d")
                if "history" not in goals:
                    goals["history"] = {}
                return goals
        except Exception as e:
            print(f"加载每日目标失败: {e}")
    
    # 返回默认目标
    return {
        "daily_target": 20,  # 默认每日目标20个单词
        "date": datetime.now().strftime("%Y-%m-%d"),
        "history": {}
    }


def save_daily_goals(goals):
    """保存每日学习目标"""
    try:
        with open(DAILY_GOALS_FILE, "w", encoding="utf-8") as f:
            json.dump(goals, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存每日目标失败: {e}")


def update_daily_target(new_target):
    """更新每日目标数量"""
    goals = load_daily_goals()
    goals["daily_target"] = int(new_target)
    save_daily_goals(goals)
    return goals


def get_today_goal():
    """获取今日目标和进度"""
    goals = load_daily_goals()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 如果日期变了，更新目标日期
    if goals["date"] != today:
        goals["date"] = today
        save_daily_goals(goals)
    
    # 获取今日学习统计
    today_stats = {"total": 0, "correct": 0}
    if today in goals["history"]:
        today_stats = goals["history"][today]
    
    return {
        "target": goals["daily_target"],
        "current": today_stats["total"],
        "correct": today_stats["correct"],
        "percentage": round((today_stats["total"] / goals["daily_target"]) * 100, 1) if goals["daily_target"] > 0 else 0
    }


def update_today_progress(is_correct):
    """更新今日学习进度"""
    goals = load_daily_goals()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 确保今日记录存在
    if today not in goals["history"]:
        goals["history"][today] = {"total": 0, "correct": 0}
    
    # 更新统计
    goals["history"][today]["total"] += 1
    if is_correct:
        goals["history"][today]["correct"] += 1
    
    save_daily_goals(goals)
    return get_today_goal()


def adjust_today_progress(delta_total=0, delta_correct=0, clamp_non_negative=True):
    """手动维护今日进度：增减总数与正确数。
    - `delta_total`: 今日总答题数的增量，可为负数
    - `delta_correct`: 今日正确数的增量，可为负数
    - `clamp_non_negative`: 是否避免出现负数并保证`correct<=total`
    返回最新的`get_today_goal()`。
    """
    goals = load_daily_goals()
    today = datetime.now().strftime("%Y-%m-%d")
    # 确保今日记录存在
    if today not in goals["history"]:
        goals["history"][today] = {"total": 0, "correct": 0}
    # 计算新值
    total = goals["history"][today]["total"] + int(delta_total)
    correct = goals["history"][today]["correct"] + int(delta_correct)
    if clamp_non_negative:
        total = max(0, total)
        correct = max(0, correct)
        # 正确数不超过总数
        if correct > total:
            correct = total
    goals["history"][today]["total"] = total
    goals["history"][today]["correct"] = correct
    save_daily_goals(goals)
    return get_today_goal()


def reset_today_history():
    """重置今日进度（total、correct归零）。返回最新的`get_today_goal()`"""
    goals = load_daily_goals()
    today = datetime.now().strftime("%Y-%m-%d")
    goals["history"][today] = {"total": 0, "correct": 0}
    save_daily_goals(goals)
    return get_today_goal()


def get_history_records(days=7):
    """获取历史学习记录
    
    Args:
        days: 获取最近几天的记录，默认为7天
    
    Returns:
        list: 包含日期、总答题数、正确数、准确率的记录列表
    """
    goals = load_daily_goals()
    history_data = []
    
    # 获取所有历史记录
    for date_str, stats in goals["history"].items():
        accuracy = 0
        if stats["total"] > 0:
            accuracy = round((stats["correct"] / stats["total"]) * 100, 1)
        
        history_data.append({
            "date": date_str,
            "total": stats["total"],
            "correct": stats["correct"],
            "accuracy": accuracy
        })
    
    # 按日期倒序排序
    history_data.sort(key=lambda x: x["date"], reverse=True)
    
    # 返回最近的指定天数记录
    return history_data[:days]