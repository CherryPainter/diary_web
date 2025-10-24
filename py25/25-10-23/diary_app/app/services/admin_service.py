# diary_app/app/services/admin_service.py
"""管理员服务"""
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import User, SecurityProfile, SystemStatus
from app.utils.logging import log_system_event

class AdminService:
    """管理员服务类"""
    
    def get_all_users(self, page=1, per_page=20):
        """
        获取所有用户
        
        Args:
            page: 页码
            per_page: 每页记录数
        
        Returns:
            Pagination: 分页对象
        """
        return User.query.order_by(User.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    def get_user_by_id(self, user_id):
        """
        根据ID获取用户（管理员专用）
        
        Args:
            user_id: 用户ID
        
        Returns:
            User: 用户对象或None
        """
        return User.query.get(user_id)
    
    def update_user_role(self, user_id, is_admin):
        """
        更新用户角色
        
        Args:
            user_id: 用户ID
            is_admin: 是否为管理员
        
        Returns:
            tuple: (成功状态, 错误消息)
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        # 不允许取消最后一个管理员
        if not is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1 and user.is_admin:
                return False, "不能取消最后一个管理员的权限"
        
        try:
            user.is_admin = is_admin
            db.session.commit()
            role = "管理员" if is_admin else "普通用户"
            log_system_event('admin', f'用户 {user.username} 角色更新为 {role}', None)
            return True, "用户角色已更新"
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'更新用户角色失败: {str(e)}', None)
            return False, "更新失败，请稍后重试"
    
    def update_user_security_level(self, user_id, security_level):
        """
        更新用户安全等级
        
        Args:
            user_id: 用户ID
            security_level: 安全等级 (1-3)
        
        Returns:
            tuple: (成功状态, 错误消息)
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        if security_level not in [1, 2, 3]:
            return False, "无效的安全等级"
        
        try:
            user.security_level = security_level
            db.session.commit()
            log_system_event('admin', f'用户 {user.username} 安全等级更新为 {security_level}', None)
            return True, "安全等级已更新"
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'更新用户安全等级失败: {str(e)}', None)
            return False, "更新失败，请稍后重试"
    
    def reset_user_password(self, user_id, new_password):
        """
        重置用户密码
        
        Args:
            user_id: 用户ID
            new_password: 新密码
        
        Returns:
            tuple: (成功状态, 错误消息)
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        # 密码长度检查
        if len(new_password) < 8:
            return False, "密码长度至少8位"
        
        try:
            # 重置密码
            user.set_password(new_password)
            
            # 重置失败次数
            if user.security_profile:
                user.security_profile.failed_count = 0
                user.security_profile.locked_until = None
            
            db.session.commit()
            log_system_event('admin', f'用户 {user.username} 密码已重置', None)
            return True, "密码已重置"
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'重置用户密码失败: {str(e)}', None)
            return False, "重置失败，请稍后重试"
    
    def delete_user(self, user_id, current_admin_id):
        """
        删除用户
        
        Args:
            user_id: 用户ID
            current_admin_id: 当前管理员ID
        
        Returns:
            tuple: (成功状态, 错误消息)
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "用户不存在"
        
        # 不允许删除自己
        if user.id == current_admin_id:
            return False, "不能删除自己的账户"
        
        # 不允许删除最后一个管理员
        if user.is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                return False, "不能删除最后一个管理员"
        
        username = user.username
        
        try:
            # 删除用户（会级联删除关联数据）
            db.session.delete(user)
            db.session.commit()
            log_system_event('admin', f'管理员删除了用户: {username}', current_admin_id)
            return True, "用户已删除"
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'删除用户失败: {username}, {str(e)}', current_admin_id)
            return False, "删除失败，请稍后重试"
    
    def update_system_settings(self, settings, admin_id):
        """
        更新系统设置
        
        Args:
            settings: 设置字典
            admin_id: 管理员ID
        
        Returns:
            tuple: (成功状态, 错误消息)
        """
        try:
            for key, value in settings.items():
                # 更新系统状态
                status = SystemStatus.query.filter_by(status_key=key).first()
                if status:
                    status.status_value = str(value)
                else:
                    # 获取描述
                    description = ""
                    if key == 'maintenance_mode':
                        description = '系统维护模式'
                    elif key == 'registration_open':
                        description = '允许新用户注册'
                    elif key == 'max_login_attempts':
                        description = '最大登录尝试次数'
                    elif key == 'session_timeout':
                        description = '会话超时时间（秒）'
                    elif key == 'security_alert_level':
                        description = '安全警报级别'
                    
                    status = SystemStatus(
                        status_key=key,
                        status_value=str(value),
                        description=description
                    )
                    db.session.add(status)
            
            db.session.commit()
            log_system_event('admin', f'系统设置已更新', admin_id)
            return True, "系统设置已更新"
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'更新系统设置失败: {str(e)}', admin_id)
            return False, "更新失败，请稍后重试"
    
    def create_admin_user(self, username, email, password):
        """
        创建管理员用户（用于初始化或紧急情况）
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
        
        Returns:
            tuple: (成功状态, 用户对象, 错误消息)
        """
        # 检查用户名和邮箱是否已存在
        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing:
            return False, None, "用户名或邮箱已存在"
        
        try:
            # 创建管理员用户
            user = User(
                username=username,
                email=email,
                is_admin=True,
                security_level=3  # 管理员默认为高安全级别
            )
            user.set_password(password)
            
            # 创建安全配置
            profile = SecurityProfile(user_id=user.id, failed_count=0)
            db.session.add(user)
            db.session.add(profile)
            
            db.session.commit()
            log_system_event('admin', f'创建了管理员用户: {username}', None)
            return True, user, "管理员用户已创建"
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'创建管理员用户失败: {str(e)}', None)
            return False, None, "创建失败，请稍后重试"