from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# 資料庫設定
DB_CONFIG = {
    "dbname": "mydatabase",
    "user": "user",
    "password": "password",
    "host": "pgsql_container",
    "port": 5432
}

# 測試連線
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
    return jsonify({"status": "ok"})

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

        # 查詢使用者
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if user and bcrypt.check_password_hash(user["password_hash"], password):
            return jsonify({"message": "登入成功", "user": username}), 200
        else:
            return jsonify({"error": "帳號或密碼錯誤"}), 401

    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
        
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "請提供帳號和密碼"}), 400

    # 密碼加密
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 插入資料庫
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()

        return jsonify({"message": "註冊成功"}), 201

    except psycopg2.Error as e:
        return jsonify({"error": "帳號已存在"}), 500

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
