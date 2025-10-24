from typing import Optional, List, Dict, Any
from sqlalchemy import or_, desc
from simple_notes.models import NoteEntry
from simple_notes.extensions import db

class NoteRepository:
    """笔记仓库，负责笔记数据的CRUD操作"""
    
    def add(self, entry: NoteEntry) -> None:
        """添加新笔记"""
        db.session.add(entry)
    
    def update(self, entry: NoteEntry) -> None:
        """更新笔记"""
        db.session.merge(entry)
    
    def delete(self, entry: NoteEntry) -> None:
        """删除笔记"""
        db.session.delete(entry)
    
    def commit(self) -> None:
        """提交事务"""
        db.session.commit()
    
    def rollback(self) -> None:
        """回滚事务"""
        db.session.rollback()
    
    def get_by_id(self, entry_id: int) -> Optional[NoteEntry]:
        """根据ID获取笔记"""
        return NoteEntry.query.get(entry_id)
    
    def get_by_id_for_user(self, entry_id: int, user_id: int) -> Optional[NoteEntry]:
        """根据ID和用户ID获取笔记"""
        return NoteEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    
    def list_by_user(self, user_id: int) -> List[NoteEntry]:
        """获取用户的所有笔记"""
        return NoteEntry.query.filter_by(user_id=user_id).order_by(desc(NoteEntry.created_at)).all()
    
    def list_of_user_paginated(self, user_id: int, page: int = 1, per_page: int = 10):
        """分页获取用户的笔记"""
        return NoteEntry.query.filter_by(user_id=user_id).order_by(desc(NoteEntry.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def list_paginated(self, page: int = 1, per_page: int = 20):
        """分页获取所有笔记（管理员用）"""
        return NoteEntry.query.order_by(desc(NoteEntry.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def paginate_all(self, page: int = 1, per_page: int = 20):
        """分页获取所有笔记"""
        return NoteEntry.query.order_by(desc(NoteEntry.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def search_user_entries(self, user_id: int, keyword: str, page: int = 1, per_page: int = 10):
        """搜索用户的笔记"""
        search_pattern = f"%{keyword}%"
        return NoteEntry.query.filter(
            NoteEntry.user_id == user_id,
            or_(
                NoteEntry.title.ilike(search_pattern),
                NoteEntry.content.ilike(search_pattern)
            )
        ).order_by(desc(NoteEntry.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    def recent_entries(self, user_id: int, limit: int = 50) -> List[NoteEntry]:
        """获取用户最近的笔记"""
        return NoteEntry.query.filter_by(user_id=user_id).order_by(
            desc(NoteEntry.created_at)
        ).limit(limit).all()
    
    def get_entries_by_date_range(self, user_id: int, start_date, end_date):
        """根据日期范围获取笔记"""
        return NoteEntry.query.filter(
            NoteEntry.user_id == user_id,
            NoteEntry.created_at >= start_date,
            NoteEntry.created_at <= end_date
        ).order_by(desc(NoteEntry.created_at)).all()
    
    def count_by_user(self, user_id: int) -> int:
        """统计用户的笔记数量"""
        return NoteEntry.query.filter_by(user_id=user_id).count()
    
    def get_total_count(self) -> int:
        """获取所有笔记的总数"""
        return NoteEntry.query.count()