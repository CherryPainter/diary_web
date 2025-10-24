"""扩展模块 - 集中管理所有Flask扩展"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
import os

# 数据库扩展
db = SQLAlchemy()

# 登录管理扩展
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # 设置登录视图
login_manager.login_message = '请先登录后再访问该页面'
login_manager.login_message_category = 'info'

# CSRF保护扩展
csrf = CSRFProtect()

# 限流扩展
limiter = Limiter(
    key_func=get_remote_address,  # 使用客户端IP作为限流键
    default_limits=[],  # 默认不限流，在路由上单独设置
    storage_uri='memory://',  # 使用内存存储（生产环境建议使用Redis）
    headers_enabled=True  # 在响应头中添加限流信息
)


def configure_logging(app):
    """配置应用日志系统"""
    # 设置日志级别
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    app.logger.setLevel(log_level)
    
    # 创建日志处理器
    handlers = []
    
    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    handlers.append(console_handler)
    
    # 文件日志处理器（如果配置了）
    if app.config['LOG_FILE']:
        # 确保日志目录存在
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建文件日志处理器
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=1024 * 1024 * 10,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(log_level)
        handlers.append(file_handler)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    for handler in handlers:
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
    
    # 添加安全日志记录器
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)
    for handler in handlers:
        security_logger.addHandler(handler)


def register_extensions(app):
    """注册所有扩展到Flask应用"""
    # 初始化数据库
    db.init_app(app)
    
    # 初始化登录管理器
    login_manager.init_app(app)
    
    # 初始化CSRF保护
    csrf.init_app(app)
    
    # 初始化限流扩展
    limiter.init_app(app)
    
    # 配置日志
    configure_logging(app)
    
    # 注册登录用户加载回调
    from app.models.user import User  # 避免循环导入
    
    @login_manager.user_loader
    def load_user(user_id):
        """加载用户的回调函数"""
        return User.query.get(int(user_id))


def create_tables(app):
    """创建数据库表并初始化默认数据"""
    with app.app_context():
        # 导入所有模型，确保它们被注册
        from app.models import user, diary, system
        
        # 创建表
        db.create_all()
        
        # 初始化默认数据
        from app.services.system_service import init_default_data
        init_default_data()