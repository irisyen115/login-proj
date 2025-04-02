from datetime import datetime
from database import db
from models import PasswordVerify

def reset_user_password(password_verify_code, new_password):
    try:
        password_verify = PasswordVerify.query.filter_by(password_verify_code=password_verify_code).first()
        if not password_verify:
            return None, "驗證密鑰不存在"

        user = password_verify.user
        if datetime.now() > password_verify.valid_until:
            return None, "驗證密鑰已過期"

        user.set_password(new_password)
        db.session.commit()

        return "密碼重設成功，請重新登入", None
    except Exception as e:
        return None, f"發生錯誤: {str(e)}"