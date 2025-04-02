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
