from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, url):
        self.driver.get(url)

    def find(self, by,value):
        return self.driver.find_element(by,value)

    def finds(self, by,value):
        return self.driver.find_elements(by,value)
    def typing(self, by,value,text):
        e = self.find(by,value)
        e.send_keys(text)
    def click(self, by,value):
            e = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by, value))
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                e
            )

            self.driver.execute_script("arguments[0].click();", e)

    def select(self, by, value, text):
        e = self.find(by, value)
        Select(e).select_by_visible_text(text)

    def wait_for_element(self, by, value, timeout=10):
        wait = WebDriverWait(self.driver, timeout)

        return wait.until(
            EC.visibility_of_element_located((by, value))
        )

