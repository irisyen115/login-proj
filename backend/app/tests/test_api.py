import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import json
from app import app

class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.client.testing = True

    def test_status(self):
        response = self.client.get('/status')
        self.assertEqual(response.status_code, 200) 
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok') 

    def test_login_success(self):
        data = {
            "username": "aaa",
            "password": "111"
        }
        response = self.client.post('/login', json=data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['message'], '登入成功')

    def test_login_invalid_credentials(self):
        data = {
            "username": "wronguser",
            "password": "wrongpassword"
        }
        response = self.client.post('/login', json=data)
        self.assertEqual(response.status_code, 401)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['error'], '帳號或密碼錯誤')

    def test_register_success(self):
        import random
        import string

        def generate_random_string(length=8):
            letters_and_digits = string.ascii_letters + string.digits
            return ''.join(random.choice(letters_and_digits) for i in range(length))

        username = generate_random_string(10)
        password = generate_random_string(12)

        data = {
            "username": username,
            "password": password
        }
        response = self.client.post('/register', json=data)
        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['message'], '註冊成功')

    def test_register_missing_fields(self):
        data = {"username": "newuser"}
        response = self.client.post('/register', json=data)
        self.assertEqual(response.status_code, 400)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['error'], '請提供帳號和密碼') 

if __name__ == '__main__':
    unittest.main()
