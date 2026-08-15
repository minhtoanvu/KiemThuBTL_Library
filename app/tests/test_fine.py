import pytest
from app import db
from app.models import User, Book, Category, BorrowRecord
from app import dao, utils
from datetime import date, timedelta
from app.tests.test_base import test_app,test_session,test_client,seed_data
class TestFineCalculation:


    def test_tra_dung_han_khong_phat(self):
        """ Trả sách đúng hạn → phạt = 0."""
        due = date.today()
        return_d = date.today()
        fine = utils.calculate_fine(due, return_d)
        assert fine == 0

    def test_tra_som_khong_phat(self):
        """ Trả sách sớm → phạt = 0."""
        due = date.today() + timedelta(days=5)
        return_d = date.today()
        fine = utils.calculate_fine(due, return_d)
        assert fine == 0

    def test_tra_tre_1_ngay(self):
        """ Trả trễ 1 ngày → phạt = 5000."""
        due = date.today() - timedelta(days=1)
        return_d = date.today()
        fine = utils.calculate_fine(due, return_d)
        assert fine == 5000

    def test_tra_tre_5_ngay(self):
        """ Trả trễ 5 ngày → phạt = 25000."""
        due = date.today() - timedelta(days=5)
        return_d = date.today()
        fine = utils.calculate_fine(due, return_d)
        assert fine == 25000

    def test_tra_tre_10_ngay(self):
        """ Trả trễ 10 ngày → phạt = 50000."""
        due = date.today() - timedelta(days=10)
        return_d = date.today()
        fine = utils.calculate_fine(due, return_d)
        assert fine == 50000

    def test_calculate_fine_khong_co_return_date(self):
        """ Tính phạt khi chưa trả (dùng ngày hiện tại)."""
        due = date.today() - timedelta(days=3)
        fine = utils.calculate_fine(due)
        assert fine == 3 * 5000

