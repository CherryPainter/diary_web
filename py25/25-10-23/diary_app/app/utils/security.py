"""安全工具模块 - 提供密码验证、令牌生成等安全功能"""
import re
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from flask import current_app, request, session, g
from app.models.system import SystemLog, SystemStatus
from app.models.user import User
from app.extensions import db

# 模拟的令牌存储（实际应用中应使用Redis或数据库）
token_storage = {}


def generate_security_token(user_id, expiration=3600):
    """
    生成安全令牌
    
    Args:
        user_id: 用户ID
        expiration: 令牌过期时间（秒）
    
    Returns:
        str: 生成的安全令牌
    """
    token = secrets.token_urlsafe(32)
    # 存储令牌和过期时间
    token_storage[token] = {
        'user_id': user_id,
        'expires_at': time.time() + expiration
    }
    return token


def verify_security_token(user_id, token):
    """
    验证安全令牌
    
    Args:
        user_id: 用户ID
        token: 要验证的令牌
    
    Returns:
        bool: 令牌是否有效
    """
    if not token or token not in token_storage:
        return False
    
    token_info = token_storage[token]
    # 检查用户ID和令牌是否过期
    if token_info['user_id'] != user_id or token_info['expires_at'] < time.time():
        # 清理过期令牌
        if token_info['expires_at'] < time.time():
            del token_storage[token]
        return False
    
    return True


def generate_secure_token(length=32):
    """生成安全的随机令牌
    
    Args:
        length: 令牌长度
    
    Returns:
        生成的随机令牌
    """
    return secrets.token_urlsafe(length)


def generate_recovery_code():
    """生成恢复码
    
    Returns:
        生成的恢复码
    """
    return secrets.token_hex(4).upper()


def generate_recovery_codes():
    """
    生成恢复码
    
    Returns:
        list: 恢复码列表
    """
    # 生成10个恢复码
    codes = [secrets.token_hex(4).upper() for _ in range(10)]
    return codes


def set_csp_nonce():
    """设置CSP nonce"""
    g.csp_nonce = secrets.token_urlsafe(16)


def validate_password_complexity(password, security_level):
    """
    验证密码复杂度
    
    Args:
        password: 密码
        security_level: 安全等级
    
    Returns:
        tuple: (是否有效, 错误消息)
    """
    # 基本长度检查
    if len(password) < 8:
        return False, "密码长度至少8位"
    
    # 中安全等级要求
    if security_level >= 2:
        if not (any(c.isupper() for c in password) and 
                any(c.islower() for c in password) and 
                any(c.isdigit() for c in password)):
            return False, "密码必须包含大小写字母和数字"
    
    # 高安全等级额外要求
    if security_level >= 3:
        special_chars = '!@#$%^&*(),.?"\'{}[]|<>/'
        if not any(c in special_chars for c in password):
            return False, "密码必须包含特殊字符"
    
    return True, ""


def hash_password(password):
    """哈希密码（简单实现，实际应使用更安全的方法如bcrypt）
    
    Args:
        password: 原始密码
    
    Returns:
        密码哈希值
    """
    # 注意：在生产环境中应使用更安全的密码哈希算法，如bcrypt、Argon2等
    # 这里仅作为示例实现
    salt = secrets.token_hex(8)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(stored_hash, provided_password):
    """验证密码
    
    Args:
        stored_hash: 存储的密码哈希值
        provided_password: 用户提供的密码
    
    Returns:
        密码是否匹配
    """
    # 注意：这是与上面简单哈希实现对应的验证方法
    # 在生产环境中应使用与哈希方法对应的安全验证方法
    try:
        salt, stored_password = stored_hash.split(':', 1)
        hashed = hashlib.sha256((provided_password + salt).encode()).hexdigest()
        return hashed == stored_password
    except (ValueError, TypeError):
        return False


def check_password_strength(password, security_level=2):
    """检查密码强度
    
    Args:
        password: 要检查的密码
        security_level: 安全等级（1=低，2=中，3=高）
    
    Returns:
        (是否通过检查, 错误消息)
    """
    if not password:
        return False, "密码不能为空"
    
    # 低安全等级要求
    if len(password) < 8:
        return False, "密码长度至少8位"
    
    # 中安全等级要求
    if security_level >= 2:
        if not (any(c.isupper() for c in password) and 
                any(c.islower() for c in password) and 
                any(c.isdigit() for c in password)):
            return False, "密码必须包含大小写字母和数字"
    
    # 高安全等级额外要求
    if security_level >= 3:
        special_chars = '!@#$%^&*(),.?"\'{}[]|<>/'
        if not any(c in special_chars for c in password):
            return False, "密码必须包含特殊字符"
    
    return True, ""


def is_safe_redirect_url(url):
    """检查重定向URL是否安全
    
    Args:
        url: 要检查的URL
    
    Returns:
        URL是否安全
    """
    from urllib.parse import urlparse, urljoin
    
    if not url:
        return False
    
    # 解析URL
    netloc = urlparse(url).netloc
    
    # 确保重定向URL属于当前应用域名
    if netloc and netloc != request.host:
        return False
    
    return True


