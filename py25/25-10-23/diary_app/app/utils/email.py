# diary_app/app/utils/email.py
"""邮件相关工具函数"""
from flask import request
from app.utils.logging import log_system_event

def send_verification_email(email, subject, message):
    """
    发送验证邮件（模拟）
    
    Args:
        email: 收件人邮箱
        subject: 邮件主题
        message: 邮件内容
    
    Returns:
        bool: 发送是否成功
    """
    # 实际应用中应使用真正的邮件发送服务
    # 这里仅记录日志作为模拟
    log_system_event(
        'info', 
        f'模拟发送邮件到 {email}，主题：{subject}', 
        None, 
        request.remote_addr if request else None
    )
    
    # 模拟发送成功
    return True

def send_password_reset_email(user, reset_token):
    """
    发送密码重置邮件
    
    Args:
        user: 用户对象
        reset_token: 密码重置令牌
    
    Returns:
        bool: 发送是否成功
    """
    subject = "密码重置请求"
    message = f"您好 {user.username}，\n\n"
    message += "您请求重置您的账户密码。点击下方链接重置密码：\n\n"
    message += f"http://yoursite.com/reset-password/{reset_token}\n\n"
    message += "如果您没有请求重置密码，请忽略此邮件。\n"
    
    return send_verification_email(user.email, subject, message)

def send_account_verification_email(user, verification_token):
    """
    发送账户验证邮件
    
    Args:
        user: 用户对象
        verification_token: 账户验证令牌
    
    Returns:
        bool: 发送是否成功
    """
    subject = "账户验证"
    message = f"您好 {user.username}，\n\n"
    message += "感谢您注册我们的服务。请点击下方链接验证您的账户：\n\n"
    message += f"http://yoursite.com/verify-account/{verification_token}\n\n"
    message += "如果您没有注册此账户，请忽略此邮件。\n"
    
    return send_verification_email(user.email, subject, message)