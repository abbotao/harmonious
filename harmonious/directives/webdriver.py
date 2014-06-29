import re
import time

from harmonious.decorators import directive, expression
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, WebDriverException, StaleElementReferenceException


def find_element(browser, element):
    if type(element) == tuple:
        return browser.find_element(by=element[0], value=element[1])
    else:
        return browser.find_element(by="css selector", value=element)


def wait_for_result(function, args, seconds):
    start = time.time()
    exception = None
    while time.time() - start < float(seconds):
        try:
            return function(*args)
        except Exception as ex:
            exception = ex
            time.sleep(0.2)
    raise exception

# This function is from lettuce-webdriver: 
# https://github.com/bbangert/lettuce_webdriver/blob/master/lettuce_webdriver/webdriver.py
def contains_content(browser, content):
    # Search for an element that contains the whole of the text we're looking
    #  for in it or its subelements, but whose children do NOT contain that
    #  text - otherwise matches <body> or <html> or other similarly useless
    #  things.
    for elem in browser.find_elements_by_xpath(str(
            '//*[contains(normalize-space(.),"{content}") '
            'and not(./*[contains(normalize-space(.),"{content}")])]'
            .format(content=content))):

        try:
            if elem.is_displayed():
                return True
        except StaleElementReferenceException:
            pass

    return False


@directive(r'load (?P<url>.+)')
def load_url(browser, url):
    browser.get(url)

#Interaction
@directive(r'type "(?P<keys>.+)" into (?P<elem>.+)')
def type_into_element(browser, elem, keys):
    find_element(browser, elem).send_keys(keys)


@expression(r'click (?P<elem>.+)')
@directive(r'press (?P<elem>.+)')
def click_element(browser, elem):
    find_element(browser, elem).click()

@directive(r'Wait (?P<seconds>\d+(\.\d+)?) seconds')
def wait(browser, seconds):
    start = time.time()
    while time.time() - start < float(seconds):
        # This function doesn't wait exactly this long,
        # So we need to wait a short period and check the actual
        # time elapsed
        time.sleep(0.2) 

@directive(r'Check (?P<elem>.+)')
def check_checkbox(browser, elem):
    element = find_element(browser, elem)
    if not element.is_selected():
        element.click()

@directive(r'Uncheck (?P<elem>.+)')
def uncheck_checkbox(browser, elem):
    element = find_element(browser, elem)
    if element.is_selected():
        element.click()

#expect statements
@directive(r'expect to see content (?P<content>.+)')
def expect_content(browser, content):
    assert contains_content(browser, content), "Could not find content."


