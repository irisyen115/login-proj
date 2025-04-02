import os
from flask import current_app
from models import db, User

def save_user_avatar(user_id, file_storage):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filename = f"{user_id}.jpg"
    filepath = os.path.join(upload_folder, filename)

    file_storage.save(filepath)

    user = User.query.get(user_id)
    if user:
        user.profile_image = filepath
        user.picture_name = filename
        db.session.commit()
    return filepath
