import pytest
from app import db
from app.models import User, Book, Category, BorrowRecord
from app import dao, utils
from app.tests.test_base import test_app,test_session,test_client,seed_data
class TestCategories:

    def test_lay_tat_ca_the_loai(self, test_app, seed_data):

        with test_app.app_context():
            cats = dao.get_all_categories()
            assert len(cats) == 16
