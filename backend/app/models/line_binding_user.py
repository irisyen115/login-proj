from models.database import db
from datetime import datetime

class LineBindingUser(db.Model):
    __tablename__ = "line_binding_user"

    line_id = db.Column(db.String(120), primary_key=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='line_binding_user')
