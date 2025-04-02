from flask import Blueprint, request, jsonify, make_response
from services.auth_service import authenticate_google_user
from config import Config
from database import db
from models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/google/callback", methods=["POST"])
def google_callback():
    data = request.get_json()
    id_token_from_google = data.get("id_token")
    if not id_token_from_google:
        return jsonify({"error": "缺少 id_token"}), 400

    user, error = authenticate_google_user(id_token_from_google, Config.CLIENT_ID)
    if error:
        return jsonify({"error": f"Google OAuth 處理失敗: {error}"}), 400

    response = make_response(jsonify({
        "message": "Google 登入成功",
        "username": user.username,
        "role": user.role,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "login_count": user.login_count
    }))
    response.set_cookie("user_id", str(user.id), httponly=True, secure=True, samesite="None", max_age=3600)
    response.set_cookie("role", user.role, httponly=True, secure=True, samesite="None", max_age=3600)
    return response

@auth_bp.route("/register", methods=["POST"])
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

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    response = make_response(jsonify({"message": "註冊成功", "user": username, "role": "user"}))
    response.set_cookie("user_id", str(new_user.id), httponly=True, secure=True, samesite="Strict")
    response.set_cookie("role", "user", httponly=True, secure=True, samesite="Strict")
    return response, 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "請提供帳號和密碼"}), 400

    from models import User, db
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "帳號或密碼錯誤"}), 401

    from services.auth_service import update_login_cache_state
    update_login_cache_state(user.id)
    from datetime import datetime
    user.last_login = datetime.now()
    user.login_count += 1
    db.session.commit()

    response = make_response(jsonify({
        "message": "登入成功",
        "role": user.role,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "login_count": user.login_count
    }))
    response.set_cookie("user_id", str(user.id), httponly=True, secure=True, samesite="Strict")
    response.set_cookie("role", user.role, httponly=True, secure=True, samesite="Strict")
    return response

@auth_bp.route("/logout")
def logout():
    response = make_response(jsonify({"message": "登出成功"}))
    response.set_cookie("user_id", "", expires=0)
    response.set_cookie("role", "", expires=0)
    return response
