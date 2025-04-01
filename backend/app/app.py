import os
from flask import Flask, request, jsonify, make_response, send_from_directory, g, json
from models import db, init_db, User, PasswordVerify, EmailVerify
import random
import string
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import desc
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import requests
import redis

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
LINE_REPLY_URL = os.getenv("LINE_REPLY_URL")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
SERVER_URL = os.getenv("SERVER_URL")
redis_host = os.getenv('REDIS_HOST')
redis_port = int(os.getenv('REDIS_PORT'))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

def trigger_email(url, recipient, subject, body_str):
    data = {
        "recipient": recipient,
        "subject": subject,
        "body": body_str
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return {"error": "Invalid JSON response from email service"}
    else:
        return {"error": f"Failed to send email, status code: {response.status_code}"}

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        body = request.json
        for event in body["events"]:
            if event["type"] == "message":
                text = event["message"]["text"]
                uid = event["source"]["userId"]

                if "綁定" in text:
                    login_url = f"{SERVER_URL}/Line-login?uid={uid}"
                    reply_message(event["replyToken"], f"請點擊以下網址進行綁定：\n{login_url}")
    except Exception as e:
        app.logger.error(f"Error in webhook: {str(e)}")
        return "Internal Server Error", 500
    return "OK", 200

def reply_message(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(LINE_REPLY_URL, json=payload, headers=headers)

BIND_DATA = {}

@app.route("/bind-email", methods=["POST"])
def bind_email():
    try:
        data = request.json
        uid = data.get("uid")
        email = data.get("email")

        if not uid or not email:
            return jsonify({"error": "缺少 UID 或 Email"}), 400

        BIND_DATA[uid] = email
        app.logger.error(BIND_DATA)

        subject = "帳戶綁定確認"
        body_str = f"您的 Line 已綁定此 Email！"
        email_response = trigger_email(f"{SERVER_URL}/send-mail", email, subject, body_str)

        if "error" in email_response:
            return jsonify({"error": "Email 發送失敗"}), 500

        return jsonify({"message": "綁定成功，請檢查您的 Email"}), 200
    except Exception as e:
        app.logger.error(f"Error in bind_email: {str(e)}")
        return jsonify({"error": "伺服器錯誤"}), 500

@app.before_request
def get_user_id():
    user_id = request.cookies.get("user_id", "").strip()
    g.user_id = int(user_id) if user_id.isdigit() else None

@app.route('/status')
def status():
    return jsonify({"status": "ok"})

def generate_reset_token(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def user_key(uid):
    return f"user:{uid}"

def update_login_cache_state(uid):
    cached_user_data = redis_client.get(user_key(uid))
    try:
        if cached_user_data:
            cached_user_data = json.loads(cached_user_data)
            cached_user_data['last_login'] = datetime.now()
            cached_user_data['login_count'] += 1
            redis_client.setex(f"user:{uid}", 3600, json.dumps(cached_user_data))
        else:
            user = User.query.filter_by(id=int(uid)).first()
            if user:
                redis_client.setex(user_key(uid), 3600, user.to_json())
    except Exception as e:
        app.logger.error(e)

@app.route('/auth/google/callback', methods=['POST'])
def oauth_callback():
    data = request.get_json()
    id_token_from_google = data.get('id_token')

    if not id_token_from_google:
        return jsonify({"error": "缺少 id_token"}), 400

    try:
        decoded_token = id_token.verify_oauth2_token(
            id_token_from_google, Request(), CLIENT_ID
        )

        username = decoded_token.get('name')
        email = decoded_token.get('email')
        picture = decoded_token.get('picture')
        if not email:
            return jsonify({"error": "無法取得使用者的 email"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=username, email=email)
            db.session.add(user)

        if picture:
            image_data = requests.get(picture).content
            filename = f"{user.id}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            with open(filepath, 'wb') as f:
                f.write(image_data)

            user.profile_image = filepath
            user.picture_name = filename
            db.session.add(user)

        update_login_cache_state(user.id)
        user.last_login = datetime.now()
        user.login_count += 1
        db.session.commit()

        response = make_response(jsonify({
            "message": "Google 登入成功",
            "username": username,
            "role": user.role,
            "last_login": user.last_login,
            "login_count": user.login_count
        }))

        response.set_cookie("user_id", str(user.id), httponly=True, secure=True, samesite="None", max_age=3600)
        response.set_cookie("role", user.role, httponly=True, secure=True, samesite="None", max_age=3600)

        return response
    except Exception as e:
        return jsonify({"error": f"Google OAuth 回調處理失敗: {str(e)}"}), 400

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not username or not password or not email:
        return jsonify({"error": "請提供帳號、密碼和電子郵件"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "帳號已存在"}), 400

    new_user = User(
        username=username,
        email=email,
        password=password
    )
    db.session.add(new_user)
    db.session.commit()

    response = make_response(jsonify({"message": "註冊成功", "user": username, "role": "user"}))
    response.set_cookie("user_id", str(new_user.id), httponly=True, secure=True, samesite="Strict")
    response.set_cookie("role", "user", httponly=True, secure=True, samesite="Strict")

    return response, 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "請提供帳號和密碼"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "帳號或密碼錯誤"}), 401

    update_login_cache_state(user.id)
    user.last_login = datetime.now()
    user.login_count += 1
    db.session.commit()

    response = make_response(jsonify({
        "message": "登入成功",
        "role": user.role,
        "last_login": user.last_login,
        "login_count": user.login_count
    }))

    response.set_cookie("user_id", str(user.id), httponly=True, secure=True, samesite="Strict")
    response.set_cookie("role", user.role, httponly=True, secure=True, samesite="Strict")
    return response

@app.route('/logout')
def logout():
    response = make_response(jsonify({"message": "登出成功"}))
    response.set_cookie("user_id", "", expires=0)
    response.set_cookie("role", "", expires=0)
    return response

def get_user_by_id(uid):
    try:
        cached_user_data = redis_client.get(f"user:{uid}")
        if cached_user_data:
            return User.from_json(cached_user_data)
        else:
            user = User.query.filter_by(id=int(uid)).first()
            if user:
                redis_client.setex(f"user:{uid}", 3600, user.to_json())
            return user
    except Exception as e:
        app.logger.error(e)
        return None

@app.route('/users', methods=['GET'])
def get_users():
    try:
        if not g.user_id:
            return jsonify({"error": "未授權"}), 401

        user = get_user_by_id(g.user_id)
        if not user:
            return jsonify({"error": "使用者不存在"}), 404

        role = user.role
        if role == "admin":
            users = User.query.with_entities(User.id, User.username, User.last_login, User.login_count, User.role).all()
            users_data = [user_row._asdict() for user_row in users]
            return jsonify(users_data)
        elif role == "user":
            user_list = [user]
            users_data = [user_col.to_dict() for user_col in user_list]
            return jsonify(users_data)
        else:
            return jsonify({"error": "無法識別角色"}), 403
    except Exception as e:
        app.logger.error(f"獲取使用者失敗: {str(e)}")
        return jsonify({"error": "內部伺服器錯誤"}), 500

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload-avatar', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "請提供照片"}), 400

    file = request.files['file']
    if not file:
        return jsonify({"error": "請提供照片"}), 400

    if not g.user_id:
        return jsonify({"error": "未授權"}), 401

    user = User.query.filter_by(id=g.user_id).first()
    if not user:
        return jsonify({"error": "使用者不存在"}), 404

    filename = f"{g.user_id}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    user.profile_image = filepath
    user.picture_name = filename
    db.session.commit()
    return jsonify({"message": "照片上傳成功", "file_path": filepath})

@app.route('/get_user_image', methods=['GET'])
def get_user_image():
    if not g.user_id:
        return jsonify({"error": "未授權"}), 401

    user = get_user_by_id(g.user_id)
    if not user:
        return jsonify({"error": "用戶未找到"}), 404

    if user.profile_image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_image)
        if os.path.exists(image_path):
            try:
                return send_from_directory(app.config['UPLOAD_FOLDER'], user.picture_name, as_attachment=True)
            except Exception as e:
                return jsonify({"error": f"檔案讀取錯誤: {str(e)}"}), 500
        else:
            return jsonify({"error": "圖片檔案不存在"}), 404
    return jsonify({"error": "無圖片可顯示"}), 404

@app.route('/send-authentication', methods=['POST'])
def send_authentication():
    try:
        data = request.json
        username = data.get("username")
        if not username:
            return jsonify({"message": "請輸入用戶名"}), 404

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"message": "用戶不存在"}), 404
        if not user.email:
            return jsonify({"message": "用戶未綁定 Email，請先綁定"}), 400

        password_verify = PasswordVerify.query.filter_by(user_id=user.id).order_by(desc(PasswordVerify.valid_until)).first()
        current_time = datetime.utcnow()
        if password_verify and current_time <= password_verify.valid_until:
            return jsonify({"message": "驗證碼已發送，請前往電子信箱驗收，勿重複點取"}), 404
        else:
            new_password_verify = PasswordVerify(
                password_verify_code=generate_reset_token(30),
                valid_until = datetime.utcnow() + timedelta(minutes=15),
                user_id = user.id
            )
            db.session.add(new_password_verify)
        db.session.commit()
        return jsonify({"message": "驗證信已發送，請重新設置"}), 200
    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

