from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

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

    password_verification = db.relationship('PasswordVerify', back_populates='user', cascade="all, delete-orphan")
    email_verifications = db.relationship('EmailVerify', back_populates='user', cascade="all, delete-orphan")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        self.login_count += 1

class PasswordVerify(db.Model):
    __tablename__ = "password_verification"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime, nullable=False)
    password_verify_code = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)  

    user = db.relationship('User', back_populates='password_verification')

class EmailVerify(db.Model):
    __tablename__ = "email_verification"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime, nullable=False)
    email_verify_code = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)  

    user = db.relationship('User', back_populates='email_verifications')

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
