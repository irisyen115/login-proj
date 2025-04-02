from models import User
from database import db
from datetime import datetime
from app import app

def register_user(data):
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password or not email:
        return {"error": "Please provide username, password, and email"}

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {"error": "User already exists"}

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return {"message": "Registration successful", "user": username, "role": "user"}

def login_user(data):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "Please provide username and password"}

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return {"error": "Invalid username or password"}

    user.last_login = datetime.now()
    user.login_count += 1
    db.session.commit()

    return {
        "message": "Login successful",
        "role": user.role,
        "last_login": user.last_login,
        "login_count": user.login_count
    }

def get_user_by_id(uid):
    from app import redis_client
    try:
        if not uid:
            return None

        cached_user_data = redis_client.get(f"user:{uid}")
        if cached_user_data:
            return User.from_json(cached_user_data)

        user = User.query.filter_by(id=int(uid)).first()
        if user:
            redis_client.setex(f"user:{uid}", 3600, user.to_json())
            return user

        return None

    except Exception as e:
        app.logger.error(f"Error while getting user {uid}: {e}")
        return None
