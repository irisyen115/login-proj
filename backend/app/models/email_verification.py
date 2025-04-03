from models.database import db
from datetime import datetime

class EmailVerify(db.Model):
    __tablename__ = "email_verification"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime, nullable=False)
    email_verify_code = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    user = db.relationship('User', back_populates='email_verification')
