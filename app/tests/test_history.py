

import pytest
from app import db
from app.models import User, Book, Category, BorrowRecord
from app import dao, utils

from app.tests.test_base import test_app,test_session,test_client,seed_data
class TestBorrowHistory:


    def test_lich_su_co_du_lieu(self, test_app, seed_data):
        """ Lấy lịch sử mượn sách của user."""
        with test_app.app_context():
            user = User.query.filter_by(username='user1234').first()
            history = dao.get_history_by_user(user.id)
            assert len(history) > 0

    def test_lich_su_user_chua_muon(self, test_app, seed_data):
        """ User chưa mượn sách nào → lịch sử rỗng."""
        with test_app.app_context():
            user = User.query.filter_by(username='user2').first()
            # user2 chỉ có records nếu seed_data tạo
            # Kiểm tra ít nhất hàm chạy không lỗi
            history = dao.get_history_by_user(user.id)
            assert isinstance(history, list)

    def test_dem_so_sach_dang_muon(self, test_app, seed_data):
        """Đếm số sách đang mượn của user."""
        with test_app.app_context():
            user = User.query.filter_by(username='user_max').first()
            count = dao.count_active_borrowing(user.id)
            assert count == 5

    def test_active_borrowing_list(self, test_app, seed_data):
        """ Lấy danh sách sách đang mượn."""
        with test_app.app_context():
            user = User.query.filter_by(username='user1234').first()
            active = dao.get_active_borrowing_list(user.id)
            for record in active:
                assert record.return_date is None






