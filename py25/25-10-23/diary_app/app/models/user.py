"""用户相关模型 - 定义用户和安全相关的数据结构"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import validates
import re
from app.extensions import db

class User(UserMixin, db.Model):
    """用户模型 - 存储用户基本信息和身份验证数据"""
    __tablename__ = 'users'
    
    # 基本字段
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 状态字段
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # 用户是否激活
    is_admin = db.Column(db.Boolean, default=False, nullable=False)  # 是否为管理员
    
    # 时间戳字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)
    
    # 安全字段
    security_level = db.Column(db.Integer, default=1, nullable=False)  # 1-低, 2-中, 3-高
    login_attempts = db.Column(db.Integer, default=0, nullable=False)  # 连续登录失败次数
    account_locked = db.Column(db.Boolean, default=False, nullable=False)
    lockout_until = db.Column(db.DateTime, nullable=True)
    
    # 个人信息字段
    display_name = db.Column(db.String(100), nullable=True)  # 显示名称
    avatar_url = db.Column(db.String(255), nullable=True)  # 头像URL
    bio = db.Column(db.Text, nullable=True)  # 个人简介
    
    # 通知偏好
    email_notifications = db.Column(db.Boolean, default=True, nullable=False)
    
    # 关系
    diaries = db.relationship('DiaryEntry', back_populates='user', lazy=True, cascade="all, delete-orphan")
    login_activities = db.relationship('UserLoginAttempt', back_populates='user', lazy=True, cascade="all, delete-orphan")
    
    @validates('username')
    def validate_username(self, key, value):
        """验证用户名格式"""
        if not re.match(r'^[a-zA-Z0-9_]{3,50}$', value):
            raise ValueError('用户名必须是3-50个字符，只能包含字母、数字和下划线')
        return value
    
    @validates('email')
    def validate_email(self, key, value):
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValueError('邮箱格式不正确')
        return value
    
    def set_password(self, password: str):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
        self.last_password_change = datetime.utcnow()
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def increment_login_attempts(self):
        """增加登录失败次数"""
        self.login_attempts += 1
        
    def reset_login_attempts(self):
        """重置登录失败次数"""
        self.login_attempts = 0
        self.account_locked = False
        self.lockout_until = None
    
    def lock_account(self, duration_minutes: int):
        """锁定账户指定时长"""
        from datetime import timedelta
        self.account_locked = True
        self.lockout_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def is_locked(self) -> bool:
        """检查账户是否被锁定"""
        if not self.account_locked or not self.lockout_until:
            return False
        
        # 如果锁定时间已过，自动解锁
        if self.lockout_until < datetime.utcnow():
            self.reset_login_attempts()
            return False
        
        return True
    
    def update_last_activity(self):
        """更新最后活动时间"""
        self.last_activity = datetime.utcnow()
    
    def __repr__(self):
        return f'<User {self.username}>'


class SecurityProfile(db.Model):
    """用户安全配置模型 - 存储用户安全相关的额外设置"""
    __tablename__ = 'security_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # 账户安全状态
    failed_count = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    # 密码重置相关
    question = db.Column(db.String(255), nullable=True)
    answer_hash = db.Column(db.String(255), nullable=True)
    
    # 2FA相关
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_secret = db.Column(db.String(255), nullable=True)  # 加密存储
    recovery_codes = db.Column(db.Text, nullable=True)  # 加密存储的恢复码
    
    # 密码策略
    last_password_change = db.Column(db.DateTime, nullable=True)
    password_history = db.Column(db.Text, nullable=True)  # 存储最近使用的密码哈希，防止重复
    
    # 会话管理
    max_sessions = db.Column(db.Integer, default=5, nullable=False)
    require_password_change = db.Column(db.Boolean, default=False, nullable=False)
    
    # 关系
    user = db.relationship('User', backref=db.backref('security_profile', uselist=False, cascade="all, delete-orphan"))
    
    def set_security_answer(self, answer: str):
        """设置安全问题答案（加密存储）"""
        self.answer_hash = generate_password_hash(answer)
    
    def check_security_answer(self, answer: str) -> bool:
        """验证安全问题答案"""
        if not self.answer_hash:
            return False
        return check_password_hash(self.answer_hash, answer)
    
    def __repr__(self):
        return f'<SecurityProfile user_id={self.user_id}>'


class UserLoginAttempt(db.Model):
    """用户登录尝试模型 - 记录用户登录历史和安全审计"""
    __tablename__ = 'user_login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # nullable=True允许记录未知用户的登录尝试
    username_attempted = db.Column(db.String(50), nullable=True)  # 尝试登录的用户名
    
    # 关系
    user = db.relationship('User', back_populates='login_activities')
    
    # 登录信息
    ip_address = db.Column(db.String(50), nullable=False, index=True)
    user_agent = db.Column(db.String(255), nullable=True)
    success = db.Column(db.Boolean, nullable=False, index=True)
    
    # 时间戳
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 安全信息
    security_reason = db.Column(db.String(255), nullable=True)  # 失败或特殊处理的原因
    location = db.Column(db.String(100), nullable=True)  # IP地理位置（可选）
    
    def __repr__(self):
        status = "成功" if self.success else "失败"
        user_info = f"用户ID:{self.user_id}" if self.user_id else f"尝试用户名:{self.username_attempted}"
        return f'<UserLoginAttempt {status} {user_info} 时间:{self.attempted_at} IP:{self.ip_address}>'