from flask import Blueprint, request, jsonify
from services.reset_service import reset_user_password

reset_bp = Blueprint("reset", __name__)

@reset_bp.route("/reset-password/<password_verify_code>", methods=["POST"])
def reset_password(password_verify_code):
    data = request.json
    new_password = data.get("password")
    if not new_password:
        return jsonify({"message": "請提供新密碼"}), 400

    result, error = reset_user_password(password_verify_code, new_password)
    if error:
        return jsonify({"message": error}), 400

    return jsonify({"message": result}), 200