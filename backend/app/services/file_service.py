import os
from models import db, User
from config import Config

def save_user_avatar(user_id, file_storage):
    upload_folder = Config.UPLOAD_FOLDER
    filename = f"{user_id}.jpg"
    filepath = os.path.join(upload_folder, filename)

    file_storage.save(filepath)

    user = User.query.get(user_id)
    if user:
        user.profile_image = filepath
        user.picture_name = filename
        db.session.commit()
    return filepath

def get_user_image_service(user):
    if user.profile_image:
        image_path = os.path.join(Config.UPLOAD_FOLDER, user.picture_name)
        if os.path.exists(image_path):
            return user.picture_name
    return None