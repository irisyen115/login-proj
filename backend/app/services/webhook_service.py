import requests
from flask import jsonify, make_response
from services.email_service import trigger_email
from config import Config
from models.database import db
from models.users import User
from models.line_binding_user import LineBindingUser
import logging
from google.oauth2 import id_token
from google.auth.transport import requests

logging.basicConfig(filename="error.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

IRIS_DS_SERVER_URL = Config.IRIS_DS_SERVER_URL
LINE_REPLY_URL = Config.LINE_REPLY_URL
LINE_ACCESS_TOKEN = Config.LINE_ACCESS_TOKEN

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

def verify_google_token(google_token):
    try:
        google_user_info = id_token.verify_oauth2_token(google_token, requests.Request(), Config.GOOGLE_CLIENT_ID)

        if google_user_info.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            return None

        return {
            "email": google_user_info.get("email"),
            "name": google_user_info.get("name"),
            "picture": google_user_info.get("picture"),
        }
    except Exception as e:
        print(f"Google Token 驗證失敗: {str(e)}")
        return None

def handle_webhook_event(body):
    try:
        for event in body.get("events", []):
            if event.get("type") == "message":
                text = event["message"]["text"]
                uid = event["source"]["userId"]
                if "綁定" in text:
                    login_url = f"{IRIS_DS_SERVER_URL}/Line-login?uid={uid}"
                    reply_message(event["replyToken"], f"請點擊以下網址進行綁定：\n{login_url}")
    except Exception:
        return "Internal Server Error", 500
    return "OK", 200

def bind_email_service(data):
    try:
        google_token = data.get("google_token")
        uid = data.get("uid")
        username = data.get("username")
        password = data.get("password", "")

        if google_token:
            google_user_info = verify_google_token(google_token)
            if not google_user_info:
                return jsonify({"error": "Google 驗證失敗"}), 400

            email = google_user_info.get("email")
            user = User.query.filter_by(email=email).first()

            if not user:
                return jsonify({"error": "帳號不存在"}), 400
        else:
            user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({"error": "帳號不存在"}), 400

        if not user.check_password(password):
            return jsonify({"error": "密碼錯誤"}), 400

        binding = LineBindingUser.query.filter_by(user_id=user.id).first()
        if not binding:
            binding = LineBindingUser(user_id=user.id, line_id=uid)
            db.session.add(binding)
        else:
            binding.line_id = uid

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

        response.set_cookie("user_id", str(user.id), httponly=True, secure=True, samesite="Strict")
        return response

    except Exception as e:
        logging.error(f"發生錯誤: {str(e)}", exc_info=True)
        return jsonify({"error": f"伺服器錯誤: {str(e)}"}), 500
