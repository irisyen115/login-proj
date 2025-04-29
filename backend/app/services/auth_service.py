import os
import random
import string
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from models.database import db
from models.users import User
from redis import StrictRedis
from config import Config
import requests
from flask import jsonify, make_response, session
from services.email_service import trigger_email
from services.user_service import update_login_cache_state, generate_signed_session_id
from models.line_binding_user import LineBindingUser
import logging

redis_client = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

def generate_reset_token(length=30):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def authenticate_google_user(id_token_str):
    try:
        decoded = id_token.verify_oauth2_token(id_token_str, Request(), Config.GOOGLE_CLIENT_ID)

        email = decoded.get('email')
        picture = decoded.get('picture')
        if not email:
            return None, "無法取得使用者的 email"

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=decoded.get('name'), email=email)
            db.session.add(user)

        if picture:
            image_data = requests.get(picture).content
            filename = f"{user.id}.jpg"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

            with open(filepath, 'wb') as f:
                f.write(image_data)

            user.profile_image = filepath
            user.picture_name = filename
            db.session.add(user)

        user.update_last_login()
        update_login_cache_state(user.id)
        db.session.commit()

        session.permanent = True
        session_id = generate_signed_session_id(user.id)
        redis_client.set(session_id, str(user.id), ex=1800)
        session['session_id'] = session_id

        return user, None
    except Exception as e:
        return None, str(e)

def bind_line_uid_to_user_email(line_uid, user):
    try:
        if not user:
            return jsonify({"error": "帳號不存在"}), 400

        binding = LineBindingUser.query.filter_by(user_id=user.id).first()
        if not binding:
            binding = LineBindingUser(user_id=user.id, line_id=line_uid)
        else:
            return jsonify({"error":f"已綁定{user.email}信箱"}), 400

        db.session.add(binding)
        db.session.commit()

        subject = "帳戶綁定確認"
        body_str = "您的 Line 已綁定此 Email！"
        email_response = trigger_email(f"{Config.IRIS_DS_SERVER_URL}/send-mail", user.email, subject, body_str)

        if not email_response or "error" in email_response:
            return jsonify({"error": "Email 發送失敗"}), 500

        response_data = {
            "message": "綁定成功，請檢查您的 Email",
            "username": user.username,
            "role": user.role,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count
        }

        response = make_response(jsonify(response_data))
        response.status_code = 200

        return response

    except Exception as e:
        logging.error(f"發生錯誤: {str(e)}", exc_info=True)
        return jsonify({"error": f"伺服器錯誤: {str(e)}"}), 500

def identify_google_user_by_token(user_data):
    google_token = user_data.get("google_token")
    username = user_data.get("username")
    password = user_data.get("password", "")

    if google_token:
        google_user_info = verify_google_token(google_token)
        if not google_user_info:
            return jsonify({"error": "Google 驗證失敗"}), 400

        email = google_user_info.get("email")
        user = User.query.filter_by(email=email).first()
    else:
        user = User.query.filter_by(username=username).first()

        if not user.check_password(password):
            return jsonify({"error": "密碼錯誤"}), 400

    user.update_last_login()
    update_login_cache_state(user.id)
    db.session.commit()

    session.permanent = True
    session_id = generate_signed_session_id(user.id)
    redis_client.set(session_id, str(user.id), ex=1800)
    session['session_id'] = session_id

    return user

def verify_google_token(google_token):
    try:
        google_user_info = id_token.verify_oauth2_token(google_token, Request(), Config.GOOGLE_CLIENT_ID)

        if google_user_info.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            return None

        return {
            "email": google_user_info.get("email"),
            "name": google_user_info.get("name"),
            "picture": google_user_info.get("picture"),
        }
    except Exception as e:
        logging.error(f"Google Token 驗證失敗: {str(e)}")
        return None