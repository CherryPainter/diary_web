# diary_app/app/services/system_service.py
"""系统服务"""
from datetime import datetime
from app.extensions import db
from app.models import SystemStatus, SystemLog
from app.utils.logging import log_system_event
from app.config import Config

class SystemService:
    """系统服务类"""
    
    def initialize_system_status(self):
        """
        初始化系统状态配置
        """
        # 检查是否已初始化
        if SystemStatus.query.first():
            return
        
        try:
            # 设置默认系统状态
            for key, (value, description) in Config.DEFAULT_STATUS.items():
                status = SystemStatus(
                    status_key=key,
                    status_value=value,
                    description=description
                )
                db.session.add(status)
            
            db.session.commit()
            log_system_event('info', '系统状态已初始化')
        except Exception as e:
            db.session.rollback()
            print(f"Failed to initialize system status: {e}")
    
    def get_system_status(self, key=None):
        """
        获取系统状态
        
        Args:
            key: 状态键名（可选）
        
        Returns:
            单个状态值或所有状态的字典
        """
        if key:
            status = SystemStatus.query.filter_by(status_key=key).first()
            return status.status_value if status else None
        
        # 获取所有状态
        status_dict = {}
        for status in SystemStatus.query.all():
            status_dict[status.status_key] = status.status_value
        return status_dict
    
    def update_system_status(self, key, value, description=None):
        """
        更新系统状态
        
        Args:
            key: 状态键名
            value: 状态值
            description: 状态描述（可选）
        
        Returns:
            bool: 是否成功
        """
        try:
            status = SystemStatus.query.filter_by(status_key=key).first()
            if status:
                status.status_value = value
                if description:
                    status.description = description
            else:
                status = SystemStatus(
                    status_key=key,
                    status_value=value,
                    description=description
                )
                db.session.add(status)
            
            db.session.commit()
            log_system_event('info', f'系统状态更新: {key} = {value}')
            return True
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'系统状态更新失败: {key}, {str(e)}')
            return False
    
    def is_maintenance_mode(self):
        """
        检查系统是否处于维护模式
        
        Returns:
            bool: 是否处于维护模式
        """
        return self.get_system_status('maintenance_mode') == 'true'
    
    def is_registration_open(self):
        """
        检查是否允许新用户注册
        
        Returns:
            bool: 是否允许注册
        """
        return self.get_system_status('registration_open') == 'true'
    
    def get_max_login_attempts(self):
        """
        获取最大登录尝试次数
        
        Returns:
            int: 最大登录尝试次数
        """
        value = self.get_system_status('max_login_attempts')
        return int(value) if value else 5
    
    def get_session_timeout(self):
        """
        获取会话超时时间（秒）
        
        Returns:
            int: 会话超时时间
        """
        value = self.get_system_status('session_timeout')
        return int(value) if value else 3600
    
    def get_security_alert_level(self):
        """
        获取安全警报级别
        
        Returns:
            str: 安全警报级别
        """
        return self.get_system_status('security_alert_level') or 'normal'
    
    def update_maintenance_mode(self, is_maintenance):
        """
        更新维护模式
        
        Args:
            is_maintenance: 是否启用维护模式
        
        Returns:
            bool: 是否成功
        """
        return self.update_system_status(
            'maintenance_mode', 
            'true' if is_maintenance else 'false',
            '系统维护模式'
        )
    
    def update_registration_status(self, is_open):
        """
        更新注册状态
        
        Args:
            is_open: 是否允许注册
        
        Returns:
            bool: 是否成功
        """
        return self.update_system_status(
            'registration_open', 
            'true' if is_open else 'false',
            '允许新用户注册'
        )
    
    def get_system_statistics(self):
        """
        获取系统统计信息
        
        Returns:
            dict: 系统统计信息
        """
        from app.models import User, DiaryEntry
        
        # 用户统计
        total_users = User.query.count()
        admin_users = User.query.filter_by(is_admin=True).count()
        
        # 日记统计
        total_diaries = DiaryEntry.query.count()
        
        # 最近的系统日志
        recent_logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(10).all()
        
        # 今日活跃用户
        today = datetime.utcnow().date()
        active_today = User.query.filter(
            User.last_login >= datetime.combine(today, datetime.min.time())
        ).count()
        
        return {
            'total_users': total_users,
            'admin_users': admin_users,
            'total_diaries': total_diaries,
            'active_today': active_today,
            'recent_logs': recent_logs,
            'maintenance_mode': self.is_maintenance_mode(),
            'registration_open': self.is_registration_open(),
            'security_alert_level': self.get_security_alert_level()
        }
    
    def init_default_data(self):
        """
        初始化系统默认数据
        
        包括默认系统状态、初始管理员账户等
        """
        try:
            # 初始化系统状态
            self.initialize_system_status()
            
            # 创建默认管理员账户（如果不存在）
            from app.models import User
            from werkzeug.security import generate_password_hash
            
            # 检查是否已有管理员
            if not User.query.filter_by(is_admin=True).first():
                # 创建默认管理员
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True,
                    security_level=3,
                    is_active=True
                )
                # 使用set_password方法设置密码
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                log_system_event('info', '默认管理员账户已创建')
            
            log_system_event('info', '系统默认数据初始化完成')
            return True
        except Exception as e:
            db.session.rollback()
            log_system_event('error', f'系统默认数据初始化失败: {str(e)}')
            print(f"Failed to initialize default data: {e}")
            return False

# 创建全局系统服务实例
system_service = SystemService()

# 导出init_default_data函数供其他模块使用
def init_default_data():
    """初始化系统默认数据的便捷函数"""
    return system_service.init_default_data()