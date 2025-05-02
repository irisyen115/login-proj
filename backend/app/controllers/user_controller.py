from flask import Blueprint, jsonify, request
from services.user_service import fetch_users_data

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["GET"])
def get_users():
    user_id = request.cookies.get("user_id")
    if not user_id:
        return jsonify({"error": "未授權"}), 401

    user = fetch_users_data(user_id)
    if user and "error" in user:
        return jsonify(user), 404

    return jsonify(user)
