from typing import Optional, Tuple
from datetime import datetime

from ..repositories.user_repo import UserRepository
from ..repositories.diary_repo import DiaryRepository
from ..models import User, DiaryEntry
from ..extensions import db

class AdminService:
    def __init__(self, user_repo: Optional[UserRepository] = None, diary_repo: Optional[DiaryRepository] = None, admin_users: Optional[set] = None):
        self.user_repo = user_repo or UserRepository()
        self.diary_repo = diary_repo or DiaryRepository()
        self.admin_users = admin_users or set()

    def is_admin(self, username: str) -> bool:
        return username in self.admin_users

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
            # Simple filter when needed (non-paginated here for brevity)
            return DiaryEntry.query.filter_by(user_id=user_id).order_by(DiaryEntry.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return self.diary_repo.paginate_all(page=page, per_page=per_page)

    def delete_entry(self, entry: DiaryEntry) -> Tuple[bool, str]:
        self.diary_repo.delete(entry)
        self.diary_repo.commit()
        return True, '日记已删除'