def sanitize_html(text):
    """简单的HTML内容清理（防止XSS攻击）
    
    Args:
        text: 要清理的文本
    
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 简单实现，移除危险标签和属性
    # 在生产环境中应使用专用的HTML清理库，如bleach
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input']
    dangerous_attrs = ['onerror', 'onload', 'onclick', 'onmouseover', 'javascript:']
    
    # 转换为小写进行匹配
    text_lower = text.lower()
    
    # 移除危险标签
    for tag in dangerous_tags:
        open_tag = f'<{tag}'
        close_tag = f'</{tag}>'
        if open_tag in text_lower:
            # 简单移除标签内容，实际应使用HTML解析器
            start_idx = text_lower.find(open_tag)
            end_idx = text_lower.find(close_tag, start_idx)
            if end_idx != -1:
                end_idx += len(close_tag)
                text = text[:start_idx] + '[内容已过滤]' + text[end_idx:]
                text_lower = text.lower()
    
    # 移除危险属性
    for attr in dangerous_attrs:
        if attr in text_lower:
            # 简单移除包含危险属性的部分
            parts = text.split(attr)
            text = '[属性已过滤]'.join(parts)
            text_lower = text.lower()
    
    return text


def log_system_event(event_type, message, user_id=None, ip_address=None):
    """记录系统事件
    
    Args:
        event_type: 事件类型（info, warning, error, audit）
        message: 事件消息
        user_id: 用户ID（可选）
        ip_address: IP地址（可选）
    """
    # 如果没有提供IP地址，从请求中获取
    if not ip_address and request:
        ip_address = request.remote_addr
    
    # 创建系统日志
    log = SystemLog(
        event_type=event_type,
        message=message,
        user_id=user_id,
        ip_address=ip_address
    )
    
    try:
        db.session.add(log)
        db.session.commit()
        return True
    except Exception as e:
        # 如果日志记录失败，打印错误但不影响主流程
        if current_app:
            current_app.logger.error(f"Failed to log system event: {str(e)}")
        return False


def check_rate_limit(limit_type, key, limit=100, period=3600):
    """简单的速率限制检查（基于内存，生产环境应使用Redis等）
    
    Args:
        limit_type: 限制类型（如login_attempt, api_request等）
        key: 限制键（如用户ID或IP地址）
        limit: 时间周期内的最大限制数
        period: 时间周期（秒）
    
    Returns:
        (是否在限制内, 剩余尝试次数)
    """
    # 注意：这是一个简单的基于内存的实现
    # 在生产环境中应使用Redis或其他持久化存储
    
    # 使用session存储尝试计数（简单实现）
    session_key = f"rate_limit:{limit_type}:{key}"
    current_time = datetime.utcnow()
    
    if session_key not in session:
        session[session_key] = {
            'count': 1,
            'reset_time': current_time + timedelta(seconds=period)
        }
        return True, limit - 1
    
    # 检查是否需要重置计数
    limit_data = session[session_key]
    if current_time > limit_data['reset_time']:
        limit_data['count'] = 1
        limit_data['reset_time'] = current_time + timedelta(seconds=period)
        session[session_key] = limit_data
        return True, limit - 1
    
    # 检查是否超过限制
    if limit_data['count'] >= limit:
        return False, 0
    
    # 更新计数
    limit_data['count'] += 1
    session[session_key] = limit_data
    return True, limit - limit_data['count']


def check_security_requirements(user, operation):
    """检查用户是否满足特定操作的安全要求
    
    Args:
        user: 用户对象
        operation: 操作名称（如login, edit_profile, delete_account等）
    
    Returns:
        是否满足安全要求
    """
    # 检查是否启用了两步验证
    if user.two_factor_enabled:
        # 对于敏感操作，确保两步验证已通过
        if operation in ['delete_account', 'change_password', 'edit_profile']:
            if not session.get('two_factor_verified'):
                return False
    
    # 检查是否为高风险操作，可能需要额外验证
    high_risk_operations = ['delete_account', 'change_email', 'disable_two_factor']
    if operation in high_risk_operations:
        # 检查会话是否是最近验证过的
        last_verified = session.get('last_security_verified')
        if not last_verified:
            return False
        
        # 验证时间是否在15分钟内
        if datetime.utcnow().timestamp() - last_verified > 900:  # 15分钟 = 900秒
            return False
    
    return True


def set_security_headers(response):
    """设置安全响应头
    
    Args:
        response: Flask响应对象
    
    Returns:
        添加了安全头的响应对象
    """
    # Content Security Policy
    nonce = getattr(g, 'csp_nonce', None)
    csp = [
        "default-src 'self'",
        f"script-src 'self' https://cdn.jsdelivr.net" + (f" 'nonce-{nonce}'" if nonce else ""),
        "style-src 'self' https://cdn.jsdelivr.net",
        "font-src 'self' https://cdn.jsdelivr.net",
        "img-src 'self' data:"
    ]
    response.headers['Content-Security-Policy'] = '; '.join(csp)
    
    # 其他安全头
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response