@directive(r'expect to see content (?P<content>.+) within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_content_within(browser, content, seconds):
    wait_for_result(expect_content, [browser, content], seconds)


@directive(r'expect exists (?P<elem>.+)')
def expect_exists(browser, elem):
    assert find_element(browser, elem) is not None, "Element does not exist."


@directive(r'expect exists (?P<elem>.+) within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_exists_within(browser, elem, seconds):
    return wait_for_result(expect_exists, [browser, elem], seconds)


@directive(r'Expect Page Title is "(?P<title>.+)"')
def expect_page_title(browser, title):
    assert browser.title == title, "Title was '%s'" % browser.title

@directive(r'Expect Page Title is "(?P<title>.+)" within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_page_title_within(browser, title, seconds):
    return wait_for_result(expect_page_title, [browser, title], seconds)


@directive(r'Expect (?P<elem>.+) contains "(?P<regexp>.+)"')
def expect_elem_match_regexp(browser, elem, regexp):
    assert re.search(regexp, find_element(browser, elem).text) is not None, "Could not find value in element"


@directive(r'Expect (?P<elem>.+) contains "(?P<regexp>.+)" within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_elem_match_regexp_within(browser, elem, regexp, seconds):
    return wait_for_result(expect_elem_match_regexp, [browser, elem, regexp], seconds)


@directive(r'Expect (?P<elem>.+) to not exist', throws=NoSuchElementException)
def expect_not_exist(browser, elem):
    return find_element(browser, elem) is None


@directive(r'Expect (?P<elem>.+) to not exist within (?P<seconds>\d+(\.\d+)?) seconds', throws=NoSuchElementException)
def expect_not_exist_within(browser, elem, seconds):
    return wait_for_result(expect_not_exist, [browser, elem], seconds)


@directive(r'Expect (?P<elem>.+) is selected')
def expect_checkbox_selected(browser, elem):
    assert find_element(browser, elem).is_selected(), "Element is not selected"

@directive(r'Expect (?P<elem>.+) is selected within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_checkbox_selected_within(browser, elem, seconds):
    return wait_for_result(expect_checkbox_selected, [browser, elem], seconds)

@directive(r'Expect (?P<elem>.+) is not selected')
def expect_checkbox_not_selected(browser, elem):
    assert not find_element(browser, elem).is_selected(), "Element is not selected"

@directive(r'Expect (?P<elem>.+) is not selected within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_checkbox_not_selected_within(browser, elem, seconds):
    return wait_for_result(expect_checkbox_not_selected, [browser, elem], seconds)

@directive(r'Follow link (?P<elem>.+)')
def follow_link(browser, elem):
    element = find_element(browser, elem)
    destination = element.get_attribute("href")
    browser.get(destination)


@directive(r'Expect link with url "(?P<url>.+)"')
def expect_link_with_url(browser, url):
    assert browser.find_element_by_xpath(str('//a[@href="%s"]' % url)) is not None, "No link found"

@directive(r'Expect link with url "(?P<url>.+) within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_link_with_url_within(browser, url, seconds):
    return wait_for_result(expect_link_with_url, [browser, url], seconds)

@directive(r'Expect link with url "(?P<url>.+)" that contains text "(?P<text>.+)"')
def expect_link_with_url_and_text(browser, url, text):
    assert browser.find_element_by_xpath(str('//a[@href="%s"][contains(., %s)]' % (url, text))) is not None, "No link found"

@directive(r'Expect link with url "(?P<url>.+)" that contains text "(?P<text>.+) within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_link_with_url_and_text_within(browser, url, text, seconds):
    return wait_for_result(expect_link_with_url_and_text, [browser, url, text], seconds)

@directive(r'Expect (?P<elem>.+) does not contain "(?P<regexp>.+)"')
def expect_elem_should_not_match_regexp(browser, elem, regexp):
    assert re.search(regexp, find_element(browser, elem).text) is None, "Value was in element."

@directive(r'Expect (?P<elem>.+) does not contain "(?P<regexp>.+) within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_elem_should_not_match_regexp_within(browser, elem, regexp, seconds):
    return wait_for_result(expect_elem_should_not_match_regexp, [browser, regexp, elem], seconds)

@directive(r'Expect url to be "(?P<url>.+)"')
def expect_browser_url_to_be(browser, url):
    assert browser.current_url == url, "URL was %s" % browser.current_url


@directive(r'Expect url to be "(?P<url>.+)" within (?P<seconds>\d+(\.\d+)?) seconds')
def eexpect_browser_url_to_be_within(browser, url, seconds):
    return wait_for_result(expect_browser_url_to_be, [browser, url], seconds)


@directive(r'Expect url to contain "(?P<url>.+)')
def expect_browser_url_to_contain(browser, url):
    assert url in browser.current_url, "URL was %s" % browser.current_url


@directive(r'Expect url to contain "(?P<url>.+) within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_browser_url_to_contain_within(browser, url, seconds):
    return wait_for_result(expect_browser_url_to_contain, [browser, url], seconds)


@directive(r'Expect (?P<elem>.+) to have a value of "(?P<value>.+)"')
def expect_element_to_have_value(browser, elem, value):
    element = find_element(browser, elem)
    assert element.get_attribute("value") == value, "Value was %s " % element.get_attribute("value")


@directive(r'Expect (?P<elem>.+) to have a value of "(?P<value>.+)" within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_element_to_have_value_within(browser, elem, value, seconds):
    return wait_for_result(expect_element_to_have_value, [browser, elem, value], seconds)


@directive(r'Expect (?P<elem>.+) to contain a value of "(?P<regexp>.+)"')
def expect_element_to_contain_value(browser, elem, regexp):
    element = find_element(browser, elem)
    assert re.search(regexp, element.get_attribute("value")) is not None, "Value was %s " % element.get_attribute("value")


@directive(r'Expect (?P<elem>.+) to contain a value of "(?P<regexp>.+)" within (?P<seconds>\d+(\.\d+)?) seconds')
def expect_element_to_contain_value_within(browser, elem, regexp, seconds):
    return wait_for_result(expect_element_to_contain_value, [browser, elem, regexp], seconds)


@directive('Accept the alert')
def accept_alert(browser):
    try:
        alert = Alert(browser)
        alert.accept()
    except WebDriverException:
        pass


@directive('Dismiss the alert')
def dismiss_alert(browser):
    try:
        alert = Alert(browser)
        alert.dismiss()
    except WebDriverException:
        pass


@directive(r'Expect an alert with text "(?P<text>.+)"')
def expect_alert(browser, text):
    try:
        alert = Alert(browser)
        assert alert.text == text, "Alert text is %s" % alert.text
    except WebDriverException:
        pass


@directive('Expect no alert displayed')
def expect_no_alert(browser):
    try:
        alert = Alert(browser) 
        assert alert is None, "Alert '%s' shown." % alert.text
    except NoAlertPresentException:
        pass
