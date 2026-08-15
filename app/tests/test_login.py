import pytest
from app import db
from app.models import User, Book, Category, BorrowRecord
from app import dao, utils
from app.tests.test_base import test_app,test_session,test_client,seed_data
class TestLogin:


    def test_login_thanh_cong_user(self, test_app, seed_data):

        with test_app.app_context():
            user = dao.auth_user('user1234', 'user1234')
            assert user is not None
            assert user.username == 'user1234'
            assert user.role == 'User'

    def test_login_thanh_cong_admin(self, test_app, seed_data):

        with test_app.app_context():
            admin = dao.auth_user('admin', 'admin123')
            assert admin is not None
            assert admin.role == 'Admin'

    def test_login_sai_mat_khau(self, test_app, seed_data):

        with test_app.app_context():
            user = dao.auth_user('user1234', 'wrong_password')
            assert user is None

    def test_login_username_khong_ton_tai(self, test_app, seed_data):

        with test_app.app_context():
            user = dao.auth_user('khong_ton_tai', 'password')
            assert user is None

    def test_login_tai_khoan_bi_khoa(self, test_app, seed_data):

        with test_app.app_context():
            user = dao.auth_user('inactive_user', 'user@1234')
            assert user is not None
            assert user.is_active is False

    def test_login_username_rong(self, test_app, seed_data):

        with test_app.app_context():
            user = dao.auth_user('', 'password')
            assert user is None

    def test_login_user_da_bi_xoa(self, test_app, seed_data):

        with test_app.app_context():
            # Soft-delete user2
            u = User.query.filter_by(username='user2').first()
            u.is_deleted = True
            u.username = 'user2_deleted_99'
            db.session.commit()

            result = dao.auth_user('user2', 'user@1234')
            assert result is None


