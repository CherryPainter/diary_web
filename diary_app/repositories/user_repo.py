from typing import Optional
from sqlalchemy import or_

from ..extensions import db
from ..models import User, SecurityProfile

class UserRepository:
    def get_by_id(self, user_id: int) -> Optional[User]:
        return db.session.get(User, user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        return User.query.filter_by(username=username).first()

    def exists_by_username_or_email(self, username: str, email: str) -> bool:
        return db.session.query(User.id).filter(or_(User.username == username, User.email == email)).first() is not None

    def add(self, user: User):
        db.session.add(user)

    def ensure_profile(self, user: User) -> SecurityProfile:
        profile = user.security_profile
        if not profile:
            profile = SecurityProfile(user_id=user.id, failed_count=0)
            db.session.add(profile)
            db.session.flush()
        return profile

    def list_users(self, page: int = 1, per_page: int = 20):
        return User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def commit(self):
        db.session.commit()