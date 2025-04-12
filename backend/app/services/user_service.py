from models.users import User
from models.database import db
from config import Config
import redis
from services.auth_service import update_login_cache_state
from datetime import datetime

redis_client = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

def register_user(data):
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password or not email:
        return {"error": "請提供帳號、密碼和電子郵件"}

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return {"error": "帳號已存在"}

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return {"user": new_user, "role": "user"}

def login_user(data):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "請提供帳號和密碼"}

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return {"error": "帳號或密碼錯誤"}

    update_login_cache_state(user.id)
    user.update_last_login()
    db.session.commit()

    return {
        "user_id": user.id,
        "role": user.role,
        "last_login": user.last_login,
        "login_count": user.login_count
    }

def fetch_users_data(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return {"error": "使用者不存在"}

    if user.role == "admin":
        users = User.query.with_entities(User.id, User.username, User.last_login, User.login_count, User.role).all()
        users_data = [user_row._asdict() for user_row in users]
        return users_data
    elif user.role == "user":
        user_list = [user]
        users_data = []

        for user_col in user_list:
            user_dict = user_col.to_dict()
            if isinstance(user_dict.get('last_login'), str):
                user_dict['last_login'] = datetime.fromisoformat(user_dict['last_login'])
            users_data.append(user_dict)
    return {"error": "未知的角色"}

def user_key(uid):
    return f"user:{uid}"

def get_user_by_id(uid):
    try:
        if not uid:
            return None
        cached_user_data = redis_client.get(user_key(uid))
        if cached_user_data:
            return User.from_json(cached_user_data)
        user = User.query.filter_by(id=int(uid)).first()
        if user:
            redis_client.setex(user_key(uid), 3600, user.to_json())
            return user
        return None
    except Exception as e:
        return None
