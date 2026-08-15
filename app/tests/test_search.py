import pytest
from app import db
from app.models import User, Book, Category, BorrowRecord
from app import dao, utils
from app.tests.test_base import test_app,test_session,test_client,seed_data
class TestSearchBooks:


    def test_tim_theo_tu_khoa(self, test_app, seed_data):

        with test_app.app_context():
            result = dao.load_books(kw='Python')
            assert result.total > 0
            for book in result.items:
                assert 'python' in book.title.lower()

    def test_tim_theo_tac_gia(self, test_app, seed_data):

        with test_app.app_context():
            result = dao.load_books(author='AI')
            assert result.total > 0
            for book in result.items:
                assert 'ai' in book.author.lower()

    def test_tim_theo_the_loai(self, test_app, seed_data):

        with test_app.app_context():
            result = dao.load_books(category='AI')
            assert result.total > 0

    def test_tim_khong_co_ket_qua(self, test_app, seed_data):

        with test_app.app_context():
            result = dao.load_books(kw='XYZ_KHONG_TON_TAI_12345')
            assert result.total == 0

    def test_tim_ket_hop_keyword_va_author(self, test_app, seed_data):

        with test_app.app_context():
            result = dao.load_books(kw='AI', author='UI')
            assert result.total > 0
            for book in result.items:
                assert 'ai' in book.title.lower()
                assert 'ui' in book.author.lower()

    def test_load_tat_ca_sach(self, test_app, seed_data):

        with test_app.app_context():
            result = dao.load_books()
            assert result.total > 0

    def test_get_book_by_id(self, test_app, seed_data):

        with test_app.app_context():
            book = dao.get_book_by_id(1)
            assert book is not None
            assert book.id == 1

    def test_get_book_by_id_khong_ton_tai(self, test_app, seed_data):

        with test_app.app_context():
            book = dao.get_book_by_id(9999)
            assert book is None



