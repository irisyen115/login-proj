import os
from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
from models import db, init_db, User
import random
import string
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app)

@app.route('/status')
def status():
    return jsonify({"status": "ok"})

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

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "帳號已存在"}), 400

    new_user = User(
        username=username,
        email=email,
        key_certificate= generate_reset_token(30)
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    response = make_response(jsonify({"message": "註冊成功", "user": username, "role": "user"}))
    response.set_cookie("user_session", username, httponly=True, secure=True, samesite="Strict")
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
        "user": username,
        "role": user.role,
        "last_login": user.last_login,
        "login_count": user.login_count
    }))
    response.set_cookie("user_session", username, httponly=True, secure=True, samesite="Strict")
    response.set_cookie("role", user.role, httponly=True, secure=True, samesite="Strict")
    return response

@app.route('/logout')
def logout():
    response = make_response(jsonify({"message": "登出成功"}))
    response.set_cookie("user_session", "", expires=0)
    return response

@app.route('/users', methods=['GET'])
def get_users():
    username = request.cookies.get("user_session", "").strip()
    user = User.query.filter_by(username=username).first()
    role = user.role

    if not role or not username:
        return jsonify({"error": "未授權"}), 401

    if role == "admin":
        users = User.query.with_entities(User.id, User.username, User.last_login, User.login_count, User.role).all()
    elif role == "user":
        users = User.query.with_entities(User.id, User.username, User.last_login, User.login_count, User.role).filter_by(username=username).all()
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
    username = request.cookies.get("user_session", "").strip()
    if not file or not username:
        return jsonify({"error": "請提供帳號與照片"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "使用者不存在"}), 404

    filename = f"{user.id}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    user.profile_image = filepath
    user.picture_name = filename
    db.session.commit()

    return jsonify({"message": "照片上傳成功", "file_path": filepath})

@app.route('/get_user_image', methods=['GET'])
def get_user_image():
    username = request.cookies.get("user_session", "").strip()

    if not username:
        return jsonify({"error": "未授權"}), 401

    user = User.query.filter_by(username=username).first()
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
