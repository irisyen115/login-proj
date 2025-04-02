import os
from flask import Flask, g, request
from config import Config
from database import db, init_db
from controllers.auth_controller import auth_bp
from controllers.webhook_controller import webhook_bp
from controllers.user_controller import user_bp
from controllers.file_controller import file_bp
from controllers.email_controller import email_bp
from controllers.reset_controller import reset_bp

app = Flask(__name__)
app.config.from_object(Config)

init_db(app)

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

@app.before_request
def get_user_id():
    user_id = request.cookies.get("user_id", "").strip()
    g.user_id = int(user_id) if user_id.isdigit() else None

app.register_blueprint(auth_bp)
app.register_blueprint(webhook_bp)
app.register_blueprint(user_bp)
app.register_blueprint(file_bp)
app.register_blueprint(email_bp)
app.register_blueprint(reset_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
