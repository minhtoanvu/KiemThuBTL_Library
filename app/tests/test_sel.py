import time
import pytest
from app.tests.pages.HomePage import HomePage

from selenium.webdriver.common.by import By
from app.tests.pages.LoginPage import LoginPage
from app.tests.pages.MyBook import MyBook
from app.tests.test_base import test_app ,driver
def test_search(driver):
    home = HomePage(driver)
    login = LoginPage(driver)
    login.open_page()
    login.login('user1111','user123')
    time.sleep(1)
    home.open_page()
    kw = 'AI'
    auth = 'ui'

    home.search_kw(kw)
    time.sleep(1)
    home.search_au(auth)
    time.sleep(1)


    r = driver.find_elements(By.CSS_SELECTOR,'.book-card')
    assert len(r) > 0
    assert kw.lower() in r[0].find_element(By.CSS_SELECTOR,'.book-title').text.lower()
    assert auth.lower() in r[0].find_element(By.CSS_SELECTOR,'.book-author').text.lower()

def test_borrow(driver):
    home = HomePage(driver)
    login = LoginPage(driver)
    login.open_page()
    login.login('user1111', 'user123')
    time.sleep(1)
    home.open_page()
    kw = 'Machine Learning cơ bản'

    home.search_kw(kw)
    time.sleep(1)
 
    time.sleep(1)
    r = driver.find_elements(By.CSS_SELECTOR, '.book-card')
    home.borrow()
    time.sleep(1)
    mb  = MyBook(driver)
    mb.open_page()
    time.sleep(1)
    tr = driver.find_elements(By.CSS_SELECTOR,'.table-dark-custom > tbody > tr')


    assert len(tr) > 0

    assert any(
        kw.lower() in tr_item.find_element(
            By.CSS_SELECTOR,
            'td:nth-child(1) strong'
        ).text.lower()
        for tr_item in tr
    )

def test_return(driver):
    login = LoginPage(driver)
    mybook = MyBook(driver)
    login.open_page()
    login.login('user1111', 'user123')
    time.sleep(1)
    mybook.open_page()
    
    book_title = 'Machine Learning cơ bản'
    mybook.return_book(book_title)
    time.sleep(1)

    tr = driver.find_elements(By.CSS_SELECTOR, '.borrowing-book > tbody > tr')
    
    is_returning = False
    for row in tr:
        title_element = row.find_element(By.CSS_SELECTOR, 'td:nth-child(1)')
        if book_title.lower() in title_element.text.lower():
            badges = row.find_elements(By.CSS_SELECTOR, '.badge-status.returning')
            if len(badges) > 0 and 'Chờ duyệt trả' in badges[0].text:
                is_returning = True
                break
                
    assert is_returning

# def test_borrow_limit(driver):
#     home = HomePage(driver)
#     login = LoginPage(driver)
#     login.open_page()
#     login.login('user_max', 'user@1234')
#     time.sleep(1)
#     home.open_page()
