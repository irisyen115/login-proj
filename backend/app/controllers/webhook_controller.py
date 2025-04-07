from flask import Blueprint, request, jsonify
from services.webhook_service import handle_webhook_event
from services.auth_service import bind_line_uid_to_user_email, identify_google_user_by_token

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    return handle_webhook_event(request.json)

@webhook_bp.route("/bind-google-email", methods=["POST"])
def bind_google_email():
    try:
        data = request.get_json()
        if not data:
            return jsonify({{"error": "no data"}}), 400
        for key in ('google_token', 'uid'):
            if key not in data:
                return jsonify({"error": f"缺少必要的資料({key})"}), 400
        line_uid = data.get("uid")
        user = identify_google_user_by_token(data)

        return bind_line_uid_to_user_email(line_uid, user)
    except Exception as e:
        return jsonify({"error": f"伺服器錯誤: {str(e)}"}), 500

@webhook_bp.route("/bind-email", methods=["POST"])
def bind_email():
    try:
        data = request.get_json()
        if not data:
            return jsonify({{"error": "no data"}}), 400
        for key in ('username', 'password', 'uid'):
            if key not in data:
                return jsonify({"error": f"缺少必要的資料({key})"}), 400
        line_uid = data.get("uid")
        user = identify_google_user_by_token(data)

        return bind_line_uid_to_user_email(line_uid, user)
    except Exception as e:
        return jsonify({"error": f"伺服器錯誤: {str(e)}"}), 500

