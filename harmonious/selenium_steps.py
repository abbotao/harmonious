import re
import time

from harmonious.decorators import step

def find_element(browser, element):
    if type(element) == tuple:
        return browser.find_element(by=element[0], value=element[1])
    else:
        return browser.find_element(by="css selector", value=element)

@step(r'load (?P<url>.+)')
def load_url(browser, url):
    browser.get(url);

@step(r'expect exists (?P<elem>.+)')
def expect_exists(browser, elem):
    assert find_element(browser, elem) is not None

@step(r'type "(?P<input>.+)" into (?P<elem>.+)')
def type_into_element(browser, elem, input):
    find_element(browser, elem).send_keys(input)

@step(r'click (?P<elem>.+)')
def click_element(browser, elem):
    find_element(browser, elem).click()

@step(r'Expect Page Title is "(?P<title>.+)"')
def expect_page_title(browser, title):
    assert browser.title == title

@step(r'Expect (?P<elem>.+) contains "(?P<regexp>.+)"')
def expect_elem_match_regexp(browser, elem, regexp):
    assert re.search(regexp, find_element(browser, elem).text) is not None

@step(r'Wait (?P<seconds>\d+(\.\d+)?) seconds')
def wait(browser, seconds):
    start = time.time()
    while time.time() - start < float(seconds):
        time.sleep(0.2)
