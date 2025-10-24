from typing import Optional, Tuple

from ..models import DiaryEntry
from ..repositories.diary_repo import DiaryRepository

class DiaryService:
    def __init__(self, repo: Optional[DiaryRepository] = None):
        self.repo = repo or DiaryRepository()

    def create_entry(self, user_id: int, title: str, content: str) -> Tuple[bool, str, Optional[DiaryEntry]]:
        if not title.strip():
            return False, '标题不能为空', None
        entry = DiaryEntry(user_id=user_id, title=title.strip(), content=content)
        self.repo.add(entry)
        self.repo.commit()
        return True, '日记已创建', entry

    def update_entry(self, entry: DiaryEntry, title: str, content: str) -> Tuple[bool, str]:
        if not title.strip():
            return False, '标题不能为空'
        entry.title = title.strip()
        entry.content = content
        self.repo.commit()
        return True, '日记已更新'

    def delete_entry(self, entry: DiaryEntry) -> Tuple[bool, str]:
        self.repo.delete(entry)
        self.repo.commit()
        return True, '日记已删除'