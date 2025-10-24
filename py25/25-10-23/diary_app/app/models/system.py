"""系统相关模型 - 定义系统配置、状态和日志的数据结构"""
from datetime import datetime
from sqlalchemy.orm import validates
from app.extensions import db

class SystemConfig(db.Model):
    """系统配置模型 - 存储系统级别的配置项"""
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text, nullable=False)
    config_type = db.Column(db.String(20), nullable=False, default='string')  # string, int, float, boolean, json
    description = db.Column(db.Text, nullable=True)
    is_editable = db.Column(db.Boolean, default=True, nullable=False)  # 是否可通过管理界面编辑
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @validates('config_key')
    def validate_config_key(self, key, value):
        """验证配置键名"""
        if not value or len(value.strip()) == 0:
            raise ValueError('配置键名不能为空')
        if not value.replace('_', '').isalnum():
            raise ValueError('配置键名只能包含字母、数字和下划线')
        return value.strip()
    
    def get_value(self):
        """根据配置类型获取转换后的值"""
        if self.config_type == 'int':
            return int(self.config_value)
        elif self.config_type == 'float':
            return float(self.config_value)
        elif self.config_type == 'boolean':
            return self.config_value.lower() in ('true', '1', 'yes', 'y')
        elif self.config_type == 'json':
            import json
            return json.loads(self.config_value)
        else:
            return self.config_value
    
    def set_value(self, value):
        """根据配置类型设置值"""
        if self.config_type == 'boolean':
            self.config_value = 'true' if value else 'false'
        elif self.config_type == 'json':
            import json
            self.config_value = json.dumps(value, ensure_ascii=False)
        else:
            self.config_value = str(value)
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}={self.config_value}>'


class SystemStatus(db.Model):
    """系统状态模型 - 存储系统运行状态信息"""
    __tablename__ = 'system_status'
    
    id = db.Column(db.Integer, primary_key=True)
    status_key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status_value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_maintenance = db.Column(db.Boolean, default=False, nullable=False)  # 是否处于维护模式
    maintenance_end = db.Column(db.DateTime, nullable=True)  # 维护结束时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 更新者
    
    # 关系
    updater = db.relationship('User')
    
    @classmethod
    def get_maintenance_status(cls):
        """获取系统维护状态"""
        maintenance = cls.query.filter_by(status_key='maintenance_mode').first()
        if maintenance and maintenance.is_maintenance:
            # 检查维护是否已结束
            if maintenance.maintenance_end and maintenance.maintenance_end < datetime.utcnow():
                maintenance.is_maintenance = False
                db.session.commit()
                return False
            return True
        return False
    
    def __repr__(self):
        return f'<SystemStatus {self.status_key}={self.status_value}>'


class SystemLog(db.Model):
    """系统日志模型 - 记录系统操作和事件日志"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(50), nullable=False, index=True)  # 'info', 'warning', 'error', 'security', 'audit'
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # 操作用户
    username = db.Column(db.String(50), nullable=True)  # 当用户不存在时记录用户名
    ip_address = db.Column(db.String(50), nullable=True, index=True)
    user_agent = db.Column(db.String(255), nullable=True)
    request_path = db.Column(db.String(255), nullable=True)  # 请求路径
    request_method = db.Column(db.String(10), nullable=True)  # 请求方法
    severity = db.Column(db.Integer, default=0, nullable=False, index=True)  # 严重程度 0-低, 1-中, 2-高
    details = db.Column(db.Text, nullable=True)  # 详细信息（JSON格式）
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 关系
    user = db.relationship('User', backref='logs')
    
    @validates('log_type')
    def validate_log_type(self, key, value):
        """验证日志类型"""
        valid_types = ['info', 'warning', 'error', 'security', 'audit']
        if value not in valid_types:
            raise ValueError(f'无效的日志类型，必须是以下之一: {valid_types}')
        return value
    
    @classmethod
    def log(cls, log_type, message, user=None, ip_address=None, **kwargs):
        """创建日志记录的便捷方法"""
        log_entry = cls(
            log_type=log_type,
            message=message,
            user_id=user.id if user else None,
            username=user.username if user else kwargs.get('username'),
            ip_address=ip_address,
            user_agent=kwargs.get('user_agent'),
            request_path=kwargs.get('request_path'),
            request_method=kwargs.get('request_method'),
            severity=kwargs.get('severity', 0),
            details=kwargs.get('details')
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    def __repr__(self):
        message_preview = self.message[:30] + '...' if len(self.message) > 30 else self.message
        return f'<SystemLog {self.log_type}: {message_preview}>'


class BackupRecord(db.Model):
    """备份记录模型 - 记录系统备份信息"""
    __tablename__ = 'backup_records'
    
    id = db.Column(db.Integer, primary_key=True)
    backup_type = db.Column(db.String(50), nullable=False)  # 'database', 'files', 'full'
    backup_file = db.Column(db.String(255), nullable=False)  # 备份文件路径
    file_size = db.Column(db.Integer, nullable=False)  # 文件大小（字节）
    status = db.Column(db.String(20), nullable=False, default='completed')  # 'pending', 'running', 'completed', 'failed'
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 创建者
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)  # 完成时间
    note = db.Column(db.Text, nullable=True)  # 备注信息
    
    # 关系
    creator = db.relationship('User')
    
    @property
    def file_size_human(self):
        """返回人类可读的文件大小"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def __repr__(self):
        return f'<BackupRecord {self.backup_type} {self.status} {self.created_at}>'