import os
import json
import random
import string
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from models.database import db
from models.users import User
from redis import StrictRedis
from config import Config
import requests

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

def authenticate_google_user(id_token_str):
    try:
        decoded = id_token.verify_oauth2_token(id_token_str, Request(), Config.GOOGLE_CLIENT_ID)

        email = decoded.get('email')
        picture = decoded.get('picture')
        if not email:
            return None, "無法取得使用者的 email"

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=decoded.get('name'), email=email)
            db.session.add(user)

        if picture:
            image_data = requests.get(picture).content
            filename = f"{user.id}.jpg"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

            with open(filepath, 'wb') as f:
                f.write(image_data)

            user.profile_image = filepath
            user.picture_name = filename
            db.session.add(user)

        update_login_cache_state(user.id)
        user.update_last_login()
        db.session.commit()

        return user, None
    except Exception as e:
        return None, str(e)