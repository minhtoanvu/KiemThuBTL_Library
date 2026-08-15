from app.models.user import User
from app import db
import hashlib
from sqlalchemy.exc import IntegrityError
import re
def get_user_by_id(user_id):
    return User.query.get(user_id)

def auth_user(username, password):
    passwordHash = hashlib.md5(
        password.strip().encode('utf-8')
    ).hexdigest()

    return User.query.filter(User.username == username.strip(),
                             User.password == passwordHash,
                             User.is_deleted == False).first()

def check_username_exists(username):
    return User.query.filter(User.username == username.strip(), User.is_deleted == False).first() is not None

def register_user(username, password):
    if len(username) < 3:
        raise ValueError("Username phai toi thieu la 3 ky tu")
    if len(password) < 6:
        raise ValueError("Mat khau phai toi thieu la 6 ky tu")
    if not re.search(r"[a-zA-Z]", password):
        raise ValueError("Password phai co ky tu")
    if not re.search(r"[0-9]", password):
        raise ValueError("Mat khau phai co so")
    if User.query.filter(User.username == username, User.is_deleted == False).first():
        raise ValueError(f"{username} da ton tai")

    password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
    u = User(username=username.strip(), password=password)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception("Username da ton tai!")