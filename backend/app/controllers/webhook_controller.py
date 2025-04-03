from flask import Blueprint, request, jsonify
from services.webhook_service import handle_webhook_event, bind_email_service

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    return handle_webhook_event(request.json)

@webhook_bp.route("/bind-email", methods=["POST"])
def bind_email():
    try:
        data = request.json
        response = bind_email_service(data)

        return response
    except Exception as e:
        return jsonify({"error": f"伺服器錯誤: {str(e)}"}), 500

