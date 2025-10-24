"""主页面相关路由"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.services.diary_service import get_system_statistics, get_recent_system_activity

# 创建蓝图
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """主页 - 根据登录状态重定向到合适的页面"""
    if current_user.is_authenticated:
        # 已登录用户重定向到日记列表
        return redirect(url_for('diary.diary_list'))
    # 未登录用户重定向到登录页面
    return redirect(url_for('auth.login'))


@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')


@main_bp.route('/stats')
def stats():
    """系统统计页面 - 仅对管理员可见"""
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('main.index'))
    
    # 获取系统统计信息
    stats = get_system_statistics()
    stats['recent_activity'] = get_recent_system_activity(days=7)
    
    return render_template('stats.html', stats=stats)