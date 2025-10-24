"""表单包 - 包含所有表单定义"""
# 从各个表单模块导入表单类
from app.forms.auth import RegisterForm, LoginForm
from app.forms.diary import DiaryForm
from app.forms.admin import AdminUserForm, SystemStatusForm

# 导出所有表单类
__all__ = [
    # 认证相关表单
    'RegisterForm',      # 注册表单
    'LoginForm',         # 登录表单
    # 日记相关表单
    'DiaryForm',         # 日记编辑表单
    # 管理员相关表单
    'AdminUserForm',     # 管理员用户管理表单
    'SystemStatusForm'   # 系统状态管理表单
]