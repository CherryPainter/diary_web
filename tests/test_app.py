import unittest
import json
from flask import url_for
from diary_app import create_app
from diary_app.extensions import db
from diary_app.models import User

class BaseTestCase(unittest.TestCase):
    """测试基类，提供共同的测试设置和工具函数"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试应用实例，使用测试配置
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        db.create_all()
        
        # 创建测试用户
        self.test_user = self._create_test_user()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除数据库表
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def _create_test_user(self):
        """创建测试用户"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user
    
    def _login(self, username='testuser', password='password123'):
        """登录用户并返回JWT token"""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': username, 'password': password}),
            content_type='application/json'
        )
        if response.status_code == 200:
            return response.json.get('token')
        return None

class AuthTestCase(BaseTestCase):
    """认证相关测试"""
    
    def test_register(self):
        """测试用户注册功能"""
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'newpassword123',
                'question': 'What is your pet\'s name?',
                'answer': 'Fluffy'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['username'], 'newuser')
        self.assertEqual(data['email'], 'newuser@example.com')
    
    def test_register_existing_username(self):
        """测试注册已存在的用户名"""
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'testuser',
                'email': 'another@example.com',
                'password': 'password123',
                'question': 'Question',
                'answer': 'Answer'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('message', data)
    
    def test_login(self):
        """测试用户登录功能"""
        token = self._login()
        self.assertIsNotNone(token)
        self.assertTrue(isinstance(token, str))
    
    def test_login_invalid_credentials(self):
        """测试使用无效凭据登录"""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser', 'password': 'wrongpassword'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data['message'], '用户名或密码错误')
    
    def test_logout(self):
        """测试用户登出功能"""
        token = self._login()
        self.assertIsNotNone(token)
        
        response = self.client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], '登出成功')

class DiaryTestCase(BaseTestCase):
    """日记相关测试"""
    
    def test_create_diary(self):
        """测试创建日记功能"""
        token = self._login()
        
        response = self.client.post(
            '/api/diaries',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({
                'title': 'Test Diary',
                'content': 'This is a test diary content.'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['title'], 'Test Diary')
        self.assertEqual(data['content'], 'This is a test diary content.')
    
    def test_get_diaries(self):
        """测试获取日记列表功能"""
        token = self._login()
        
        # 先创建几个日记
        for i in range(3):
            self.client.post(
                '/api/diaries',
                headers={'Authorization': f'Bearer {token}'},
                data=json.dumps({
                    'title': f'Diary {i}',
                    'content': f'Content {i}'
                }),
                content_type='application/json'
            )
        
        # 获取日记列表
        response = self.client.get(
            '/api/diaries',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(isinstance(data['items'], list))
        self.assertEqual(len(data['items']), 3)
    
    def test_get_single_diary(self):
        """测试获取单个日记功能"""
        token = self._login()
        
        # 创建一个日记
        create_response = self.client.post(
            '/api/diaries',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({
                'title': 'Single Diary',
                'content': 'Single diary content.'
            }),
            content_type='application/json'
        )
        
        diary_id = create_response.get_json()['id']
        
        # 获取该日记
        get_response = self.client.get(
            f'/api/diaries/{diary_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(get_response.status_code, 200)
        data = get_response.get_json()
        self.assertEqual(data['title'], 'Single Diary')
        self.assertEqual(data['content'], 'Single diary content.')
    
    def test_update_diary(self):
        """测试更新日记功能"""
        token = self._login()
        
        # 创建一个日记
        create_response = self.client.post(
            '/api/diaries',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({
                'title': 'Update Test',
                'content': 'Original content.'
            }),
            content_type='application/json'
        )
        
        diary_id = create_response.get_json()['id']
        
        # 更新日记
        update_response = self.client.put(
            f'/api/diaries/{diary_id}',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({
                'title': 'Updated Title',
                'content': 'Updated content.'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(update_response.status_code, 200)
        data = update_response.get_json()
        self.assertEqual(data['title'], 'Updated Title')
        self.assertEqual(data['content'], 'Updated content.')
    
    def test_delete_diary(self):
        """测试删除日记功能"""
        token = self._login()
        
        # 创建一个日记
        create_response = self.client.post(
            '/api/diaries',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({
                'title': 'Delete Test',
                'content': 'This will be deleted.'
            }),
            content_type='application/json'
        )
        
        diary_id = create_response.get_json()['id']
        
        # 删除日记
        delete_response = self.client.delete(
            f'/api/diaries/{diary_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(delete_response.status_code, 200)
        data = delete_response.get_json()
        self.assertEqual(data['message'], '删除成功')
        
        # 验证日记已被删除
        get_response = self.client.get(
            f'/api/diaries/{diary_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(get_response.status_code, 404)

class UserTestCase(BaseTestCase):
    """用户相关测试"""
    
    def test_get_current_user(self):
        """测试获取当前用户信息功能"""
        token = self._login()
        
        response = self.client.get(
            '/api/users/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
    
    def test_update_user_info(self):
        """测试更新用户信息功能"""
        token = self._login()
        
        response = self.client.put(
            '/api/users/me',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({
                'email': 'updated@example.com'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['email'], 'updated@example.com')

if __name__ == '__main__':
    unittest.main()