import sys
import os

# 把專案根目錄加入模組搜索路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import json
from app import app

class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ 在所有測試前執行一次，用來設定測試環境 """
        cls.client = app.test_client()  # 初始化測試 client
        cls.client.testing = True  # 開啟測試模式

    def test_status(self):
        """ 測試 /status 路徑 """
        response = self.client.get('/status')
        self.assertEqual(response.status_code, 200)  # 驗證 HTTP 回應碼
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')  # 驗證回應內容

    def test_login_success(self):
        """ 測試登入成功的情況 """
        data = {
            "username": "aaa",
            "password": "111"
        }
        response = self.client.post('/login', json=data)
        self.assertEqual(response.status_code, 200)  # 登入成功應該回應 200
        json_data = json.loads(response.data)
        self.assertEqual(json_data['message'], '登入成功')  # 驗證訊息

    def test_login_invalid_credentials(self):
        """ 測試登入失敗的情況（帳號或密碼錯誤） """
        data = {
            "username": "wronguser",
            "password": "wrongpassword"
        }
        response = self.client.post('/login', json=data)
        self.assertEqual(response.status_code, 401)  # 登入失敗應該回應 401
        json_data = json.loads(response.data)
        self.assertEqual(json_data['error'], '帳號或密碼錯誤')  # 驗證錯誤訊息

    def test_register_success(self):
        """ 測試註冊成功的情況 """
        import random
        import string

        def generate_random_string(length=8):
            """生成隨機字符串，默認長度為8"""
            letters_and_digits = string.ascii_letters + string.digits
            return ''.join(random.choice(letters_and_digits) for i in range(length))

        # 隨機生成帳號和密碼
        username = generate_random_string(10)  # 隨機生成一個 10 字符長的帳號
        password = generate_random_string(12)  # 隨機生成一個 12 字符長的密碼

        data = {
            "username": username,
            "password": password
        }
        response = self.client.post('/register', json=data)
        self.assertEqual(response.status_code, 201)  # 註冊成功應該回應 201
        json_data = json.loads(response.data)
        self.assertEqual(json_data['message'], '註冊成功')  # 驗證訊息

    def test_register_missing_fields(self):
        """ 測試註冊時缺少帳號或密碼 """
        data = {"username": "newuser"}
        response = self.client.post('/register', json=data)
        self.assertEqual(response.status_code, 400)  # 應該回應 400，表示錯誤
        json_data = json.loads(response.data)
        self.assertEqual(json_data['error'], '請提供帳號和密碼')  # 驗證錯誤訊息

if __name__ == '__main__':
    unittest.main()