@app.route("/verify-email", methods=["POST"])
def verify_email():
    try:
        data = request.json
        username = data.get("username")
        if not username:
            return jsonify({"message": "請輸入用戶名"}), 404

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"message": "用戶不存在"}), 404
        if not user.email:
            return jsonify({"message": "用戶未綁定 Email，若需綁定，請洽系統服務"}), 400

        email_verify = EmailVerify.query.filter_by(user_id=user.id).order_by(desc(EmailVerify.valid_until)).first()
        current_time = datetime.utcnow()
        if email_verify and current_time <= email_verify.valid_until:
            return jsonify({"message": "驗證碼已發送，請前往電子信箱驗收，請勿重複點取"}), 400
        else:
            new_email_verify = EmailVerify(
                email_verify_code=generate_reset_token(6),
                valid_until=datetime.utcnow() + timedelta(minutes=15),
                user_id=user.id
            )
            db.session.add(new_email_verify)
        db.session.commit()
        return jsonify({"email": user.email, "message": "驗證碼已發送，請檢查電子郵件"}), 200
    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

@app.route('/reset-password/<password_verify_code>', methods=['POST'])
def reset_password_with_password_verify_code(password_verify_code):
    try:
        password_verify = PasswordVerify.query.filter_by(password_verify_code=password_verify_code).first()
        user = password_verify.user
        current_time = datetime.now()
        if current_time > password_verify.valid_until:
            return jsonify({"message": "驗證密鑰已過期"}), 400

        data = request.json
        new_password = data.get("password")
        if not new_password:
            return jsonify({"message": "請提供新密碼"}), 400

        user.set_password(new_password)
        db.session.commit()
        return jsonify({"message": "密碼重設成功，請重新登入"}), 200
    except Exception as e:
        return jsonify({"error": f"發生錯誤: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
