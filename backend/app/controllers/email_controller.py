from flask import Blueprint, request, jsonify
from services.email_service import send_authentication_email, send_email_verification, send_email_code

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
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 200

@email_bp.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.json
    username = data.get("username")
    verification_code = data.get("verificationCode")
    if not username:
        return jsonify({"message": "請輸入用戶名"}), 404
    if not verification_code:
        return jsonify({"message": "請輸入信箱驗證碼"}), 404
    result = send_email_code(username, verification_code)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)
