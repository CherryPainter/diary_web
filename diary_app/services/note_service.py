from typing import Optional, Tuple

from ..models import NoteEntry
from ..repositories.note_repo import NoteRepository

class NoteService:
    def __init__(self, repo: Optional[NoteRepository] = None):
        self.repo = repo or NoteRepository()

    def create_entry(self, user_id: int, title: str, content: str) -> Tuple[bool, str, Optional[NoteEntry]]:
        if not title.strip():
            return False, '标题不能为空', None
        entry = NoteEntry(user_id=user_id, title=title.strip(), content=content)
        self.repo.add(entry)
        self.repo.commit()
        return True, '笔记已创建', entry

    def update_entry(self, entry: NoteEntry, title: str, content: str) -> Tuple[bool, str]:
        if not title.strip():
            return False, '标题不能为空'
        entry.title = title.strip()
        entry.content = content
        self.repo.commit()
        return True, '笔记已更新'

    def delete_entry(self, entry: NoteEntry) -> Tuple[bool, str]:
        self.repo.delete(entry)
        self.repo.commit()
        return True, '笔记已删除'