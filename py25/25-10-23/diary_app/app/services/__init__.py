"""服务层包 - 集中管理所有业务逻辑服务实例"""
# 从各个服务模块导入服务类
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.diary_service import DiaryService
from app.services.system_service import SystemService
from app.services.admin_service import AdminService

# 导入模块级函数
from app.services.diary_service import (
    get_diary_statistics,
    get_system_statistics,
    get_recent_system_activity
)

# 创建服务实例（单例模式）
# 使用服务实例而非直接使用类，便于依赖注入和统一管理
auth_service = AuthService()
user_service = UserService()
diary_service = DiaryService()
system_service = SystemService()
admin_service = AdminService()

# 导出所有服务实例
__all__ = [
    # 服务实例
    'auth_service',      # 认证服务实例 - 处理登录、注册等认证相关业务
    'user_service',      # 用户服务实例 - 处理用户信息管理相关业务
    'diary_service',     # 日记服务实例 - 处理日记CRUD相关业务
    'system_service',    # 系统服务实例 - 处理系统配置和状态管理相关业务
    'admin_service',     # 管理员服务实例 - 处理管理员特定操作相关业务
    
    # 模块级函数
    'get_diary_statistics',          # 获取用户日记统计信息
    'get_system_statistics',         # 获取系统整体统计信息
    'get_recent_system_activity'     # 获取最近的系统活动
]