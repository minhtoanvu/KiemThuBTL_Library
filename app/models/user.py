from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='User')  # Admin hoặc User
    is_active = db.Column(db.Boolean, default=True)  # Check khóa tài khoản (TC28)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, username, password, role='User'):
        self.username = username
        self.password = password
        self.role = role
        self.is_deleted = False