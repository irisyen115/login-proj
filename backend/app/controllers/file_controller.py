from flask import Blueprint, request, jsonify, send_from_directory, g
from services.file_service import save_user_avatar, get_user_image_service
from services.user_service import get_user_by_id
from config import Config

file_bp = Blueprint("file", __name__)

@file_bp.route('/upload-avatar', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "請提供照片"}), 400

    file = request.files['file']
    if not file:
        return jsonify({"error": "請提供照片"}), 400

    if not g.user_id:
        return jsonify({"error": "未授權"}), 401

    try:
        avatar_url = save_user_avatar(g.user_id, file)
    except Exception as e:
        return jsonify({"error": f"照片上傳錯誤: {str(e)}"}), 500

    return jsonify({"message": "照片上傳成功", "avatar_url": avatar_url})

@file_bp.route('/get_user_image', methods=['GET'])
def get_user_image():
    if not g.user_id:
        return jsonify({"error": "未授權"}), 401

    user = get_user_by_id(g.user_id)
    if not user:
        return jsonify({"error": "用戶未找到"}), 404

    picture_name = get_user_image_service(user)

    if picture_name:
        try:
            return send_from_directory(Config.UPLOAD_FOLDER, picture_name, as_attachment=True)
        except Exception as e:
            return jsonify({"error": f"檔案讀取錯誤: {str(e)}"}), 500

    return jsonify({"error": "無圖片可顯示"}), 404