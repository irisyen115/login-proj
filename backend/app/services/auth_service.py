import json
import random
import string
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from models import db, User
from redis import StrictRedis
from config import Config

redis_client = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

def generate_reset_token(length=30):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def update_login_cache_state(uid):
    try:
        cached = redis_client.get(f"user:{uid}")
        if cached:
            user_data = json.loads(cached)
            user_data['last_login'] = datetime.utcnow().isoformat()
            user_data['login_count'] += 1
            redis_client.setex(f"user:{uid}", 3600, json.dumps(user_data))
        else:
            user = User.query.get(uid)
            if user:
                redis_client.setex(f"user:{uid}", 3600, user.to_json())
    except Exception as e:
        print(e)

def authenticate_google_user(id_token_str, client_id):
    try:
        decoded = id_token.verify_oauth2_token(id_token_str, Request(), client_id)
        email = decoded.get('email')
        if not email:
            return None, "無法取得使用者的 email"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=decoded.get('name'), email=email)
            db.session.add(user)
        user.last_login = datetime.utcnow()
        user.login_count += 1
        db.session.commit()
        update_login_cache_state(user.id)
        return user, None
    except Exception as e:
        return None, str(e)
