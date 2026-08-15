import pytest
from app import db
from app.models import User, Book, Category, BorrowRecord
from app import dao, utils
from datetime import date, timedelta
from app.tests.test_base import test_app,test_session,test_client,seed_data
class TestBorrowEligibility:


    def test_muon_thanh_cong(self, test_app, seed_data):
        with test_app.app_context():
            user = User.query.filter_by(username='user2').first()
            book = Book.query.filter(Book.quantity > 0).first()
            count = dao.count_active_borrowing(user.id)
            eligible, msg = utils.check_borrow_eligibility(user, book, count)
            assert eligible is True

    def test_muon_khi_het_sach(self, test_app, seed_data):

        with test_app.app_context():
            user = User.query.filter_by(username='user2').first()

            book = Book.query.filter_by(title='Sách hết').first()
            count = dao.count_active_borrowing(user.id)
            eligible, msg = utils.check_borrow_eligibility(user, book, count)
            assert eligible is False
            assert 'hết' in msg.lower()

    def test_muon_khi_da_dat_gioi_han_5(self, test_app, seed_data):

        with test_app.app_context():
            user = User.query.filter_by(username='user_max').first()
            book = Book.query.filter(Book.quantity > 0).first()
            count = dao.count_active_borrowing(user.id)
            assert count >= 5
            eligible, msg = utils.check_borrow_eligibility(user, book, count)
            assert eligible is False
            assert '5' in msg

    def test_muon_khi_tai_khoan_bi_khoa(self, test_app, seed_data):

        with test_app.app_context():
            user = User.query.filter_by(username='inactive_user').first()
            book = Book.query.filter(Book.quantity > 0).first()
            eligible, msg = utils.check_borrow_eligibility(user, book, 0)
            assert eligible is False
            assert 'khóa' in msg.lower()

    def test_tao_borrow_record(self, test_app, seed_data):

        with test_app.app_context():
            user = User.query.filter_by(username='user2').first()
            book = Book.query.filter_by(title='Django cho người mới').first()
            old_qty = book.quantity

            record = BorrowRecord(
                user_id=user.id,
                book_id=book.id,
                due_date=date.today() + timedelta(days=14),
            )
            db.session.add(record)
            book.quantity -= 1
            db.session.commit()

            assert book.quantity == old_qty - 1
            assert record.status == 'BORROWED'
            assert record.fine == 0

    def test_muon_khi_co_no_qua_han(self, test_app, seed_data):
        with test_app.app_context():
            user = User.query.filter_by(username='user2').first()
            book = Book.query.filter(Book.quantity > 0).first()
            
            # Create an overdue record for the user
            overdue_record = BorrowRecord(
                user_id=user.id,
                book_id=book.id,
                borrow_date=date.today() - timedelta(days=30),
                due_date=date.today() - timedelta(days=16),
                status='BORROWED'
            )
            db.session.add(overdue_record)
            db.session.commit()
            
            eligible, msg = utils.check_borrow_eligibility(user, book, 0)
            assert eligible is False
            assert 'nợ quá hạn' in msg.lower()
