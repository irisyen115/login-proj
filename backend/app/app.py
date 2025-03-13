import os
from flask import Flask, request, jsonify, make_response
import random
import string
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
DB_CONFIG = {
    "dbname": "mydatabase",
    "user": "user",
    "password": "password",
    "host": "pgsql_container",
    "port": 5432
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.close()
    print("✅ 成功連接 PostgreSQL")
except Exception as e:
    print("❌ 無法連接 PostgreSQL:", e)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/status')
def status():
    response = make_response(jsonify({"status": "ok"}))
    response.set_cookie("user_session", "123456", httponly=True, secure=True, samesite="Strict")
    return response

@app.route('/logout')
def logout():
    response = make_response(jsonify({"message": "登出成功"}))
    response.set_cookie("user_session", "", expires=0)
    return response

def generate_reset_token(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password or not email:
        return jsonify({"error": "請提供帳號、密碼和電子郵件"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user:
            return jsonify({"error": "帳號已存在"}), 400

        key_certificate = generate_reset_token(30)
        app.logger.error(f"密鑰為: {key_certificate}")
        cur.execute("INSERT INTO users (username, password_hash, email, last_login, login_count, key_certificate) VALUES (%s, %s, %s, %s, %s, %s)",
                    (username, password_hash, email, None, 0, key_certificate))
        conn.commit()

        response = make_response(jsonify({"message": "註冊成功", "user": username, "role": "user"}))
        response.set_cookie("user_session", username, httponly=True, secure=True, samesite="Strict")
        response.set_cookie("role", "user", httponly=True, secure=True, samesite="Strict")

        return response, 201

    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "請提供帳號和密碼"}), 400

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "帳號不存在"}), 404

        if not user["password_hash"]:
            return jsonify({"error": "密碼欄位錯誤"}), 500

        if bcrypt.check_password_hash(user["password_hash"], password):
            now = datetime.now()
            cur.execute(
                "UPDATE users SET last_login = %s, login_count = login_count + 1 WHERE username = %s RETURNING last_login, login_count, role",
                (now, username)
            )
            updated_user = cur.fetchone()
            conn.commit()

            response = make_response(jsonify({
                "message": "登入成功",
                "user": username,
                "role": updated_user["role"],
                "last_login": updated_user["last_login"],
                "login_count": updated_user["login_count"]
            }))
            response.set_cookie("user_session", username, httponly=True, secure=True, samesite="Strict")
            response.set_cookie("role", updated_user["role"], httponly=True, secure=True, samesite="Strict")
            return response

        return jsonify({"error": "帳號或密碼錯誤"}), 401

    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
@app.route('/users', methods=['GET'])
def get_users():
    username = request.cookies.get("user_session", "").strip()
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    role = user['role']

    if not role or not username:
        return jsonify({"error": "未授權"}), 401

    try:
        if role == "admin":
            cur.execute("SELECT id, username, last_login, login_count, role FROM users")
        elif role == "user":
            cur.execute("SELECT id, username, last_login, login_count, role FROM users WHERE username = %s", (username,))
        else:
            return jsonify({"error": "無法識別角色"}), 403

        users = cur.fetchall()
        return jsonify(users)

    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/upload-avatar', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "請提供照片"}), 400

    file = request.files['file']
    username = request.cookies.get("user_session", "").strip()

    if not file or not username:
        return jsonify({"error": "請提供帳號與照片"}), 400

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "使用者不存在"}), 404

        user_id = user['id']
        filename = f"{user_id}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(filepath)

        cur.execute("UPDATE users SET profile_image = %s WHERE id = %s", (filepath, user_id))
        conn.commit()

        return jsonify({"message": "照片上傳成功", "file_path": filepath})

    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

@app.route('/reset-password/<key_certificate>', methods=['POST'])
def reset_password_with_key_certificate(key_certificate):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT username FROM users WHERE key_certificate = %s", (key_certificate,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "無效的驗證密鑰"}), 400

        username = user["username"]
        new_key_certificate = generate_reset_token(30)

        data = request.json
        new_password = data.get("password")

        if not new_password:
            return jsonify({"error": "請提供新密碼"}), 400

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        cur.execute("UPDATE users SET key_certificate = %s, id_authentication = %s, password_hash = %s WHERE username = %s",
                    (new_key_certificate, False, username, hashed_password))
        conn.commit()
        return jsonify({"message": "密碼重設成功，請重新登入"}), 200
    except psycopg2.Error as db_error:
        return jsonify({"error": f"資料庫錯誤: {str(db_error)}"}), 500
    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
