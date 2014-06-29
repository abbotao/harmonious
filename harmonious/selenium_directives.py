import re
import time

from harmonious.decorators import directive
from selenium.common.exceptions import NoSuchElementException


def find_element(browser, element):
    if type(element) == tuple:
        return browser.find_element(by=element[0], value=element[1])
    else:
        return browser.find_element(by="css selector", value=element)


@directive(r'load (?P<url>.+)')
def load_url(browser, url):
    browser.get(url)


@directive(r'expect exists (?P<elem>.+)')
def expect_exists(browser, elem):
    assert find_element(browser, elem) is not None, "Element exists"


@directive(r'type "(?P<keys>.+)" into (?P<elem>.+)')
def type_into_element(browser, elem, keys):
    find_element(browser, elem).send_keys(keys)


@directive(r'click (?P<elem>.+)')
def click_element(browser, elem):
    find_element(browser, elem).click()


@directive(r'Expect Page Title is "(?P<title>.+)"')
def expect_page_title(browser, title):
    assert browser.title == title, "Title was '%s'" % browser.title


@directive(r'Expect (?P<elem>.+) contains "(?P<regexp>.+)"')
def expect_elem_match_regexp(browser, elem, regexp):
    assert re.search(regexp, find_element(browser, elem).text) is not None, "Could not find value in element"


@directive(r'Wait (?P<seconds>\d+(\.\d+)?) seconds')
def wait(browser, seconds):
    start = time.time()
    while time.time() - start < float(seconds):
        time.sleep(0.2)


@directive(r'Expect (?P<elem>.+) to not exist', throws=NoSuchElementException)
def expect_not_exist(browser, elem):
    return find_element(browser, elem) is None
