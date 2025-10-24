"""日记相关模型 - 定义日记、分类、标签和评论的数据结构"""
from datetime import datetime
from sqlalchemy.orm import validates, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table, Text
from app.extensions import db

# 日记和标签的多对多关系表
diary_tag_association = db.Table('diary_tag_association',
    db.Column('diary_id', db.Integer, db.ForeignKey('diary_entries.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('diary_tags.id'), primary_key=True)
)

class DiaryEntry(db.Model):
    """日记条目模型 - 存储用户的日记内容和元数据"""
    __tablename__ = 'diary_entries'
    
    # 基本字段
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 内容字段
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)  # 内容摘要，用于列表显示
    
    # 隐私控制
    is_private = db.Column(db.Boolean, default=True, nullable=False)  # 是否私密（仅自己可见）
    allow_comments = db.Column(db.Boolean, default=False, nullable=False)  # 是否允许评论
    
    # 情感标签
    mood = db.Column(db.String(50), nullable=True)  # 心情标签
    weather = db.Column(db.String(50), nullable=True)  # 天气标签
    
    # 时间信息
    entry_date = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)  # 日记日期
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 状态信息
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)  # 软删除标记
    
    # 分类关联
    category_id = db.Column(db.Integer, db.ForeignKey('diary_categories.id'), nullable=True)
    
    # 关系
    user = relationship('User', back_populates='diaries')
    category = relationship('DiaryCategory', back_populates='diaries')
    tags = relationship('DiaryTag', secondary=diary_tag_association, lazy='subquery',
                      backref=db.backref('diaries', lazy=True))
    comments = relationship('DiaryComment', back_populates='diary', cascade="all, delete-orphan")
    
    @validates('title')
    def validate_title(self, key, value):
        """验证标题长度"""
        if not value or len(value.strip()) == 0:
            raise ValueError('日记标题不能为空')
        if len(value) > 200:
            raise ValueError('日记标题不能超过200个字符')
        return value.strip()
    
    @validates('content')
    def validate_content(self, key, value):
        """验证内容"""
        if not value or len(value.strip()) == 0:
            raise ValueError('日记内容不能为空')
        return value
    
    def generate_summary(self, max_length=150):
        """生成内容摘要"""
        # 移除HTML标签（如果有）
        import re
        clean_text = re.sub(r'<[^>]+>', '', self.content)
        # 生成摘要
        if len(clean_text) > max_length:
            self.summary = clean_text[:max_length] + '...'
        else:
            self.summary = clean_text
    
    def soft_delete(self):
        """软删除日记"""
        self.is_deleted = True
        # 可以选择清空标题和内容，只保留元数据
        self.title = f"[已删除] {self.title[:50]}"
        self.content = "此日记已被删除"
    
    def restore(self):
        """恢复已删除的日记"""
        self.is_deleted = False
    
    def __repr__(self):
        return f'<DiaryEntry {self.title[:30]}...>' if len(self.title) > 30 else f'<DiaryEntry {self.title}>'


class DiaryCategory(db.Model):
    """日记分类模型 - 用于对日记进行分类管理"""
    __tablename__ = 'diary_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 用户特定的分类
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(20), nullable=True, default='#3366cc')  # 分类颜色
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship('User')
    diaries = relationship('DiaryEntry', back_populates='category')
    
    # 确保每个用户的分类名称唯一
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='_user_category_uc'),
    )
    
    @validates('name')
    def validate_name(self, key, value):
        """验证分类名称"""
        if not value or len(value.strip()) == 0:
            raise ValueError('分类名称不能为空')
        if len(value) > 100:
            raise ValueError('分类名称不能超过100个字符')
        return value.strip()
    
    def __repr__(self):
        return f'<DiaryCategory {self.name}>'


class DiaryTag(db.Model):
    """日记标签模型 - 用于对日记进行标签管理"""
    __tablename__ = 'diary_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @validates('name')
    def validate_name(self, key, value):
        """验证标签名称"""
        if not value or len(value.strip()) == 0:
            raise ValueError('标签名称不能为空')
        if len(value) > 50:
            raise ValueError('标签名称不能超过50个字符')
        # 标准化标签名称（小写，去除多余空格）
        return ' '.join(value.strip().lower().split())
    
    def __repr__(self):
        return f'<DiaryTag {self.name}>'


class DiaryComment(db.Model):
    """日记评论模型 - 允许用户对日记进行评论"""
    __tablename__ = 'diary_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('diary_entries.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)  # 软删除标记
    
    # 关系
    diary = relationship('DiaryEntry', back_populates='comments')
    user = relationship('User')
    
    @validates('content')
    def validate_content(self, key, value):
        """验证评论内容"""
        if not value or len(value.strip()) == 0:
            raise ValueError('评论内容不能为空')
        if len(value) > 1000:
            raise ValueError('评论内容不能超过1000个字符')
        return value.strip()
    
    def soft_delete(self):
        """软删除评论"""
        self.is_deleted = True
        self.content = "此评论已被删除"
    
    def __repr__(self):
        return f'<DiaryComment diary_id={self.diary_id} user_id={self.user_id}>'