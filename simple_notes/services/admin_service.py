from typing import Optional, Tuple
from datetime import datetime

from simple_notes.repositories.user_repo import UserRepository
from simple_notes.repositories.note_repo import NoteRepository
from simple_notes.models import User, NoteEntry
from simple_notes.extensions import db

from typing import Optional, Tuple, Set
import json

from simple_notes.models import User, NoteEntry, AppSetting

class AdminService:
    def __init__(self, user_repo: Optional[UserRepository] = None, note_repo: Optional[NoteRepository] = None):
        self.user_repo = user_repo or UserRepository()
        self.note_repo = note_repo or NoteRepository()

    def get_admin_users(self) -> Set[str]:
        setting = AppSetting.query.filter_by(key='admin_users').first()
        if setting and setting.value:
            try:
                data = json.loads(setting.value)
                return set(u for u in data if isinstance(u, str) and u.strip())
            except Exception:
                return set()
        # Fallback to config
        from flask import current_app
        return set(current_app.config.get('ADMIN_USERS', set()))

    def set_admin_users(self, users: Set[str]):
        val = json.dumps(sorted(list(users)))
        setting = AppSetting.query.filter_by(key='admin_users').first()
        if not setting:
            setting = AppSetting(key='admin_users', value=val)
            db.session.add(setting)
        else:
            setting.value = val
        db.session.commit()

    def add_admin_user(self, username: str) -> Tuple[bool, str]:
        users = self.get_admin_users()
        users.add(username.strip())
        self.set_admin_users(users)
        return True, '已添加管理员'

    def remove_admin_user(self, username: str) -> Tuple[bool, str]:
        users = self.get_admin_users()
        users.discard(username.strip())
        self.set_admin_users(users)
        return True, '已移除管理员'

    def is_admin(self, username: str) -> bool:
        return username in self.get_admin_users()

    # Users
    def list_users(self, page: int = 1, per_page: int = 20):
        return self.user_repo.list_users(page=page, per_page=per_page)

    def lock_user(self, user: User) -> Tuple[bool, str]:
        profile = self.user_repo.ensure_profile(user)
        profile.failed_count = 3
        profile.locked_until = None
        self.user_repo.commit()
        return True, '账户已锁定'

    def unlock_user(self, user: User) -> Tuple[bool, str]:
        profile = self.user_repo.ensure_profile(user)
        profile.failed_count = 0
        profile.locked_until = None
        self.user_repo.commit()
        return True, '账户已解锁'

    # Entries
    def list_entries(self, page: int = 1, per_page: int = 20, user_id: Optional[int] = None):
        if user_id:
            return NoteEntry.query.filter_by(user_id=user_id).order_by(NoteEntry.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return self.note_repo.paginate_all(page=page, per_page=per_page)

    def delete_entry(self, entry: NoteEntry) -> Tuple[bool, str]:
        self.note_repo.delete(entry)
        self.note_repo.commit()
        return True, '笔记已删除'