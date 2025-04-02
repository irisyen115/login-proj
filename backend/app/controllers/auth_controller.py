from flask import Blueprint, request, jsonify, make_response
from services.auth_service import authenticate_google_user, register_user, authenticate_user
from config import Config

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
    user, error = register_user(data)
    if error:
        return jsonify({"error": error}), 400

    response = make_response(jsonify({"message": "註冊成功", "user": user.username, "role": "user"}))
    response.set_cookie("user_id", str(user.id), httponly=True, secure=True, samesite="Strict")
    response.set_cookie("role", "user", httponly=True, secure=True, samesite="Strict")
    return response, 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user, error = authenticate_user(data)
    if error:
        return jsonify({"error": error}), 401

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
