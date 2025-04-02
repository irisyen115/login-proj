from flask import Blueprint, jsonify, g
from models import User
user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["GET"])
def get_users():
    if not g.get("user_id"):
        return jsonify({"error": "未授權"}), 401

    from services.user_service import get_user_by_id
    user = get_user_by_id(g.user_id)
    if not user:
        return jsonify({"error": "使用者不存在"}), 404

    if user.role == "admin":
        users = User.query.with_entities(User.id, User.username, User.last_login, User.login_count, User.role).all()
        users_data = [user_row._asdict() for user_row in users]
        return jsonify(users_data)
    elif user.role == "user":
        user_list = [user]
        users_data = [user_col.to_dict() for user_col in user_list]
        return jsonify(users_data)
