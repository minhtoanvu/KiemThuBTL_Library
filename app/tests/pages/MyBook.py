from selenium.webdriver.common.by import By
from app.tests.pages.BasePage import BasePage


class MyBook(BasePage):
    URL = 'http://127.0.0.1:5000/my-books'

    TABLE_BORROWING = (By.CSS_SELECTOR,'.borrowing-book tbody tr')
    TABLE_HISTORY = (By.CSS_SELECTOR,'.history-book')

    def open_page(self):
        self.open(self.URL)

    def return_book(self, kw):
        rows = self.finds(*self.TABLE_BORROWING)

        for row in rows:

            title = row.find_element(
                By.CSS_SELECTOR,
                'td:nth-child(1) strong'
            ).text

            if kw.lower() in title.lower():

                buttons = row.find_elements(
                    By.CSS_SELECTOR,
                    'form button[type="submit"]'
                )

                if buttons:
                    buttons[0].click()
                    return True

        return False



