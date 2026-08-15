
import os
import hashlib
from selenium import webdriver
import pytest
from flask import Flask
from selenium import webdriver
from datetime import date, timedelta

from app import db
from app.models import User, Book, Category, BorrowRecord


def md5(text: str) -> str:
    return hashlib.md5(text.strip().encode('utf-8')).hexdigest()


# ---------- APP & CLIENT ----------

def create_test_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["PAGE_SIZE"] = 2
    app.config["TESTING"] = True
    app.secret_key = "test-secret-key"
    db.init_app(app)
    return app


@pytest.fixture
def test_app():
    app = create_test_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def test_session(test_app: Flask):
    yield db.session
    db.session.rollback()



@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--incognito")

    if os.getenv("GITHUB_ACTIONS"):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


@pytest.fixture
def seed_data(test_session):
    cat_names = [
        'Lập trình', 'AI', 'Database', 'Web', 'Frontend',
        'Backend', 'Software', 'Data Science', 'DevOps',
        'System', 'Cloud', 'Security', 'Technology',
        'Game', 'Mobile', 'Design'
    ]
    categories = []
    for name in cat_names:
        c = Category(name)
        test_session.add(c)
        categories.append(c)
    test_session.commit()

    admin = User('admin', md5('admin123'), 'Admin')
    user1 = User('user1234', md5('user1234'), 'User')
    user2 = User('user2', md5('user@1234'), 'User')
    inactive = User('inactive_user', md5('user@1234'), 'User')
    inactive.is_active = False
    user_max = User('user_max', md5('user@1234'), 'User')

    users = [admin, user1, user2, inactive, user_max]
    test_session.add_all(users)
    test_session.commit()

    books = [
        Book('Lập trình C#', 'Minh', 1, 10),
        Book('Python căn bản', 'AI Guide', 1, 1),
        Book('Java nâng cao', 'Tech Master', 1, 5),
        Book('Machine Learning cơ bản', 'AI Lab', 2, 8),
        Book('Deep Learning thực chiến', 'OpenAI VN', 2, 6),
        Book('SQL Server toàn tập', 'DB Team', 3, 7),
        Book('Flask Web Development', 'Miguel', 4, 4),
        Book('Django cho người mới', 'Python VN', 4, 9),
        Book('HTML CSS JavaScript', 'Frontend Dev', 5, 12),
        Book('AI', 'UI Team', 5, 10),
        Book('Sách hết', 'Test Author', 1, 0),  # Sách hết kho
    ]
    test_session.add_all(books)
    test_session.commit()

 
    today = date.today()

    # user1234: 1 sách đang mượn
    r1 = BorrowRecord(
        user_id=user1.id,
        book_id=books[3].id,  # Machine Learning cơ bản
        borrow_date=today - timedelta(days=3),
        due_date=today + timedelta(days=11),
    )
    r1.status = 'BORROWED'

    # user1234: 1 sách quá hạn
    r2 = BorrowRecord(
        user_id=user1.id,
        book_id=books[5].id,  # SQL Server
        borrow_date=today - timedelta(days=20),
        due_date=today - timedelta(days=6),
    )
    r2.status = 'BORROWED'

    # user1234: 1 sách đã trả
    r3 = BorrowRecord(
        user_id=user1.id,
        book_id=books[0].id,  # Lập trình C#
        borrow_date=today - timedelta(days=30),
        due_date=today - timedelta(days=16),
        return_date=today - timedelta(days=18),
    )
    r3.status = 'RETURNED'
    r3.fine = 0

    # user_max: 5 sách đang mượn (đạt giới hạn)
    max_records = []
    for i in range(5):
        rm = BorrowRecord(
            user_id=user_max.id,
            book_id=books[i].id,
            borrow_date=today - timedelta(days=i + 1),
            due_date=today + timedelta(days=14 - i),
        )
        rm.status = 'BORROWED'
        max_records.append(rm)

    all_records = [r1, r2, r3] + max_records
    test_session.add_all(all_records)
    test_session.commit()

    return {
        'admin': admin,
        'user1': user1,
        'user2': user2,
        'inactive': inactive,
        'user_max': user_max,
        'categories': categories,
        'books': books,
        'records': all_records,
    }

@pytest.fixture
def driver():

    options = webdriver.ChromeOptions()

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False
    }

    options.add_experimental_option("prefs", prefs)

    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--incognito")

    # GitHub Actions / Linux CI
    if os.getenv("GITHUB_ACTIONS"):

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    driver.maximize_window()

    driver.implicitly_wait(10)

    yield driver

    driver.quit()