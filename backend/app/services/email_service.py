import random
import string
from datetime import datetime, timedelta
from models import db, PasswordVerify, EmailVerify, User
from sqlalchemy import desc
import requests

def generate_reset_token(length=30):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def send_authentication_email(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"message": "用戶不存在"}
    if not user.email:
        return {"message": "用戶未綁定 Email，請先綁定"}

    password_verify = PasswordVerify.query.filter_by(user_id=user.id).order_by(desc(PasswordVerify.valid_until)).first()
    current_time = datetime.utcnow()
    if password_verify and current_time <= password_verify.valid_until:
        return {"message": "驗證碼已發送，請前往電子信箱驗收，勿重複點取"}
    else:
        new_password_verify = PasswordVerify(
            password_verify_code=generate_reset_token(30),
            valid_until=datetime.utcnow() + timedelta(minutes=15),
            user_id=user.id
        )
        db.session.add(new_password_verify)
        db.session.commit()
        return {"message": "驗證信已發送，請重新設置"}

def send_email_verification(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"message": "用戶不存在"}
    if not user.email:
        return {"message": "用戶未綁定 Email，若需綁定請洽系統服務"}

    email_verify = EmailVerify.query.filter_by(user_id=user.id).order_by(desc(EmailVerify.valid_until)).first()
    current_time = datetime.utcnow()
    if email_verify and current_time <= email_verify.valid_until:
        return {"message": "驗證碼已發送，請勿重複點取"}
    else:
        new_email_verify = EmailVerify(
            email_verify_code=generate_reset_token(6),
            valid_until=datetime.utcnow() + timedelta(minutes=15),
            user_id=user.id
        )
        db.session.add(new_email_verify)
        db.session.commit()
        return {"email": user.email, "message": "驗證碼已發送，請檢查電子郵件"}

def trigger_email(url, recipient, subject, body_str):
    data = {
        "recipient": recipient,
        "subject": subject,
        "body": body_str
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send email, status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}