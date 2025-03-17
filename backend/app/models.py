from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=None)
    login_count = db.Column(db.Integer, default=0)
    profile_image = db.Column(db.String(255), nullable=True)
    picture_name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(30), nullable=True)
    key_certificate = db.Column(db.String(30), unique=True, nullable=True)
    id_authentication = db.Column(db.Boolean, default=False)
    email_verify = db.Column(db.String(255), nullable=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        self.login_count += 1

class Certificate(db.Model):
    __tablename__ = "certificate"

    id = db.Column(db.Integer, primary_key=True)
    valid_until = db.Column(db.DateTime, nullable=False)
    key_certificate = db.Column(db.String(50), nullable=True)
    email_verify = db.Column(db.String(50), nullable=True)

    @classmethod
    def add_certificate(cls, key_certificate=None, email_verify=None):
        if not key_certificate and not email_verify:
            raise ValueError("必須至少提供 key_certificate 或 email_verify")

        new_certificate = cls(
            key_certificate=key_certificate,
            email_verify=email_verify,
            valid_until=datetime.utcnow() + timedelta(minutes=15)
        )
        db.session.add(new_certificate)
        db.session.commit()
        return new_certificate

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
