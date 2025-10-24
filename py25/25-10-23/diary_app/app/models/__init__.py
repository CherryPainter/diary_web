"""数据模型包 - 集中导出所有数据库模型"""
# 从各个模块导入模型
from app.models.user import User, SecurityProfile, UserLoginAttempt
from app.models.diary import DiaryEntry, DiaryEntry as Diary, DiaryCategory, DiaryTag, DiaryComment
from app.models.system import SystemStatus, SystemLog

# 导出所有模型
__all__ = [
    # 用户相关模型
    'User',
    'SecurityProfile',
    'UserLoginAttempt',
    # 日记相关模型
    'Diary',
    'DiaryEntry',
    'DiaryCategory',
    'DiaryTag',
    'DiaryComment',
    # 系统相关模型
    'SystemStatus',
    'SystemLog'
]