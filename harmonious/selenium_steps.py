import re
import time

from harmonious.decorators import direction
from selenium.common.exceptions import NoSuchElementException

def find_element(browser, element):
    if type(element) == tuple:
        return browser.find_element(by=element[0], value=element[1])
    else:
        return browser.find_element(by="css selector", value=element)

@direction(r'load (?P<url>.+)')
def load_url(browser, url):
    browser.get(url);

@direction(r'expect exists (?P<elem>.+)')
def expect_exists(browser, elem):
    assert find_element(browser, elem) is not None

@direction(r'type "(?P<input>.+)" into (?P<elem>.+)')
def type_into_element(browser, elem, input):
    find_element(browser, elem).send_keys(input)

@direction(r'click (?P<elem>.+)')
def click_element(browser, elem):
    find_element(browser, elem).click()

@direction(r'Expect Page Title is "(?P<title>.+)"')
def expect_page_title(browser, title):
    assert browser.title == title

@direction(r'Expect (?P<elem>.+) contains "(?P<regexp>.+)"')
def expect_elem_match_regexp(browser, elem, regexp):
    assert re.search(regexp, find_element(browser, elem).text) is not None

@direction(r'Wait (?P<seconds>\d+(\.\d+)?) seconds')
def wait(browser, seconds):
    start = time.time()
    while time.time() - start < float(seconds):
        time.sleep(0.2)

@direction(r'Expect (?P<elem>.+) to not exist', throws=NoSuchElementException)
def expect_not_exist(browser, elem):
    find_element(browser, elem) is None


