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

# create_table_sql = """
# CREATE TABLE IF NOT EXISTS users (
#     id SERIAL PRIMARY KEY,
#     username VARCHAR(50) UNIQUE NOT NULL,
#     email VARCHAR(100) UNIQUE NOT NULL,
#     password_hash TEXT NOT NULL,
#     role VARCHAR(20) DEFAULT 'user',
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP    
# );
# """

# 測試連線
try:
    conn = psycopg2.connect(**DB_CONFIG)
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
    email = data.get("email")

    if not username or not password or not email:
        return jsonify({"error": "請提供帳號、密碼和電子郵件"}), 400

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 查詢使用者
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if user and bcrypt.check_password_hash(user["password_hash"], password):
            return jsonify({"message": "登入成功", "user": username}), 200
        else:
            return jsonify({"error": "帳號、電子郵件或密碼錯誤"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()
        
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    print("XDDDD")

    if not username or not password or not email:
        return jsonify({"error": "請提供帳號、密碼和電子郵件"}), 400

    # 密碼加密
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 插入資料庫
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, password_hash))
        conn.commit()

        return jsonify({"message": "註冊成功"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
