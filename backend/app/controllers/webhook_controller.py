from flask import Blueprint, request, jsonify
from services.webhook_service import handle_webhook_event, handle_bind_email

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    return handle_webhook_event(request.json)

@webhook_bp.route("/bind-email", methods=["POST"])
def bind_email():
    return handle_bind_email(request.json)
