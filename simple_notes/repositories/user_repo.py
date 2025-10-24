from typing import Optional
from sqlalchemy import or_

from simple_notes.extensions import db
from simple_notes.models import User, SecurityProfile

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
        # Prefer the relationship if already loaded/assigned
        profile = user.security_profile
        if profile:
            return profile
        # Double-check directly from DB to avoid duplicate insert when relationship not loaded
        profile = SecurityProfile.query.filter_by(user_id=user.id).first()
        if profile:
            # attach to relationship for consistency
            user.security_profile = profile
            return profile
        # Create a new profile only if none exists; initialize non-null fields
        profile = SecurityProfile(user_id=user.id, failed_count=0, question='', answer_hash='')
        db.session.add(profile)
        # Do not flush here; let caller decide when to commit/flush to avoid premature INSERT
        return profile

    def list_users(self, page: int = 1, per_page: int = 20):
        return User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def commit(self):
        db.session.commit()