import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from models import db, init_db, User
import random
import string
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app)

@app.route('/status')
def status():
    return jsonify({"status": "ok"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password or not email:
        return jsonify({"error": "請提供帳號、密碼和電子郵件"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "帳號已存在"}), 400

    new_user = User(
        username=username,
        email=email,
        key_certificate=''.join(random.choices(string.ascii_letters + string.digits, k=30))
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    response = make_response(jsonify({"message": "註冊成功", "user": username, "role": "user"}))
    response.set_cookie("user_session", username, httponly=True, secure=True, samesite="Strict")
    response.set_cookie("role", "user", httponly=True, secure=True, samesite="Strict")

    return response, 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "請提供帳號和密碼"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "帳號或密碼錯誤"}), 401

    user.last_login = datetime.now()
    user.login_count += 1
    db.session.commit()

    response = make_response(jsonify({
        "message": "登入成功",
        "user": username,
        "role": user.role,
        "last_login": user.last_login,
        "login_count": user.login_count
    }))
    response.set_cookie("user_session", username, httponly=True, secure=True, samesite="Strict")
    response.set_cookie("role", user.role, httponly=True, secure=True, samesite="Strict")
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
