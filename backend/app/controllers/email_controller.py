from flask import Blueprint, request, jsonify
from services.email_service import send_authentication_email, send_email_verification

email_bp = Blueprint("email", __name__)

@email_bp.route("/send-authentication", methods=["POST"])
def send_authentication():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"message": "請輸入用戶名"}), 404
    result = send_authentication_email(username)
    return jsonify(result)

@email_bp.route("/verify-email", methods=["POST"])
def verify_email():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"message": "請輸入用戶名"}), 404
    result = send_email_verification(username)
    return jsonify(result)

@email_bp.route("/reset-password/<password_verify_code>", methods=["POST"])
def reset_password(password_verify_code):
    from models import PasswordVerify, db
    from datetime import datetime
    try:
        password_verify = PasswordVerify.query.filter_by(password_verify_code=password_verify_code).first()
        if not password_verify:
            return jsonify({"message": "驗證密鑰不存在"}), 404
        user = password_verify.user
        if datetime.now() > password_verify.valid_until:
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
