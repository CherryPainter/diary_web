"""配置模块 - 提供多环境配置管理"""
import os
from datetime import timedelta
from pathlib import Path

class Config:
    """基础配置类 - 包含所有环境共用的设置"""
    # 安全配置
    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(32)
    SESSION_COOKIE_HTTPONLY = True  # 防止JavaScript访问cookies
    SESSION_COOKIE_SAMESITE = "Lax"  # 防止CSRF攻击
    SESSION_COOKIE_SECURE = False  # 生产环境应启用HTTPS并设置为True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)  # 会话超时时间
    
    # 表单和CSRF配置
    WTF_CSRF_ENABLED = True  # 启用CSRF保护
    
    # 数据库配置
    @staticmethod
    def get_database_url():
        """获取数据库URL，优先使用DATABASE_URL环境变量，其次尝试MySQL配置，最后回退到SQLite"""
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL:
            return DATABASE_URL
            
        # 尝试MySQL配置
        MYSQL_HOST = os.getenv("MYSQL_HOST")
        MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
        MYSQL_DB = os.getenv("MYSQL_DB")
        MYSQL_USER = os.getenv("MYSQL_USER")
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
        
        if all([MYSQL_HOST, MYSQL_DB, MYSQL_USER, MYSQL_PASSWORD]):
            return f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
        
        # 回退到SQLite（开发环境）
        instance_dir = Path('instance')
        instance_dir.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{instance_dir / 'diary.db'}"
    
    # SQLAlchemy配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 显示SQL语句（生产环境禁用）
    
    # 安全配置
    PASSWORD_COMPLEXITY_REQUIRED = True  # 是否要求密码复杂度
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))  # 最大登录尝试次数
    LOCKOUT_DURATION = int(os.getenv("LOCKOUT_DURATION", "30"))  # 账户锁定时长（分钟）
    
    # 限流配置
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "200 per day, 50 per hour")  # 默认限流规则
    LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "10 per minute, 30 per hour")  # 登录接口限流规则
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # 日志级别
    LOG_FILE = os.getenv("LOG_FILE")  # 日志文件路径
    
    # 上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 最大上传文件大小
    UPLOAD_FOLDER = 'uploads'  # 上传文件保存目录
    
    # 系统配置
    REGISTRATION_OPEN = os.getenv("REGISTRATION_OPEN", "True").lower() == "true"  # 是否允许新用户注册
    MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "False").lower() == "true"  # 是否处于维护模式
    
    # 安全级别配置
    SECURITY_LEVELS = {
        1: "低",
        2: "中",
        3: "高"
    }
    
    # 默认系统状态
    DEFAULT_STATUS = {
        'maintenance_mode': ('false', '系统维护模式'),
        'registration_open': ('true', '允许新用户注册'),
        'max_login_attempts': ('5', '最大登录尝试次数'),
        'session_timeout': ('3600', '会话超时时间（秒）'),
        'security_alert_level': ('normal', '安全警报级别')
    }
    
    # 邮件配置（可选）
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


class DevelopmentConfig(Config):
    """开发环境配置 - 优化开发体验和调试能力"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # 显示SQL语句便于调试
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)  # 开发环境会话时间较长
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")  # 开发环境使用DEBUG级别日志
    
    # 开发环境可以临时关闭CSRF保护（生产环境必须开启）
    # WTF_CSRF_ENABLED = False  # 取消注释以临时禁用CSRF保护


class ProductionConfig(Config):
    """生产环境配置 - 优化性能和安全性"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() == "true"  # 仅HTTPS
    
    # 生产环境限流更严格
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "100 per day, 30 per hour")
    LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "5 per minute, 20 per hour")
    
    # 生产环境使用更高级别的日志
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")


class TestingConfig(Config):
    """测试环境配置 - 便于自动化测试"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False  # 测试环境关闭CSRF保护以方便测试
    
    # 使用内存数据库
    @staticmethod
    def get_database_url():
        return "sqlite:///:memory:"


# 配置映射字典，用于根据环境变量选择配置
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}