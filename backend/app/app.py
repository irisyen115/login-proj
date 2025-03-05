from flask import Flask, request, jsonify, make_response
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
