"""日记服务模块 - 处理日记相关的业务逻辑"""
from datetime import datetime, timedelta
from flask import current_app, request
from app.extensions import db
from app.models.diary import DiaryEntry, DiaryCategory, DiaryTag, DiaryComment
from app.models.system import SystemLog
from app.services.user_service import user_service

class DiaryService:
    """日记服务类 - 提供日记管理相关的功能"""
    
    def create_diary(self, user_id, title, content, **kwargs):
        """创建新日记"""
        # 验证内容长度
        if not title or len(title.strip()) == 0:
            raise ValueError('日记标题不能为空')
        
        if not content or len(content.strip()) == 0:
            raise ValueError('日记内容不能为空')
        
        # 检查内容长度限制
        max_content_length = current_app.config.get('MAX_DIARY_CONTENT_LENGTH', 50000)
        if len(content) > max_content_length:
            raise ValueError(f'日记内容过长，最大长度为{max_content_length}字符')
        
        # 创建日记对象
        diary = DiaryEntry(
            user_id=user_id,
            title=title,
            content=content,
            is_private=kwargs.get('is_private', True),
            allow_comments=kwargs.get('allow_comments', False),
            mood=kwargs.get('mood'),
            weather=kwargs.get('weather')
        )
        
        # 生成摘要
        if kwargs.get('summary'):
            diary.summary = kwargs.get('summary')
        else:
            diary.generate_summary()
        
        # 添加分类
        if kwargs.get('category_id'):
            category = DiaryCategory.query.filter_by(
                id=kwargs.get('category_id'),
                user_id=user_id
            ).first()
            if category:
                diary.category = category
        
        # 添加标签
        if kwargs.get('tags'):
            for tag_id in kwargs.get('tags'):
                tag = DiaryTag.query.filter_by(
                    id=tag_id,
                    user_id=user_id
                ).first()
                if tag:
                    diary.tags.append(tag)
        
        db.session.add(diary)
        db.session.commit()
        
        # 记录创建日志
        SystemLog.log(
            'info',
            f'日记创建成功: {title[:30]}... (ID: {diary.id})',
            user_id=user_id,
            ip_address=request.remote_addr if request else None
        )
        
        return diary
    
    def get_diary(self, diary_id, user_id=None):
        """获取日记详情"""
        diary = DiaryEntry.query.filter_by(id=diary_id, is_deleted=False).first()
        
        if not diary:
            raise ValueError('日记不存在')
        
        # 权限检查
        if diary.is_private and diary.user_id != user_id:
            # 如果不是自己的私密日记，则检查是否有访问权限
            current_user = user_service.get_user_by_id(user_id) if user_id else None
            if not (current_user and current_user.is_admin):
                raise PermissionError('无权访问此日记')
        
        # 更新查看次数
        if user_id != diary.user_id:  # 自己查看不计入统计
            diary.view_count += 1
            db.session.commit()
        
        return diary
    
    def update_diary(self, diary_id, user_id, **kwargs):
        """更新日记"""
        diary = DiaryEntry.query.filter_by(id=diary_id, is_deleted=False).first()
        
        if not diary:
            raise ValueError('日记不存在')
        
        # 权限检查
        current_user = user_service.get_user_by_id(user_id)
        if diary.user_id != user_id and not (current_user and current_user.is_admin):
            raise PermissionError('无权修改此日记')
        
        # 更新字段
        if 'title' in kwargs:
            if not kwargs['title'] or len(kwargs['title'].strip()) == 0:
                raise ValueError('日记标题不能为空')
            diary.title = kwargs['title']
        
        if 'content' in kwargs:
            if not kwargs['content'] or len(kwargs['content'].strip()) == 0:
                raise ValueError('日记内容不能为空')
            
            # 检查内容长度限制
            max_content_length = current_app.config.get('MAX_DIARY_CONTENT_LENGTH', 50000)
            if len(kwargs['content']) > max_content_length:
                raise ValueError(f'日记内容过长，最大长度为{max_content_length}字符')
            
            diary.content = kwargs['content']
            # 重新生成摘要
            diary.generate_summary()
        
        if 'summary' in kwargs:
            diary.summary = kwargs['summary']
        
        if 'is_private' in kwargs:
            diary.is_private = kwargs['is_private']
        
        if 'allow_comments' in kwargs:
            diary.allow_comments = kwargs['allow_comments']
        
        if 'mood' in kwargs:
            diary.mood = kwargs['mood']
        
        if 'weather' in kwargs:
            diary.weather = kwargs['weather']
        
        # 更新分类
        if 'category_id' in kwargs:
            if kwargs['category_id'] is None:
                diary.category = None
            else:
                category = DiaryCategory.query.filter_by(
                    id=kwargs['category_id'],
                    user_id=diary.user_id
                ).first()
                if category:
                    diary.category = category
        
        # 更新标签
        if 'tags' in kwargs:
            diary.tags = []  # 清空现有标签
            if kwargs['tags']:
                for tag_id in kwargs['tags']:
                    tag = DiaryTag.query.filter_by(
                        id=tag_id,
                        user_id=diary.user_id
                    ).first()
                    if tag:
                        diary.tags.append(tag)
        
        diary.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 记录更新日志
        SystemLog.log(
            'info',
            f'日记更新成功: {diary.title[:30]}... (ID: {diary.id})',
            user_id=user_id,
            ip_address=request.remote_addr if request else None
        )
        
        return diary
    
    def delete_diary(self, diary_id, user_id):
        """删除日记（软删除）"""
        diary = DiaryEntry.query.filter_by(id=diary_id, is_deleted=False).first()
        
        if not diary:
            raise ValueError('日记不存在')
        
        # 权限检查
        current_user = user_service.get_user_by_id(user_id)
        if diary.user_id != user_id and not (current_user and current_user.is_admin):
            raise PermissionError('无权删除此日记')
        
        # 软删除
        diary.is_deleted = True
        diary.deleted_at = datetime.utcnow()
        db.session.commit()
        
        # 记录删除日志
        SystemLog.log(
            'audit',
            f'日记已删除: {diary.title[:30]}... (ID: {diary.id})',
            user_id=user_id,
            ip_address=request.remote_addr if request else None
        )
        
        return True
    
    def get_diary_list(self, user_id=None, **filters):
        """获取日记列表"""
        query = DiaryEntry.query.filter_by(is_deleted=False)
        
        # 如果指定了用户，只返回该用户的日记
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        else:
            # 如果未指定用户，只返回公开日记
            query = query.filter_by(is_private=False)
        
        # 应用筛选条件
        if filters.get('category_id'):
            query = query.filter_by(category_id=filters['category_id'])
        
        if filters.get('tag_id'):
            query = query.join(DiaryEntry.tags).filter(DiaryTag.id == filters['tag_id'])
        
        if filters.get('start_date'):
            query = query.filter(DiaryEntry.created_at >= filters['start_date'])
        
        if filters.get('end_date'):
            query = query.filter(DiaryEntry.created_at <= filters['end_date'])
        
        if filters.get('mood'):
            query = query.filter_by(mood=filters['mood'])
        
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            query = query.filter(
                (DiaryEntry.title.like(search_term)) | 
                (DiaryEntry.content.like(search_term)) |
                (DiaryEntry.summary.like(search_term))
            )
        
        # 排序
        order_by = filters.get('order_by', 'created_at')
        order_direction = filters.get('order_direction', 'desc')
        
        if order_direction == 'desc':
            query = query.order_by(getattr(DiaryEntry, order_by).desc())
        else:
            query = query.order_by(getattr(DiaryEntry, order_by).asc())
        
        # 分页
        page = filters.get('page', 1)
        per_page = filters.get('per_page', current_app.config.get('DIARY_PER_PAGE', 10))
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination
    
    def create_category(self, user_id, name, description=''):
        """创建日记分类"""
        # 检查分类名是否已存在
        existing = DiaryCategory.query.filter_by(user_id=user_id, name=name).first()
        if existing:
            raise ValueError('分类名已存在')
        
        category = DiaryCategory(
            user_id=user_id,
            name=name,
            description=description
        )
        
        db.session.add(category)
        db.session.commit()
        
        return category
    
    def get_categories(self, user_id):
        """获取用户的所有分类"""
        return DiaryCategory.query.filter_by(user_id=user_id).order_by(DiaryCategory.created_at.desc()).all()
    
    def update_category(self, category_id, user_id, **kwargs):
        """更新分类"""
        category = DiaryCategory.query.get(category_id)
        
        if not category or category.user_id != user_id:
            raise ValueError('分类不存在或无权修改')
        
        if 'name' in kwargs:
            # 检查新名称是否与其他分类重复
            existing = DiaryCategory.query.filter_by(
                user_id=user_id,
                name=kwargs['name']
            ).filter(DiaryCategory.id != category_id).first()
            if existing:
                raise ValueError('分类名已存在')
            category.name = kwargs['name']
        
        if 'description' in kwargs:
            category.description = kwargs['description']
        
        category.updated_at = datetime.utcnow()
        db.session.commit()
        
        return category
    
    def delete_category(self, category_id, user_id):
        """删除分类"""
        category = DiaryCategory.query.get(category_id)
        
        if not category or category.user_id != user_id:
            raise ValueError('分类不存在或无权删除')
        
        # 检查是否有日记使用此分类
        diary_count = DiaryEntry.query.filter_by(category_id=category_id, is_deleted=False).count()
        if diary_count > 0:
            raise ValueError(f'该分类下还有{diary_count}篇日记，无法删除')
        
        db.session.delete(category)
        db.session.commit()
        
        return True
    
    def create_tag(self, user_id, name):
        """创建标签"""
        # 检查标签是否已存在
        existing = DiaryTag.query.filter_by(user_id=user_id, name=name).first()
        if existing:
            return existing  # 如果已存在，直接返回
        
        tag = DiaryTag(
            user_id=user_id,
            name=name
        )
        
        db.session.add(tag)
        db.session.commit()
        
        return tag
    
    def get_tags(self, user_id):
        """获取用户的所有标签"""
        return DiaryTag.query.filter_by(user_id=user_id).order_by(DiaryTag.usage_count.desc(), DiaryTag.name.asc()).all()
    
    def delete_tag(self, tag_id, user_id):
        """删除标签"""
        tag = DiaryTag.query.get(tag_id)
        
        if not tag or tag.user_id != user_id:
            raise ValueError('标签不存在或无权删除')
        
        # 移除与日记的关联
        tag.diaries = []
        
        db.session.delete(tag)
        db.session.commit()
        
        return True
    
    def add_comment(self, diary_id, user_id, content):
        """添加评论"""
        diary = DiaryEntry.query.filter_by(id=diary_id, is_deleted=False).first()
        
        if not diary:
            raise ValueError('日记不存在')
        
        if not diary.allow_comments:
            raise ValueError('该日记不允许评论')
        
        if not content or len(content.strip()) == 0:
            raise ValueError('评论内容不能为空')
        
        # 检查评论长度限制
        max_comment_length = current_app.config.get('MAX_COMMENT_LENGTH', 1000)
        if len(content) > max_comment_length:
            raise ValueError(f'评论内容过长，最大长度为{max_comment_length}字符')
        
        comment = DiaryComment(
            diary_id=diary_id,
            user_id=user_id,
            content=content
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # 记录评论日志
        if diary.user_id != user_id:  # 如果不是自己评论自己的日记，记录通知
            SystemLog.log(
                'notification',
                f'您的日记收到了新评论: {diary.title[:30]}...',
                user_id=diary.user_id
            )
        
        return comment
    
    def delete_comment(self, comment_id, user_id):
        """删除评论"""
        comment = DiaryComment.query.get(comment_id)
        
        if not comment:
            raise ValueError('评论不存在')
        
        # 获取日记信息，用于权限检查
        diary = DiaryEntry.query.get(comment.diary_id)
        
        # 权限检查：评论作者、日记作者或管理员可以删除
        current_user = user_service.get_user_by_id(user_id)
        if (comment.user_id != user_id and 
            diary.user_id != user_id and 
            not (current_user and current_user.is_admin)):
            raise PermissionError('无权删除此评论')
        
        db.session.delete(comment)
        db.session.commit()
        
        return True
    
    def get_diary_stats(self, user_id):
        """获取用户日记统计信息"""
        # 总日记数
        total_diaries = DiaryEntry.query.filter_by(user_id=user_id, is_deleted=False).count()
        
        # 本月日记数
        today = datetime.utcnow()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_diaries = DiaryEntry.query.filter(
            DiaryEntry.user_id == user_id,
            DiaryEntry.is_deleted == False,
            DiaryEntry.created_at >= month_start
        ).count()
        
        # 分类统计
        categories = DiaryCategory.query.filter_by(user_id=user_id).all()
        category_stats = []
        for category in categories:
            count = DiaryEntry.query.filter_by(
                user_id=user_id,
                category_id=category.id,
                is_deleted=False
            ).count()
            category_stats.append({
                'name': category.name,
                'count': count
            })
        
        # 心情统计
        moods = db.session.query(
            DiaryEntry.mood,
            db.func.count(DiaryEntry.id).label('count')
        ).filter(
            DiaryEntry.user_id == user_id,
            DiaryEntry.is_deleted == False,
            DiaryEntry.mood.isnot(None)
        ).group_by(DiaryEntry.mood).all()
        
        return {
            'total_diaries': total_diaries,
            'month_diaries': month_diaries,
            'category_stats': category_stats,
            'mood_stats': [{'mood': m[0], 'count': m[1]} for m in moods]
        }
    
    # 兼容原有方法
    def create_diary_entry(self, user, title, content):
        """创建日记条目（兼容旧接口）"""
        try:
            entry = self.create_diary(
                user_id=user.id,
                title=title,
                content=content
            )
            return True, entry, "日记创建成功"
        except ValueError as e:
            return False, None, str(e)
        except Exception as e:
            return False, None, "日记创建失败，请稍后重试"
    
    def get_diary_entry(self, user, entry_id):
        """获取日记条目（兼容旧接口）"""
        try:
            return self.get_diary(entry_id, user.id)
        except (ValueError, PermissionError):
            return None
    
    def get_user_diaries(self, user, page=1, per_page=10):
        """获取用户的日记列表（兼容旧接口）"""
        return self.get_diary_list(
            user_id=user.id,
            page=page,
            per_page=per_page
        )
    
    def update_diary_entry(self, user, entry_id, title, content):
        """更新日记条目（兼容旧接口）"""
        try:
            entry = self.update_diary(
                diary_id=entry_id,
                user_id=user.id,
                title=title,
                content=content
            )
            return True, entry, "日记更新成功"
        except (ValueError, PermissionError) as e:
            return False, None, str(e)
        except Exception as e:
            return False, None, "日记更新失败，请稍后重试"

    def get_total_users(self):
        """获取系统总用户数
        
        Returns:
            用户总数
        """
        from app.models.user import User
        return User.query.count()
    
    def get_total_diaries(self):
        """获取系统总日记数
        
        Returns:
            日记总数
        """
        return DiaryEntry.query.filter_by(is_deleted=False).count()
    
    def get_recent_activity(self, days: int = 7):
        """获取最近的系统活动
        
        Args:
            days: 天数范围
        
        Returns:
            活动列表
        """
        from datetime import datetime, timedelta
        from sqlalchemy import func
        from app.models.user import User
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 获取最近创建的日记
        recent_diaries = db.session.query(
            DiaryEntry.created_at,
            User.username,
            func.literal('diary').label('activity_type'),
            DiaryEntry.title.label('description')
        ).join(
            User
        ).filter(
            DiaryEntry.created_at >= cutoff_date,
            DiaryEntry.is_deleted == False
        ).order_by(
            DiaryEntry.created_at.desc()
        ).limit(20).all()
        
        # 获取最近的评论
        recent_comments = db.session.query(
            DiaryComment.created_at,
            User.username,
            func.literal('comment').label('activity_type'),
            func.concat(DiaryEntry.title, ' 评论').label('description')
        ).join(
            User
        ).join(
            DiaryEntry
        ).filter(
            DiaryComment.created_at >= cutoff_date,
            DiaryComment.is_deleted == False
        ).order_by(
            DiaryComment.created_at.desc()
        ).limit(20).all()
        
        # 合并并排序活动
        activities = []
        
        for activity in recent_diaries:
            activities.append({
                'timestamp': activity.created_at,
                'username': activity.username,
                'type': activity.activity_type,
                'description': activity.description
            })
        
        for activity in recent_comments:
            activities.append({
                'timestamp': activity.created_at,
                'username': activity.username,
                'type': activity.activity_type,
                'description': activity.description
            })
        
        # 按时间排序
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return activities[:20]  # 返回最近20条活动

# 创建全局日记服务实例
diary_service = DiaryService()

# 模块级统计函数
def get_diary_statistics(user_id):
    """获取用户日记统计信息 - 模块级函数
    
    Args:
        user_id: 用户ID
    
    Returns:
        包含统计数据的字典
    """
    return diary_service.get_diary_stats(user_id)

def get_system_statistics():
    """获取系统整体统计信息 - 模块级函数
    
    Returns:
        包含系统统计数据的字典
    """
    from app.models.user import User
    return {
        'total_users': diary_service.get_total_users(),
        'total_diaries': diary_service.get_total_diaries()
    }

def get_recent_system_activity(days=7):
    """获取最近的系统活动 - 模块级函数
    
    Args:
        days: 天数范围
    
    Returns:
        活动列表
    """
    return diary_service.get_recent_activity(days)