import requests
from flask import jsonify
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

def handle_bind_email(data):
    try:
        uid = data.get("uid")
        email = data.get("email")
        if not uid or not email:
            return jsonify({"error": "缺少 UID 或 Email"}), 400

        subject = "帳戶綁定確認"
        body_str = "您的 Line 已綁定此 Email！"
        email_response = trigger_email(f"{IRIS_DS_SERVER_URL}/send-mail", email, subject, body_str)
        if "error" in email_response:
            return jsonify({"error": "Email 發送失敗"}), 500
        return jsonify({"message": "綁定成功，請檢查您的 Email"}), 200
    except Exception:
        return jsonify({"error": "伺服器錯誤"}), 500
