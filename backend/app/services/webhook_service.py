import os
import requests
from dotenv import load_dotenv
from flask import jsonify
from utils.email_utils import trigger_email

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")
LINE_REPLY_URL = os.getenv("LINE_REPLY_URL")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

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
                    login_url = f"{SERVER_URL}/Line-login?uid={uid}"
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
        email_response = trigger_email(f"{SERVER_URL}/send-mail", email, subject, body_str)
        if "error" in email_response:
            return jsonify({"error": "Email 發送失敗"}), 500
        return jsonify({"message": "綁定成功，請檢查您的 Email"}), 200
    except Exception:
        return jsonify({"error": "伺服器錯誤"}), 500
