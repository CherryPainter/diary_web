# diary_app/app/utils/logging.py
"""日志相关工具函数"""
from flask import request
from app.extensions import db
from app.models import SystemLog

def log_system_event(log_type, message, user_id=None, ip_address=None):
    """
    记录系统日志
    
    Args:
        log_type: 日志类型 ('info', 'warning', 'error', 'security', 'admin')
        message: 日志消息
        user_id: 用户ID（可选）
        ip_address: IP地址（可选）
    
    Returns:
        SystemLog: 创建的日志记录对象
    """
    # 如果未提供IP地址，尝试从请求中获取
    if ip_address is None and request:
        ip_address = request.remote_addr
    
    log = SystemLog(
        log_type=log_type,
        message=message,
        user_id=user_id,
        ip_address=ip_address
    )
    
    try:
        db.session.add(log)
        db.session.commit()
        return log
    except Exception as e:
        # 确保日志记录失败不会影响主业务流程
        db.session.rollback()
        print(f"Failed to log system event: {e}")
        return None

def get_user_activity_logs(user_id, limit=50):
    """
    获取用户活动记录
    
    Args:
        user_id: 用户ID
        limit: 返回的记录数量限制
    
    Returns:
        list: 用户活动日志列表
    """
    return SystemLog.query.filter_by(user_id=user_id)\
        .order_by(SystemLog.created_at.desc())\
        .limit(limit)\
        .all()

def get_system_logs(log_type=None, page=1, per_page=50):
    """
    获取系统日志，支持分页和类型筛选
    
    Args:
        log_type: 日志类型筛选（可选）
        page: 页码
        per_page: 每页记录数
    
    Returns:
        Pagination: 分页后的日志记录
    """
    query = SystemLog.query
    
    if log_type:
        query = query.filter_by(log_type=log_type)
    
    return query.order_by(SystemLog.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

def get_recent_system_logs(limit=20):
    """
    获取最近的系统日志
    
    Args:
        limit: 返回的记录数量限制
    
    Returns:
        list: 最近的系统日志列表
    """
    return SystemLog.query.order_by(SystemLog.created_at.desc()).limit(limit).all()