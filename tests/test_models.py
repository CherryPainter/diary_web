import unittest
from datetime import datetime
from diary_app.extensions import db
from diary_app.models import User, DiaryEntry, SecurityProfile, AppSetting

class UserModelTestCase(unittest.TestCase):
    """用户模型测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 这里应该使用测试数据库，为了简化示例使用内存数据库
        # 在实际测试中，应该使用测试配置
        pass
    
    def tearDown(self):
        """测试后的清理工作"""
        pass
    
    def test_password_setting_and_checking(self):
        """测试密码设置和验证功能"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        
        # 验证密码哈希值不为空
        self.assertTrue(user.password_hash is not None)
        # 验证密码检查函数工作正确
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_user_creation(self):
        """测试用户创建功能"""
        user = User(username='newuser', email='newuser@example.com')
        user.set_password('securepassword')
        
        # 验证用户属性
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertIsInstance(user.created_at, datetime)
    
    def test_user_relationships(self):
        """测试用户与其他模型的关系"""
        user = User(username='reluser', email='reluser@example.com')
        user.set_password('password')
        
        # 测试用户与日记的关系
        diary = DiaryEntry(user=user, title='Test Diary', content='Test Content')
        self.assertEqual(diary.user, user)
        
        # 测试用户与安全配置文件的关系
        security_profile = SecurityProfile(
            user=user,
            question='What is your pet\'s name?',
            answer_hash='hashed_answer'
        )
        self.assertEqual(security_profile.user, user)

class DiaryEntryModelTestCase(unittest.TestCase):
    """日记条目模型测试类"""
    
    def test_diary_creation(self):
        """测试日记创建功能"""
        user = User(username='diaryuser', email='diaryuser@example.com')
        user.set_password('password')
        
        diary = DiaryEntry(
            user=user,
            title='My First Diary',
            content='This is the content of my first diary.'
        )
        
        # 验证日记属性
        self.assertEqual(diary.title, 'My First Diary')
        self.assertEqual(diary.content, 'This is the content of my first diary.')
        self.assertIsInstance(diary.created_at, datetime)
        self.assertIsInstance(diary.updated_at, datetime)
        self.assertEqual(diary.user, user)
    
    def test_diary_timestamps(self):
        """测试日记时间戳功能"""
        user = User(username='timeuser', email='timeuser@example.com')
        user.set_password('password')
        
        diary = DiaryEntry(user=user, title='Time Test', content='Time content')
        created_at = diary.created_at
        updated_at = diary.updated_at
        
        # 验证创建时间和更新时间初始相同
        self.assertEqual(created_at, updated_at)
        
        # 模拟更新操作（在实际测试中应更新数据库）
        # 这里只是验证逻辑，实际测试需要通过数据库会话进行

class SecurityProfileModelTestCase(unittest.TestCase):
    """安全配置文件模型测试类"""
    
    def test_security_profile_creation(self):
        """测试安全配置文件创建功能"""
        user = User(username='secureuser', email='secureuser@example.com')
        user.set_password('password')
        
        security_profile = SecurityProfile(
            user=user,
            question='What is your favorite color?',
            answer_hash='hashed_favorite_color'
        )
        
        # 验证安全配置文件属性
        self.assertEqual(security_profile.question, 'What is your favorite color?')
        self.assertEqual(security_profile.answer_hash, 'hashed_favorite_color')
        self.assertEqual(security_profile.failed_count, 0)
        self.assertIsNone(security_profile.locked_until)
        self.assertEqual(security_profile.user, user)
    
    def test_failed_login_count(self):
        """测试登录失败计数功能"""
        user = User(username='faileduser', email='faileduser@example.com')
        user.set_password('password')
        
        security_profile = SecurityProfile(
            user=user,
            question='Security question',
            answer_hash='hashed_answer'
        )
        
        # 验证初始失败计数为0
        self.assertEqual(security_profile.failed_count, 0)
        
        # 模拟增加失败计数
        security_profile.failed_count += 1
        self.assertEqual(security_profile.failed_count, 1)

class AppSettingModelTestCase(unittest.TestCase):
    """应用设置模型测试类"""
    
    def test_app_setting_creation(self):
        """测试应用设置创建功能"""
        setting = AppSetting(key='site_name', value='My Diary App')
        
        # 验证设置属性
        self.assertEqual(setting.key, 'site_name')
        self.assertEqual(setting.value, 'My Diary App')
    
    def test_different_setting_types(self):
        """测试不同类型的设置值"""
        # 测试字符串设置
        str_setting = AppSetting(key='description', value='A simple diary application')
        self.assertEqual(str_setting.value, 'A simple diary application')
        
        # 测试数字设置（以字符串形式存储）
        num_setting = AppSetting(key='max_entries', value='100')
        self.assertEqual(num_setting.value, '100')
        
        # 测试布尔设置（以字符串形式存储）
        bool_setting = AppSetting(key='feature_enabled', value='true')
        self.assertEqual(bool_setting.value, 'true')

if __name__ == '__main__':
    unittest.main()