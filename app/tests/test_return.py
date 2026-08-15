import pytest
from app import db
from app.models import User, Book, Category, BorrowRecord
from app import dao, utils
from app.tests.test_base import test_app,test_session,test_client,seed_data
from datetime import date, timedelta
class TestReturn:

    def test_validate_return_thanh_cong(self, test_app, seed_data):
        """ Validate trả sách thành công."""
        with test_app.app_context():
            user = User.query.filter_by(username='user1234').first()
            record = BorrowRecord.query.filter_by(
                user_id=user.id, status='BORROWED'
            ).first()
            valid, msg = utils.validate_return(user, record)
            assert valid is True

    def test_validate_return_khong_co_record(self, test_app, seed_data):
        """ Không tìm thấy phiếu mượn."""
        with test_app.app_context():
            user = User.query.filter_by(username='user1234').first()
            valid, msg = utils.validate_return(user, None)
            assert valid is False
            assert 'không tìm thấy' in msg.lower()

    def test_validate_return_sach_nguoi_khac(self, test_app, seed_data):
        """ Trả sách người khác đã mượn."""
        with test_app.app_context():
            user1 = User.query.filter_by(username='user1234').first()
            user2 = User.query.filter_by(username='user2').first()
            record = BorrowRecord.query.filter_by(
                user_id=user1.id, status='BORROWED'
            ).first()
            # user2 cố trả sách user1 đã mượn
            valid, msg = utils.validate_return(user2, record)
            assert valid is False
            assert 'người khác' in msg.lower()

    def test_return_status_chuyen_returning(self, test_app, seed_data):
        """ Chuyển status thành RETURNING khi user yêu cầu trả."""
        with test_app.app_context():
            user = User.query.filter_by(username='user1234').first()
            record = BorrowRecord.query.filter_by(
                user_id=user.id, status='BORROWED'
            ).first()
            record.status = 'RETURNING'
            record.return_date = date.today()
            record.fine = utils.calculate_fine(record.due_date, record.return_date)
            db.session.commit()

            updated = BorrowRecord.query.get(record.id)
            assert updated.status == 'RETURNING'

