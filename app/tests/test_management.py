import pytest
from app import db
from app.models import User, Book, Category, BorrowRecord
from app import dao, utils
from app.tests.test_base import test_app,test_session,test_client,seed_data
class TestUserManagement:


    def test_get_user_by_id(self, test_app, seed_data):
        """ Lấy user theo ID."""
        with test_app.app_context():
            user = dao.get_user_by_id(1)
            assert user is not None

    def test_get_user_khong_ton_tai(self, test_app, seed_data):
        """ Lấy user với ID không tồn tại."""
        with test_app.app_context():
            user = dao.get_user_by_id(9999)
            assert user is None

    def test_soft_delete_user(self, test_app, seed_data):
        """ Soft-delete user."""
        with test_app.app_context():
            user = User.query.filter_by(username='user2').first()
            user.is_deleted = True
            user.username = 'user2_deleted_' + str(user.id)
            db.session.commit()

            # Kiểm tra không thể login
            result = dao.auth_user('user2', 'user@1234')
            assert result is None

    def test_khoa_tai_khoan(self, test_app, seed_data):
        """ Khóa tài khoản user."""
        with test_app.app_context():
            user = User.query.filter_by(username='user2').first()
            user.is_active = False
            db.session.commit()

            updated = User.query.filter_by(username='user2').first()
            assert updated.is_active is False
