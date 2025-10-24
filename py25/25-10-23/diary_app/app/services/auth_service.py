# diary_app/app/services/auth_service.py
"""认证服务"""
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import User, SecurityProfile
from app.utils.logging import log_system_event
from app.utils.security import validate_password_complexity

class AuthService:
    """认证服务类"""
    
    def register_user(self, username, email, password):
        """
        用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
        
        Returns:
            tuple: (成功状态, 用户对象, 错误消息)
        """
        # 唯一性检查
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return False, None, "用户名或邮箱已存在"
        
        # 密码复杂度验证（基础级别）
        is_valid, error_msg = validate_password_complexity(password, 1)
        if not is_valid:
            return False, None, error_msg
        
        try:
            # 创建用户
            user = User(username=username.strip(), email=email.strip())
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # 获取用户ID
            
            # 创建安全配置
            security_profile = SecurityProfile(user_id=user.id, failed_count=0)
            db.session.add(security_profile)
            
            db.session.commit()
            log_system_event('info', f'新用户注册: {username}', user.id)
            
            return True, user, "注册成功"
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'用户注册失败: {str(e)}')
            return False, None, "注册失败，请稍后重试"
    
    def login_user(self, username, password, ip_address=None):
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            ip_address: IP地址
        
        Returns:
            tuple: (成功状态, 用户对象, 锁定标志, 安全问题, 错误消息)
        """
        # 查找用户
        user = User.query.filter_by(username=username.strip()).first()
        
        # 用户不存在
        if not user:
            return False, None, False, None, "用户名或密码错误"
        
        # 检查账户是否锁定
        if user.security_profile:
            if (user.security_profile.locked_until and user.security_profile.locked_until > datetime.utcnow()) or \
               user.security_profile.failed_count >= 3:
                return False, None, True, user.security_profile.question, "账户已锁定，请使用辅助验证解锁"
        
        # 密码验证
        if not user.check_password(password):
            # 记录失败次数
            if not user.security_profile:
                profile = SecurityProfile(user_id=user.id, failed_count=0)
                db.session.add(profile)
                user.security_profile = profile
            
            profile = user.security_profile
            profile.failed_count = (profile.failed_count or 0) + 1
            
            # 检查是否需要锁定
            if profile.failed_count >= 3:
                profile.locked_until = None  # 无限期锁定，需辅助验证解锁
                db.session.commit()
                log_system_event('warning', f'用户 {username} 账户被锁定', user.id, ip_address)
                return False, None, True, profile.question, "账户已锁定，请使用辅助验证解锁"
            
            db.session.commit()
            log_system_event('warning', f'用户 {username} 登录失败，密码错误', user.id, ip_address)
            return False, None, False, None, "用户名或密码错误"
        
        # 登录成功，重置失败记录
        if user.security_profile:
            user.security_profile.failed_count = 0
            user.security_profile.locked_until = None
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        log_system_event('info', f'用户 {username} 登录成功', user.id, ip_address)
        return True, user, False, None, "登录成功"
    
    def verify_security_answer(self, username, answer):
        """
        验证安全问题答案
        
        Args:
            username: 用户名
            answer: 安全问题答案
        
        Returns:
            tuple: (成功状态, 错误消息)
        """
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return False, "用户不存在"
        
        profile = user.security_profile
        if not profile or not profile.question or not profile.answer_hash:
            return False, "未设置辅助验证，无法解锁"
        
        # 验证答案
        from werkzeug.security import check_password_hash
        if not check_password_hash(profile.answer_hash, answer):
            return False, "辅助验证答案错误"
        
        # 解除锁定
        profile.failed_count = 0
        profile.locked_until = None
        db.session.commit()
        
        log_system_event('info', f'用户 {username} 通过辅助验证解锁账户', user.id)
        return True, "账户已解锁，请重新登录"