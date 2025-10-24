"""日记路由模块 - 处理日记相关的HTTP请求"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length
from app.services import diary_service, get_diary_statistics
from app.services.system_service import system_service

# 创建日记路由蓝图
diary_bp = Blueprint('diary', __name__, url_prefix='/diary')

# 日记相关表单
class DiaryForm(FlaskForm):
    """日记表单"""
    title = StringField('标题', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('内容', validators=[DataRequired()])
    summary = StringField('摘要', validators=[Length(max=500)])
    is_private = BooleanField('私密日记', default=True)
    allow_comments = BooleanField('允许评论', default=False)
    mood = SelectField('心情', choices=[
        ('', '选择心情'),
        ('happy', '开心'),
        ('excited', '兴奋'),
        ('peaceful', '平静'),
        ('sad', '难过'),
        ('angry', '生气'),
        ('anxious', '焦虑'),
        ('tired', '疲惫'),
        ('grateful', '感恩')
    ])
    weather = SelectField('天气', choices=[
        ('', '选择天气'),
        ('sunny', '晴天'),
        ('cloudy', '多云'),
        ('rainy', '下雨'),
        ('snowy', '下雪'),
        ('windy', '大风'),
        ('foggy', '大雾')
    ])
    category_id = SelectField('分类', coerce=int, choices=[('0', '未分类')])
    tags = HiddenField('标签')  # 使用隐藏字段存储标签ID，前端使用组件选择
    submit = SubmitField('保存')

class CategoryForm(FlaskForm):
    """分类表单"""
    name = StringField('分类名称', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('分类描述', validators=[Length(max=200)])
    submit = SubmitField('保存')

class CommentForm(FlaskForm):
    """评论表单"""
    content = TextAreaField('评论内容', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('提交')

@diary_bp.before_request
def check_maintenance_mode():
    """检查系统维护模式"""
    if system_service.is_maintenance_mode() and not current_user.is_authenticated:
        return redirect(url_for('user.login'))

@diary_bp.route('/')
@login_required
def diary_list():
    """日记列表"""
    # 获取筛选条件
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    mood = request.args.get('mood', '')
    
    # 构建筛选参数
    filters = {
        'page': page,
        'per_page': 10,
        'search': search
    }
    
    if category_id:
        filters['category_id'] = category_id
    
    if mood:
        filters['mood'] = mood
    
    # 获取日记列表
    pagination = diary_service.get_diary_list(user_id=current_user.id, **filters)
    
    # 获取用户的所有分类
    categories = diary_service.get_categories(current_user.id)
    
    return render_template(
        'diary/list.html', 
        diaries=pagination.items,
        pagination=pagination,
        categories=categories,
        selected_category=category_id,
        search=search,
        selected_mood=mood
    )
    
# 兼容原来的路由
def index():
    """日记列表首页（兼容旧路由）"""
    return diary_list()

@diary_bp.route('/create_entry', methods=['GET', 'POST'])
def create_entry():
    """创建日记（兼容旧路由）"""
    return create()

@diary_bp.route('/view_entry/<int:entry_id>')
def view_entry(entry_id):
    """查看日记详情（兼容旧路由）"""
    return view(entry_id)

@diary_bp.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    """编辑日记（兼容旧路由）"""
    return edit(entry_id)

@diary_bp.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """删除日记（兼容旧路由）"""
    return delete(entry_id)

@diary_bp.route('/search', methods=['GET'])
@login_required
def search():
    """搜索日记"""
    # 获取搜索关键词和分页参数
    keyword = request.args.get('keyword', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建筛选参数
    filters = {
        'page': page,
        'per_page': per_page,
        'search': keyword
    }
    
    # 执行搜索
    pagination = diary_service.get_diary_list(user_id=current_user.id, **filters)
    
    # 计算总页数
    total_pages = pagination.pages
    
    return render_template(
        'diary/search.html',
        diaries=pagination.items,
        pagination=pagination,
        total_pages=total_pages,
        page=page,
        per_page=per_page,
        keyword=keyword
    )

@diary_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """创建日记"""
    form = DiaryForm()
    
    # 加载用户的分类
    categories = diary_service.get_categories(current_user.id)
    form.category_id.choices = [(0, '未分类')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        try:
            # 处理标签
            tag_ids = []
            if form.tags.data:
                tag_ids = [int(id) for id in form.tags.data.split(',') if id.isdigit()]
            
            # 创建日记
            diary = diary_service.create_diary(
                user_id=current_user.id,
                title=form.title.data,
                content=form.content.data,
                summary=form.summary.data if form.summary.data else None,
                is_private=form.is_private.data,
                allow_comments=form.allow_comments.data,
                mood=form.mood.data if form.mood.data else None,
                weather=form.weather.data if form.weather.data else None,
                category_id=form.category_id.data if form.category_id.data != 0 else None,
                tags=tag_ids
            )
            
            flash('日记创建成功！', 'success')
            return redirect(url_for('diary.view', entry_id=diary.id))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('创建日记失败，请稍后重试', 'error')
    
    return render_template('diary/create.html', form=form)

@diary_bp.route('/<int:entry_id>')
def view(entry_id):
    """查看日记详情"""
    try:
        # 获取当前用户ID（如果已登录）
        current_user_id = current_user.id if current_user.is_authenticated else None
        
        # 获取日记详情
        diary = diary_service.get_diary(entry_id, current_user_id)
        
        # 准备评论表单
        comment_form = CommentForm()
        
        return render_template(
            'diary/view.html', 
            entry=diary,
            comment_form=comment_form
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('diary.diary_list'))
    except PermissionError as e:
        flash(str(e), 'error')
        return redirect(url_for('main.index'))

@diary_bp.route('/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(entry_id):
    """编辑日记"""
    try:
        # 获取日记
        diary = diary_service.get_diary(entry_id, current_user.id)
        
        form = DiaryForm(obj=diary)
        
        # 加载用户的分类
        categories = diary_service.get_categories(current_user.id)
        form.category_id.choices = [(0, '未分类')] + [(c.id, c.name) for c in categories]
        
        # 设置初始值
        if diary.category:
            form.category_id.data = diary.category.id
        
        # 初始化标签
        form.tags.data = ','.join([str(tag.id) for tag in diary.tags])
        
        if form.validate_on_submit():
            # 处理标签
            tag_ids = []
            if form.tags.data:
                tag_ids = [int(id) for id in form.tags.data.split(',') if id.isdigit()]
            
            # 更新日记
            diary = diary_service.update_diary(
                diary_id=entry_id,
                user_id=current_user.id,
                title=form.title.data,
                content=form.content.data,
                summary=form.summary.data if form.summary.data else None,
                is_private=form.is_private.data,
                allow_comments=form.allow_comments.data,
                mood=form.mood.data if form.mood.data else None,
                weather=form.weather.data if form.weather.data else None,
                category_id=form.category_id.data if form.category_id.data != 0 else None,
                tags=tag_ids
            )
            
            flash('日记更新成功！', 'success')
            return redirect(url_for('diary.view', entry_id=diary.id))
    
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('diary.diary_list'))
    except PermissionError as e:
        flash(str(e), 'error')
        return redirect(url_for('diary.diary_list'))
    
    return render_template('diary/edit.html', form=form, entry=diary)

@diary_bp.route('/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete(entry_id):
    """删除日记"""
    try:
        diary_service.delete_diary(entry_id, current_user.id)
        flash('日记已成功删除', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except PermissionError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('删除日记失败，请稍后重试', 'error')
    
    return redirect(url_for('diary.diary_list'))

# 评论路由
@diary_bp.route('/<int:entry_id>/comment', methods=['POST'])
@login_required
def add_comment(entry_id):
    """添加评论"""
    form = CommentForm()
    
    if form.validate_on_submit():
        try:
            diary_service.add_comment(
                diary_id=entry_id,
                user_id=current_user.id,
                content=form.content.data
            )
            flash('评论添加成功！', 'success')
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('添加评论失败，请稍后重试', 'error')
    
    return redirect(url_for('diary.view', entry_id=entry_id))

@diary_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """删除评论"""
    try:
        # 先获取评论信息，用于重定向
        from app.models.diary import DiaryComment
        comment = DiaryComment.query.get(comment_id)
        if comment:
            entry_id = comment.diary_id
            
            diary_service.delete_comment(comment_id, current_user.id)
            flash('评论已删除', 'success')
            
            return redirect(url_for('diary.view', entry_id=entry_id))
    except ValueError as e:
        flash(str(e), 'error')
    except PermissionError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('删除评论失败', 'error')
    
    return redirect(url_for('main.index'))

# 分类管理路由
@diary_bp.route('/categories')
@login_required
def category_list():
    """分类列表"""
    categories = diary_service.get_categories(current_user.id)
    return render_template('diary/categories.html', categories=categories)

@diary_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """创建分类"""
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            diary_service.create_category(
                user_id=current_user.id,
                name=form.name.data,
                description=form.description.data
            )
            flash('分类创建成功！', 'success')
            return redirect(url_for('diary.category_list'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('创建分类失败，请稍后重试', 'error')
    
    return render_template('diary/category_form.html', form=form)

@diary_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """编辑分类"""
    try:
        # 获取分类
        from app.models.diary import DiaryCategory
        category = DiaryCategory.query.filter_by(
            id=category_id,
            user_id=current_user.id
        ).first()
        
        if not category:
            flash('分类不存在', 'error')
            return redirect(url_for('diary.category_list'))
        
        form = CategoryForm(obj=category)
        
        if form.validate_on_submit():
            diary_service.update_category(
                category_id=category_id,
                user_id=current_user.id,
                name=form.name.data,
                description=form.description.data
            )
            flash('分类更新成功！', 'success')
            return redirect(url_for('diary.category_list'))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('diary.category_list'))
    except Exception as e:
        flash('更新分类失败，请稍后重试', 'error')
    
    return render_template('diary/category_form.html', form=form, category=category)

@diary_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """删除分类"""
    try:
        diary_service.delete_category(category_id, current_user.id)
        flash('分类已成功删除', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('删除分类失败，请稍后重试', 'error')
    
    return redirect(url_for('diary.category_list'))

# 标签管理路由 - 主要通过AJAX接口
@diary_bp.route('/api/tags', methods=['GET'])
@login_required
def get_tags():
    """获取用户标签（AJAX接口）"""
    try:
        tags = diary_service.get_tags(current_user.id)
        return jsonify({
            'tags': [{'id': tag.id, 'name': tag.name} for tag in tags]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@diary_bp.route('/api/tags', methods=['POST'])
@login_required
def create_tag():
    """创建标签（AJAX接口）"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': '缺少标签名称'}), 400
        
        tag = diary_service.create_tag(
            user_id=current_user.id,
            name=data['name']
        )
        
        return jsonify({
            'id': tag.id,
            'name': tag.name
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 统计路由
@diary_bp.route('/stats')
@login_required
def diary_stats():
    """日记统计信息"""
    try:
        stats = get_diary_statistics(current_user.id)
        return render_template('diary/stats.html', stats=stats)
    except Exception as e:
        flash('获取统计信息失败', 'error')
        return redirect(url_for('diary.diary_list'))

# 公开日记路由
@diary_bp.route('/public')
def public_diaries():
    """公开日记列表"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    # 获取公开日记列表
    pagination = diary_service.get_diary_list(
        page=page,
        per_page=10,
        search=search
    )
    
    return render_template('diary/public.html', diaries=pagination.items, pagination=pagination, search=search)

@diary_bp.route('/recent')
@login_required
def recent():
    """获取最近的日记"""
    # 获取最近的5篇日记
    recent_diaries = diary_service.get_recent_diaries(current_user, limit=5)
    
    return render_template('recent.html', diaries=recent_diaries)

@diary_bp.route('/api/search', methods=['GET'])
def api_search():
    """搜索日记API（用于实时搜索）"""
    if not current_user.is_authenticated:
        return jsonify({'error': '未登录'}), 401
    
    keyword = request.args.get('keyword', '', type=str)
    limit = request.args.get('limit', 5, type=int)
    
    # 构建筛选参数
    filters = {
        'page': 1,
        'per_page': limit,
        'search': keyword
    }
    
    # 执行搜索
    pagination = diary_service.get_diary_list(user_id=current_user.id, **filters)
    
    # 构建响应
    results = [{
        'id': entry.id,
        'title': entry.title,
        'created_at': entry.created_at.isoformat(),
        'summary': entry.summary if hasattr(entry, 'summary') else ''
    } for entry in pagination.items]
    
    return jsonify(results)

# 添加路由别名，方便在模板中使用
diary_bp.add_url_rule('/', 'index', diary_list, methods=['GET'])