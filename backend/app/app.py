import os
from flask import Flask, request, jsonify, make_response, send_from_directory, g
from flask_cors import CORS
from models import db, init_db, User, PasswordVerify, EmailVerify
import random
import string
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import desc
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import requests

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app, supports_credentials=True, origins=["https://irisyen115.synology.me"])
init_db(app)

@app.before_request
def get_user_id():
    user_id = request.cookies.get("user_id", "").strip()
    g.user_id = int(user_id) if user_id.isdigit() else None

@app.route('/status')
def status():
    return jsonify({"status": "ok"})

def generate_reset_token(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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
        app.logger.error({"error": f"Google OAuth 回調處理失敗: {str(e)}"})
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
    response.set_cookie("user_session", "", expires=0)
    return response

@app.route('/users', methods=['GET'])
def get_users():
    if not g.user_id:
        return jsonify({"error": "未授權"}), 401

    user = User.query.filter_by(id=g.user_id).first()
    if not user:
        return jsonify({"error": "使用者不存在"}), 404

    role = user.role
    if role == "admin":
        users = User.query.with_entities(User.id, User.username, User.last_login, User.login_count, User.role).all()
    elif role == "user":
        users = User.query.with_entities(User.id, User.username, User.last_login, User.login_count, User.role).filter_by(id=g.user_id)
    else:
        return jsonify({"error": "無法識別角色"}), 403
    return jsonify([user._asdict() for user in users])

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

    user = User.query.filter_by(id=g.user_id).first()
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
