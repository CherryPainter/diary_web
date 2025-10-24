# diary_app/app/utils/data.py
"""数据相关工具函数"""
import json
from datetime import datetime
from app.models import DiaryEntry

def export_user_data(user):
    """
    导出用户数据
    
    Args:
        user: 用户对象
    
    Returns:
        dict: 用户数据字典
    """
    export_data = {
        'user_info': {
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'security_level': user.security_level
        },
        'diary_entries': []
    }
    
    # 添加所有日记条目
    entries = DiaryEntry.query.filter_by(user_id=user.id).all()
    for entry in entries:
        export_data['diary_entries'].append({
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'created_at': entry.created_at.isoformat(),
            'updated_at': entry.updated_at.isoformat()
        })
    
    return export_data

def generate_export_file(user):
    """
    生成导出文件内容
    
    Args:
        user: 用户对象
    
    Returns:
        tuple: (文件内容, 文件名, 文件类型)
    """
    export_data = export_user_data(user)
    
    # 生成JSON内容
    file_content = json.dumps(export_data, ensure_ascii=False, indent=2)
    
    # 生成文件名
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"diary_export_{user.username}_{timestamp}.json"
    
    # 文件类型
    content_type = "application/json"
    
    return file_content, filename, content_type

def calculate_user_statistics(user):
    """
    计算用户统计信息
    
    Args:
        user: 用户对象
    
    Returns:
        dict: 用户统计信息
    """
    # 总日记数
    total_entries = DiaryEntry.query.filter_by(user_id=user.id).count()
    
    # 最近的日记条目
    recent_entries = DiaryEntry.query.filter_by(user_id=user.id)\
        .order_by(DiaryEntry.created_at.desc())\
        .limit(5)\
        .all()
    
    # 按日期分组的日记统计
    entries = DiaryEntry.query.filter_by(user_id=user.id).all()
    today = datetime.utcnow().date()
    groups_map = {}
    
    for entry in entries:
        d = entry.created_at.date()
        if d == today:
            label = '今天'
        elif d == today - timedelta(days=1):
            label = '昨天'
        else:
            label = d.strftime('%Y-%m-%d')
        groups_map.setdefault(label, []).append(entry)
    
    # 按组里最新条目的时间降序排列分组
    sorted_groups = sorted(
        groups_map.items(),
        key=lambda kv: max(x.created_at for x in kv[1]),
        reverse=True
    )
    
    sidebar_groups = [{'label': k, 'items': v} for k, v in sorted_groups]
    
    return {
        'total_entries': total_entries,
        'recent_entries': recent_entries,
        'sidebar_groups': sidebar_groups
    }

# 为了避免循环导入，在函数内部导入
from datetime import timedelta