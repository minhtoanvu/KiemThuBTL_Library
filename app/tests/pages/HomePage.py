
from app.tests.BasePage import BasePage

from selenium.webdriver.common.by import By



class HomePage(BasePage):
    URL = 'http://127.0.0.1:5000/'

    INPUT_KEYWORD= (By.CSS_SELECTOR,'#search-keyword')
    INPUT_AUTHOR= (By.CSS_SELECTOR,'#search-author')
    INPUT_CATEGORY= (By.CSS_SELECTOR,'#search-category')
    BUTTON_SEARCH = (By.CSS_SELECTOR,'.btn-search-advanced')
    BUTTON_BORROW = (By.CSS_SELECTOR,'.btn-gradient')
    BUTTON_CONFIRM_BORROW  = (By.CSS_SELECTOR,'#borrowForm > div.modal-footer > button.btn-gradient')
    def open_page(self):
        self.open(self.URL)


    def search_kw(self, keyword):
        self.typing(*self.INPUT_KEYWORD,keyword)
        self.click(*self.BUTTON_SEARCH)
    def search_au(self, keyword):
        self.typing(*self.INPUT_AUTHOR,keyword)
        self.click(*self.BUTTON_SEARCH)

    # def search_cate(self, keyword):
    #     self.select(*self.INPUT_CATEGORY,keyword)
    #     self.click(*self.BUTTON_SEARCH)
    def borrow(self):
        self.click(*self.BUTTON_BORROW)
        self.wait_for_element(*self.BUTTON_CONFIRM_BORROW)
        self.click(*self.BUTTON_CONFIRM_BORROW)
