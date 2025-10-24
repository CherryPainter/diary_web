from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Optional, Tuple

from ..models import User, SecurityProfile
from ..repositories.user_repo import UserRepository
from ..extensions import db

class AuthService:
    def __init__(self, user_repo: Optional[UserRepository] = None):
        self.user_repo = user_repo or UserRepository()

    def register(self, username: str, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        if self.user_repo.exists_by_username_or_email(username.strip(), email.strip()):
            return False, '用户名或邮箱已存在', None
        user = User(username=username.strip(), email=email.strip())
        user.password_hash = generate_password_hash(password)
        self.user_repo.add(user)
        self.user_repo.commit()
        return True, '注册成功，请登录', user

    def validate_login(self, username: str, password: str) -> Tuple[bool, str, Optional[User], Optional[str]]:
        user = self.user_repo.get_by_username(username.strip())
        if not user:
            return False, '用户名或密码错误', None, None
        # 账户锁定检查
        profile = user.security_profile
        if profile and ((profile.locked_until and profile.locked_until > datetime.utcnow()) or (profile.failed_count or 0) >= 3):
            return False, '账户已锁定，请使用辅助验证解锁。', user, profile.question if profile else None
        # 密码检查
        if not check_password_hash(user.password_hash, password):
            profile = self.user_repo.ensure_profile(user)
            profile.failed_count = (profile.failed_count or 0) + 1
            if profile.failed_count >= 3:
                profile.locked_until = None
                db.session.commit()
                return False, '账户已锁定，请使用辅助验证解锁。', user, profile.question
            db.session.commit()
            return False, '用户名或密码错误', None, None
        # 成功登录，清理失败记录
        if user.security_profile:
            user.security_profile.failed_count = 0
            user.security_profile.locked_until = None
        db.session.commit()
        return True, '登录成功', user, None

    def aux_verify(self, username: str, answer: str) -> Tuple[bool, str]:
        user = self.user_repo.get_by_username(username.strip())
        if not user:
            return False, '用户不存在'
        profile = user.security_profile
        if not profile or not profile.question or not profile.answer_hash:
            return False, '未设置辅助验证，无法解锁。'
        if not check_password_hash(profile.answer_hash, answer):
            return False, '辅助验证答案错误。'
        profile.failed_count = 0
        profile.locked_until = None
        db.session.commit()
        return True, '账户已解锁，请重新登录。'

    def save_security(self, user: User, question: str, answer: str, auth_password: str) -> Tuple[bool, str]:
        # trim inputs and validate non-empty
        q = (question or '').strip()
        a = (answer or '').strip()
        if not q or not a:
            return False, '请填写问题和答案'
        # secondary password verification
        if not auth_password or not check_password_hash(user.password_hash, auth_password):
            return False, '需二次验证密码，密码错误'
        # ensure a single profile and update
        profile = self.user_repo.ensure_profile(user)
        profile.question = q
        profile.answer_hash = generate_password_hash(a)
        # reset failed count and unlock on successful save
        profile.failed_count = 0
        profile.locked_until = None
        self.user_repo.commit()
        return True, '辅助验证已保存'

    def change_password(self, user: User, old_password: str, new_password: str, confirm_new: str) -> Tuple[bool, str]:
        if not check_password_hash(user.password_hash, old_password):
            return False, '旧密码错误'
        if not new_password or len(new_password) < 8:
            return False, '新密码长度至少8位'
        if new_password != confirm_new:
            return False, '两次输入的新密码不一致'
        user.password_hash = generate_password_hash(new_password)
        self.user_repo.commit()
        return True, '密码已更新'