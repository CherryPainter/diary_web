from typing import Optional, List

from ..extensions import db
from ..models import NoteEntry

class NoteRepository:
    def list_of_user_paginated(self, user_id: int, page: int, per_page: int = 10):
        return NoteEntry.query.filter_by(user_id=user_id).order_by(NoteEntry.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def recent_entries(self, user_id: int, limit: int = 50) -> List[NoteEntry]:
        return NoteEntry.query.filter_by(user_id=user_id).order_by(NoteEntry.created_at.desc()).limit(limit).all()

    def add(self, entry: NoteEntry):
        db.session.add(entry)

    def get_by_id_for_user(self, entry_id: int, user_id: int) -> Optional[NoteEntry]:
        return NoteEntry.query.filter_by(id=entry_id, user_id=user_id).first()

    def delete(self, entry: NoteEntry):
        db.session.delete(entry)

    def paginate_all(self, page: int = 1, per_page: int = 20):
        return NoteEntry.query.order_by(NoteEntry.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def commit(self):
        db.session.commit()