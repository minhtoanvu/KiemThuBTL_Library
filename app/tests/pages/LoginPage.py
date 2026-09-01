from app.tests.pages.BasePage import BasePage
from selenium.webdriver.common.by import By
class LoginPage(BasePage):
    URL = 'http://127.0.0.1:5000/login'

    INPUT_USERNAME = (By.CSS_SELECTOR, '#username')
    INPUT_PASSWORD = (By.CSS_SELECTOR, '#password')
    BUTTON_SUBMIT= (By.CSS_SELECTOR, 'body > div.container.container-main.mt-3 > div > div > form > button')

    def open_page(self):
        self.open(self.URL)
    def login(self,username,password):
        self.typing(*self.INPUT_USERNAME,username)
        self.typing(*self.INPUT_PASSWORD,password)
        self.click(*self.BUTTON_SUBMIT)