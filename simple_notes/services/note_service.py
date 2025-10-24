from datetime import datetime
from typing import Optional, Tuple, List
from simple_notes.models import NoteEntry
from simple_notes.repositories.note_repo import NoteRepository
from simple_notes.extensions import db
import re

class NoteService:
    def __init__(self, repo: Optional[NoteRepository] = None):
        self.repo = repo or NoteRepository()
    
    def create_entry(self, user_id: int, title: str, content: str) -> Tuple[bool, str, Optional[NoteEntry]]:
        """创建新笔记"""
        try:
            # 验证输入
            if not title or len(title.strip()) == 0:
                return False, '标题不能为空', None
            
            if len(title) > 200:
                return False, '标题长度不能超过200个字符', None
            
            # 创建笔记
            entry = NoteEntry(
                user_id=user_id,
                title=title,
                content=content,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.repo.add(entry)
            self.repo.commit()
            
            return True, '笔记已创建', entry
        except Exception as e:
            self.repo.rollback()
            return False, f'创建笔记失败: {str(e)}', None
    
    def update_entry(self, entry: NoteEntry, title: str, content: str) -> Tuple[bool, str]:
        """更新笔记"""
        try:
            # 验证输入
            if not title or len(title.strip()) == 0:
                return False, '标题不能为空'
            
            if len(title) > 200:
                return False, '标题长度不能超过200个字符'
            
            # 更新笔记
            entry.title = title
            entry.content = content
            entry.updated_at = datetime.utcnow()
            
            self.repo.update(entry)
            self.repo.commit()
            
            return True, '笔记已更新'
        except Exception as e:
            self.repo.rollback()
            return False, f'更新笔记失败: {str(e)}'
    
    def delete_entry(self, entry: NoteEntry) -> Tuple[bool, str]:
        """删除笔记"""
        try:
            self.repo.delete(entry)
            self.repo.commit()
            return True, '笔记已删除'
        except Exception as e:
            self.repo.rollback()
            return False, f'删除笔记失败: {str(e)}'
    
    def get_entry_by_id(self, entry_id: int, user_id: int) -> Optional[NoteEntry]:
        """根据ID获取用户的笔记"""
        return self.repo.get_by_id_for_user(entry_id, user_id)
    
    def search_entries(self, user_id: int, keyword: str, page: int = 1, per_page: int = 10):
        """搜索用户的笔记"""
        if not keyword or len(keyword.strip()) == 0:
            return self.repo.list_of_user_paginated(user_id, page, per_page)
        
        return self.repo.search_user_entries(user_id, keyword, page, per_page)
    
    def get_recent_entries(self, user_id: int, limit: int = 10) -> List[NoteEntry]:
        """获取用户最近的笔记"""
        return self.repo.recent_entries(user_id, limit)
    
    def analyze_content(self, content: str) -> dict:
        """分析笔记内容，提取关键词和统计信息"""
        # 简单的文本分析
        words = re.findall(r'\b\w+\b', content)
        word_count = len(words)
        char_count = len(content)
        
        # 计算阅读时间（假设每分钟阅读300个单词）
        reading_time = max(1, int(word_count / 300))
        
        # 提取标题（如果内容中有关键词）
        # 这里可以添加更复杂的NLP分析
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'reading_time_minutes': reading_time
        }