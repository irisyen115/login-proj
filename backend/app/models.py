from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import json
from sqlalchemy import Enum

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.Text, nullable=True)
    role = db.Column(Enum("user", "admin", "guest", name="role_enum"), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=None)
    login_count = db.Column(db.Integer, default=0)
    profile_image = db.Column(db.String(255), nullable=True)
    picture_name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(254), nullable=True)

    password_verification = db.relationship('PasswordVerify', back_populates='user', cascade="all, delete-orphan")
    email_verifications = db.relationship('EmailVerify', back_populates='user', cascade="all, delete-orphan")

    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email
        if password:
            self.set_password(password)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        self.login_count += 1

    def to_dict(self):
        return {
            col.name: (getattr(self, col.name).isoformat() if isinstance(getattr(self, col.name), datetime) else getattr(self, col.name))
            for col in self.__table__.columns
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_data):
        data_dict = json.loads(json_data)
        u = User(data_dict['username'], data_dict['email'], data_dict.get('password'))
        u.role = data_dict.get('role')
        u.created_at = datetime.fromisoformat(data_dict['created_at'])
        u.updated_at = datetime.fromisoformat(data_dict['updated_at'])
        u.last_login = datetime.fromisoformat(data_dict['last_login'])
        u.login_count = data_dict.get('login_count')
        u.profile_image = data_dict.get('profile_image')
        u.picture_name = data_dict.get('picture_name')
        u.password_hash = data_dict.get('password_hash')
        return u

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
