import os
from flask import Flask, request, jsonify, make_response, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_cors import CORS
from werkzeug.utils import secure_filename

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
        
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "請提供帳號和密碼"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            return jsonify({"error": "帳號已存在"}), 400

        cur.execute("INSERT INTO users (username, password_hash, last_login, login_count) VALUES (%s, %s, %s, %s)",
                    (username, password_hash, None, 0))
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
                "UPDATE users SET last_login = %s, login_count = login_count + 1 WHERE username = %s RETURNING last_login, login_count, role, profile_image",
                (now, username)
            )
            updated_user = cur.fetchone()
            conn.commit()

            response = make_response(jsonify({
                "message": "登入成功",
                "user": username,
                "profile_image": updated_user.get('profile_image', '')
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
            cur.execute("SELECT id, username, last_login, login_count, role, profile_image FROM users")
        elif role == "user":
            cur.execute("SELECT id, username, last_login, login_count, role, profile_image FROM users WHERE username = %s", (username,))
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
        
        cur.execute("UPDATE users SET profile_image = %s, picture_name = %s WHERE id = %s", (filepath, filename, user_id))
        conn.commit()
        
        return jsonify({"message": "照片上傳成功", "file_path": filepath})
    
    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
            
@app.route('/get_user_image', methods=['GET'])
def get_user_image():
    username = request.cookies.get("user_session", "").strip()

    if not username:
        return jsonify({"error": "未授權"}), 401

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        cur.execute("SELECT profile_image, picture_name FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        app.logger.error(f"username: {username}")

        if not user:
            return jsonify({"error": "用戶未找到"}), 404

        profile_image = user['profile_image']

        if profile_image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image)

            if os.path.exists(image_path):
                app.logger.error(f"Image Path:, {profile_image}")
                x = send_from_directory(app.config['UPLOAD_FOLDER'], user['picture_name'])
                app.logger.error(f"response:, {x}")
                return x
            else:
                return jsonify({"error": "圖片檔案不存在"}), 404
        else:
            app.logger.error("Image Path:", image_path)
            
            return jsonify({"error": "用戶未設定圖片"}), 404

    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
