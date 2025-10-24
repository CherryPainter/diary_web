"""用户服务模块 - 处理用户相关的业务逻辑"""
from datetime import datetime, timedelta
from flask import current_app
from flask_login import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, SecurityProfile, UserLoginAttempt, SystemLog
from app.extensions import db
from app.utils.security import log_system_event


class UserService:
    """用户服务类 - 提供用户管理相关功能"""
    
    def create_user(self, username, email, password, security_level=1):
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            security_level: 安全等级
        
        Returns:
            User: 创建的用户对象
        
        Raises:
            ValueError: 如果用户名或邮箱已存在
        """
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            raise ValueError('用户名已存在')
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            raise ValueError('邮箱已被注册')
        
        # 验证密码复杂度
        if not self._validate_password_complexity(password):
            raise ValueError('密码不符合安全要求')
        
        # 创建用户
        user = User(
            username=username,
            email=email,
            security_level=security_level
        )
        user.set_password(password)
        
        # 创建安全配置
        security_profile = SecurityProfile(user_id=user.id)
        
        db.session.add(user)
        db.session.add(security_profile)
        db.session.commit()
        
        # 记录用户创建日志
        log_system_event('info', f'创建新用户: {username}', None)
        
        return user
    
    def authenticate_user(self, username, password):
        """
        验证用户身份
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            tuple: (用户对象, 错误消息)
        """
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        if not user:
            # 记录失败的登录尝试
            self._record_login_attempt(username, False)
            return None, "用户名或密码错误"
        
        # 检查账户是否锁定
        if user.account_locked:
            if user.lockout_until and user.lockout_until > datetime.utcnow():
                minutes_remaining = int((user.lockout_until - datetime.utcnow()).total_seconds() / 60)
                return None, f"账户已锁定，请在{minutes_remaining}分钟后再试"
            else:
                # 锁定时间已过，解锁账户
                user.account_locked = False
                user.login_attempts = 0
                user.lockout_until = None
                db.session.commit()
        
        # 验证密码
        if not check_password_hash(user.password_hash, password):
            # 增加失败尝试次数
            user.login_attempts += 1
            
            # 记录失败的登录尝试
            self._record_login_attempt(username, False)
            
            # 检查是否需要锁定账户
            max_attempts = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
            lockout_minutes = current_app.config.get('ACCOUNT_LOCKOUT_MINUTES', 30)
            
            if user.login_attempts >= max_attempts:
                user.account_locked = True
                user.lockout_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)
                db.session.commit()
                log_system_event('security', f'用户账户锁定: {username}', user.id)
                return None, f"登录失败次数过多，账户已锁定{lockout_minutes}分钟"
            
            db.session.commit()
            return None, "用户名或密码错误"
        
        # 登录成功，重置失败尝试次数
        user.login_attempts = 0
        user.last_login = datetime.utcnow()
        user.last_activity = datetime.utcnow()
        db.session.commit()
        
        # 记录成功的登录尝试
        self._record_login_attempt(username, True)
        log_system_event('info', f'用户登录成功: {username}', user.id)
        
        return user, None
    
    def _record_login_attempt(self, username, success):
        """
        记录登录尝试
        
        Args:
            username: 尝试登录的用户名
            success: 是否登录成功
        """
        attempt = UserLoginAttempt(
            username=username,
            success=success,
            attempted_at=datetime.utcnow()
        )
        db.session.add(attempt)
        db.session.commit()
    
    def get_user_by_id(self, user_id):
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            User: 用户对象
        """
        return User.query.get(user_id)
    
    def get_user_by_username(self, username):
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
        
        Returns:
            User: 用户对象
        """
        return User.query.filter_by(username=username).first()
    
    def get_user_by_email(self, email):
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
        
        Returns:
            User: 用户对象
        """
        return User.query.filter_by(email=email).first()
    
    def update_password(self, user, old_password, new_password):
        """
        更新用户密码
        
        Args:
            user: 用户对象
            old_password: 旧密码
            new_password: 新密码
        
        Returns:
            tuple: (成功状态, 错误消息)
        """
        # 验证旧密码
        if not check_password_hash(user.password_hash, old_password):
            return False, "旧密码错误"
        
        # 检查密码长度
        if len(new_password) < 8:
            return False, "新密码长度至少8位"
        
        # 验证密码复杂度
        if not self._validate_password_complexity(new_password):
            return False, "新密码不符合安全要求"
        
        # 避免密码重复
        if check_password_hash(user.password_hash, new_password):
            return False, "新密码不能与旧密码相同"
        
        # 确保安全配置存在
        if not user.security_profile:
            profile = SecurityProfile(user_id=user.id)
            db.session.add(profile)
            user.security_profile = profile
        
        # 更新密码
        old_password_hash = user.password_hash
        user.set_password(new_password)
        user.password_changed_at = datetime.utcnow()
        
        # 更新安全信息
        profile = user.security_profile
        profile.last_password_change = datetime.utcnow()
        
        # 保存密码历史（最近5个）
        if not profile.password_history:
            profile.password_history = []
        
        profile.password_history.insert(0, {
            'password_hash': old_password_hash,
            'changed_at': datetime.utcnow().isoformat()
        })
        
        # 只保留最近5次密码记录
        if len(profile.password_history) > 5:
            profile.password_history = profile.password_history[:5]
        
        try:
            db.session.commit()
            log_system_event('security', f'用户 {user.username} 修改了密码', user.id)
            return True, "密码已更新"
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'用户 {user.username} 修改密码失败: {str(e)}', user.id)
            return False, "密码更新失败，请稍后重试"
    
    def update_security_settings(self, user, question, answer, two_factor_enabled=False):
        """
        更新用户安全设置
        
        Args:
            user: 用户对象
            question: 安全问题
            answer: 安全问题答案
            two_factor_enabled: 是否启用双因素认证
        
        Returns:
            tuple: (成功状态, 错误消息)
        """
        if not question or not answer:
            return False, "请填写问题和答案"
        
        # 确保安全配置存在
        if not user.security_profile:
            profile = SecurityProfile(user_id=user.id)
            db.session.add(profile)
            user.security_profile = profile
        
        # 更新安全信息
        profile = user.security_profile
        profile.question = question
        profile.answer_hash = generate_password_hash(answer)
        profile.two_factor_enabled = two_factor_enabled
        
        try:
            db.session.commit()
            log_system_event('security', f'用户 {user.username} 更新了安全设置', user.id)
            return True, "辅助验证已保存"
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'用户 {user.username} 更新安全设置失败: {str(e)}', user.id)
            return False, "保存失败，请稍后重试"
    
    def update_security_level(self, user, security_level):
        """
        更新用户安全等级
        
        Args:
            user: 用户对象
            security_level: 安全等级 (1-3)
        
        Returns:
            tuple: (成功状态, 错误消息)
        """
        if security_level not in [1, 2, 3]:
            return False, "无效的安全等级"
        
        user.security_level = security_level
        
        try:
            db.session.commit()
            log_system_event('info', f'更新用户安全等级: {user.username} 到 {security_level}', user.id)
            return True, "安全等级已更新"
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'更新用户安全等级失败: {str(e)}', user.id)
            return False, "更新失败，请稍后重试"
    
    def reset_password(self, user_id, new_password):
        """
        重置用户密码（管理员功能）
        
        Args:
            user_id: 用户ID
            new_password: 新密码
        
        Returns:
            bool: 是否成功
        
        Raises:
            ValueError: 如果用户不存在或密码不符合要求
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')
        
        # 验证新密码复杂度
        if not self._validate_password_complexity(new_password):
            raise ValueError('新密码不符合安全要求')
        
        # 更新密码
        user.set_password(new_password)
        user.password_changed_at = datetime.utcnow()
        user.account_locked = False
        user.login_attempts = 0
        user.lockout_until = None
        
        db.session.commit()
        
        # 记录密码重置日志
        current_user = login_manager.current_user if login_manager.current_user.is_authenticated else None
        SystemLog.log(
            'security',
            f'用户密码已重置: {user.username} (ID: {user.id})',
            user=current_user,
            severity=1
        )
        
        return True
    
    def deactivate_user(self, user_id):
        """
        停用用户账号
        
        Args:
            user_id: 用户ID
        
        Returns:
            bool: 是否成功
        
        Raises:
            ValueError: 如果用户不存在或不能停用
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')
        
        # 不允许停用管理员账户
        if user.is_admin:
            raise ValueError('不能停用管理员账户')
        
        user.is_active = False
        db.session.commit()
        
        # 记录停用日志
        current_user = login_manager.current_user if login_manager.current_user.is_authenticated else None
        SystemLog.log(
            'security',
            f'用户账户已停用: {user.username} (ID: {user.id})',
            user=current_user,
            severity=1
        )
        
        return True
    
    def reactivate_user(self, user_id):
        """
        重新激活用户账号
        
        Args:
            user_id: 用户ID
        
        Returns:
            bool: 是否成功
        
        Raises:
            ValueError: 如果用户不存在
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')
        
        user.is_active = True
        user.account_locked = False
        user.login_attempts = 0
        user.lockout_until = None
        db.session.commit()
        
        # 记录激活日志
        current_user = login_manager.current_user if login_manager.current_user.is_authenticated else None
        SystemLog.log(
            'info',
            f'用户账户已重新激活: {user.username} (ID: {user.id})',
            user=current_user
        )
        
        return True
    
    def get_user_stats(self, user_id):
        """
        获取用户统计信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            dict: 统计信息
        
        Raises:
            ValueError: 如果用户不存在
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')
        
        # 获取日记统计
        from app.models.diary import DiaryEntry
        total_diaries = DiaryEntry.query.filter_by(user_id=user_id, is_deleted=False).count()
        
        # 获取最近7天的日记数
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_diaries = DiaryEntry.query.filter(
            DiaryEntry.user_id == user_id,
            DiaryEntry.is_deleted == False,
            DiaryEntry.created_at >= seven_days_ago
        ).count()
        
        # 获取登录尝试统计
        login_attempts = UserLoginAttempt.query.filter_by(user_id=user_id).order_by(
            UserLoginAttempt.attempted_at.desc()
        ).limit(5).all()
        
        return {
            'total_diaries': total_diaries,
            'recent_diaries': recent_diaries,
            'last_login': user.last_login,
            'account_status': '正常' if user.is_active and not user.account_locked else '异常',
            'login_attempts': login_attempts
        }
    
    def update_user_activity(self, user):
        """
        更新用户活动时间
        
        Args:
            user: 用户对象
        """
        if user.is_authenticated:
            user.last_activity = datetime.utcnow()
            db.session.commit()
    
    def _validate_password_complexity(self, password):
        """
        验证密码复杂度
        
        Args:
            password: 密码
        
        Returns:
            bool: 是否符合要求
        """
        # 基本长度检查
        if len(password) < 8:
            return False
        
        # 检查是否包含字母和数字
        has_alpha = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        # 如果配置了更严格的密码策略
        require_complexity = current_app.config.get('PASSWORD_COMPLEXITY_REQUIRED', True)
        if require_complexity:
            # 还需要包含特殊字符
            has_special = any(not c.isalnum() for c in password)
            return has_alpha and has_digit and has_special
        
        return has_alpha and has_digit
    
    def _encrypt_security_answer(self, answer):
        """
        加密安全问题答案
        
        Args:
            answer: 安全问题答案
        
        Returns:
            str: 加密后的答案
        """
        # 简单的哈希处理，实际应用中可以使用更强的加密方式
        return generate_password_hash(answer.lower().strip())


# 创建全局用户服务实例
user_service = UserService()