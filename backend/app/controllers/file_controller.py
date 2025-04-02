import os
from flask import Blueprint, request, jsonify, send_from_directory, g
from services.file_service import save_user_avatar
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
        filepath = save_user_avatar(g.user_id, file)
    except Exception as e:
        return jsonify({"error": f"照片上傳錯誤: {str(e)}"}), 500

    return jsonify({"message": "照片上傳成功", "file_path": filepath})

@file_bp.route('/get_user_image', methods=['GET'])
def get_user_image():
    if not g.user_id:
        return jsonify({"error": "未授權"}), 401

    from services.user_service import get_user_by_id
    user = get_user_by_id(g.user_id)
    if not user:
        return jsonify({"error": "用戶未找到"}), 404

    if user.profile_image:
        image_path = Config.UPLOAD_FOLDER
        if os.path.exists(image_path):
            try:
                return send_from_directory(image_path, user.picture_name, as_attachment=True)
            except Exception as e:
                return jsonify({"error": f"檔案讀取錯誤: {str(e)}"}), 500
        else:
            return jsonify({"error": "圖片檔案不存在"}), 404

    return jsonify({"error": "無圖片可顯示"}), 404