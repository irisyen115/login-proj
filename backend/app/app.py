import os
from flask import Flask, g, session, redirect, url_for, request
from config import Config
from models.database import db, init_db
from controllers.auth_controller import auth_bp
from controllers.webhook_controller import webhook_bp
from controllers.user_controller import user_bp
from controllers.file_controller import file_bp
from controllers.email_controller import email_bp
from controllers.reset_controller import reset_bp
from flask_cors import CORS
from datetime import timedelta
from services.user_service import redis_client
import logging

app = Flask(__name__)
app.config.from_object(Config)
app.permanent_session_lifetime = timedelta(minutes=30)

CORS(app, supports_credentials=True, origins=[Config.IRIS_DS_SERVER_URL])
init_db(app)

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

@app.before_request
def get_user_id():
    open_paths = [
        '/auth/google/callback',
        '/login',
        '/register',
        '/webhook',
        '/bind-email',
        '/bind-google-email',
    ]

    if request.path in open_paths:
        return

    session_id = session.get("session_id")
    logging.error(f"Session ID: {session_id}")

    if session_id:
        user_id = redis_client.get(session_id)
        logging.error(f"User ID from Redis: {user_id}")

        if user_id:
            g.user_id = int(user_id)
            redis_client.expire(session_id, 1800)
            return

        else:
            logging.error("Invalid session ID, clearing session.")
            clear_session(session_id)
            return redirect(url_for('auth.login'))
    else:
        logging.error("Session ID is None, user is not authenticated.")
        g.user_id = None
        return redirect(url_for('auth.login'))

def clear_session(session_id):
    g.user_id = None
    redis_client.delete(session_id)
    session.pop('session_id', None)
    logging.error("Session ID cleared and user logged out.")

app.register_blueprint(auth_bp)
app.register_blueprint(webhook_bp)
app.register_blueprint(user_bp)
app.register_blueprint(file_bp)
app.register_blueprint(email_bp)
app.register_blueprint(reset_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
