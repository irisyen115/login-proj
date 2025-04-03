from flask import Blueprint, jsonify, g
from services.user_service import fetch_users_data

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["GET"])
def get_users():
    if not g.user_id:
        return jsonify({"error": "未授權"}), 401

    user = fetch_users_data(g.user_id)
    if user and "error" in user:
        return jsonify(user), 404

    return jsonify(user)
