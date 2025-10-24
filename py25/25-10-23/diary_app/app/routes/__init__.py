"""路由包 - 包含所有API路由定义"""
# 从各个路由模块导入蓝图
from app.routes.auth_routes import auth_bp
from app.routes.diary_routes import diary_bp
from app.routes.user_routes import user_bp
from app.routes.admin_routes import admin_bp
from app.routes.main_routes import main_bp

# 导出所有蓝图
__all__ = [
    'auth_bp',
    'diary_bp',
    'user_bp',
    'admin_bp',
    'main_bp'
]