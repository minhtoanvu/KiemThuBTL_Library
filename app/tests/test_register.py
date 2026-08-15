import pytest
from app.models import User, Book, Category, BorrowRecord
from app import dao, utils
from app.tests.test_base import test_app,test_session,test_client,seed_data
class TestRegister:

    def test_dang_ky_thanh_cong(self, test_app, seed_data):

        with test_app.app_context():
            user = dao.register_user('newuser', 'Pass@123')
            actually = User.query.filter_by(username='newuser').first()
            assert actually is not None
            assert actually.username == 'newuser'
    def test_dang_ky_username_da_ton_tai(self, test_app, seed_data):
        with test_app.app_context():
            with pytest.raises(ValueError):
                dao.register_user('user1234', 'Pass@123')

    def test_dang_ky_username_qua_ngan(self, test_app, seed_data):

        with test_app.app_context():
            with pytest.raises(ValueError):
                dao.register_user('ab', 'Pass@123')

    def test_dang_ky_mat_khau_qua_ngan(self, test_app, seed_data):

        with test_app.app_context():
            with pytest.raises(ValueError):
                dao.register_user('newuser2', 'ab1')

    def test_dang_ky_mat_khau_khong_co_chu(self, test_app, seed_data):

        with test_app.app_context():
            with pytest.raises(ValueError):
                dao.register_user('newuser3', '123456')

    def test_dang_ky_mat_khau_khong_co_so(self, test_app, seed_data):

        with test_app.app_context():
            with pytest.raises(ValueError):
                dao.register_user('newuser4', 'abcdef')

    def test_check_username_exists(self, test_app, seed_data):

        with test_app.app_context():
            assert dao.check_username_exists('user1234') is True
            assert dao.check_username_exists('khong_ton_tai') is False

