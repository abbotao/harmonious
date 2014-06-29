import os
import time
import re

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, StaleElementReferenceException
from nose.tools import raises

HERE = os.path.dirname(__file__)
TEST_HTML = os.path.join(HERE, 'html')
PAGES = dict()
for filename in os.listdir(TEST_HTML):
    name = filename.split('.html')[0]
    PAGES[name] = 'file://%s' % os.path.join(TEST_HTML, filename)

from harmonious.directives import webdriver as wd


def assert_matches(regexp, string):
    assert re.search(regexp, string, flags=re.IGNORECASE) is not None


class TestDirectives(object):
    def setup(self):
        self.browser = webdriver.PhantomJS()

    def teardown(self):
        self.browser.close()

    def test_find_element(self):
        self.browser.get(PAGES['basic_page'])
        try:
            assert wd.find_element(self.browser, "#test1") is not None, "Could not find using CSS selector"
            assert wd.find_element(self.browser, ("id", "test1")) is not None, "Could not find using 'by' id"
        except NoSuchElementException:
            assert False, "Caught NoSuchElementException"

    def test_wait_for_result_immediate_pass(self):
        def passing(a, b, c):
            return a and b and c

        start = time.time()
        assert wd.wait_for_result(passing, [True, True, True], 1)
        assert time.time() - start < 1

    def test_wait_for_result_delayed_pass(self):
        def delayed(start, timeout):
            if time.time() - start < timeout:
                raise Exception()
            else:
                return True

        start = time.time()
        assert wd.wait_for_result(delayed, [start, 1], 2)
        assert time.time() - start < 2

    @raises(Exception)
    def test_wait_failure(self):
        def always_raise():
            raise Exception()

        assert wd.wait_for_result(always_raise, [], 1)

    def test_contains_content(self):
        self.browser.get(PAGES['basic_page'])
        assert wd.contains_content(self.browser, "Testing")
        assert wd.contains_content(self.browser, "Google Link")
        assert not wd.contains_content(self.browser, "hidden")
        assert not wd.contains_content(self.browser, "Failure")

    def test_load_url(self):
        assert_matches(wd.load_url.regexp, "load http://www.google.com")
        wd.load_url(self.browser, "http://www.google.com/")
        assert self.browser.current_url == "http://www.google.com/", "current url is %s" % self.browser.current_url 

    def test_type_into_element(self):
        self.browser.get(PAGES['form'])
        assert_matches(wd.type_into_element.regexp, 'type "andrew" into "#test1"')
        wd.type_into_element(self.browser, "#test1", "testing")
        value = wd.find_element(self.browser, "#test1").get_attribute("value")
        assert value == "testing", "Value: %s" % value

    def test_click_element(self):
        self.browser.get(PAGES['basic_page'])
        assert_matches(wd.click_element.regexp, 'click "#test1"')
        wd.click_element(self.browser, "#test2")
        assert self.browser.current_url == "http://www.google.com/"

    def test_follow_link(self):
        self.browser.get(PAGES['basic_page'])
        assert_matches(wd.follow_link.regexp, 'follow link "#test1"')
        wd.follow_link(self.browser, "#test2")
        assert self.browser.current_url == "http://www.google.com/"

    def test_wait(self):
        assert_matches(wd.wait.regexp, 'wait 2.1 seconds')
        start = time.time()
        wd.wait(self.browser, 2)
        assert time.time() - start >= 2

    def test_check_uncheck_checkbox(self):
        self.browser.get(PAGES['form'])
        assert_matches(wd.check_checkbox.regexp, 'check "#test1"')
        assert_matches(wd.uncheck_checkbox.regexp, 'uncheck "#test1"')
        # check the checkbox
        wd.check_checkbox(self.browser, "#checkbox1")
        assert wd.find_element(self.browser, "#checkbox1").is_selected()
        # when called again, should still be checked
        wd.check_checkbox(self.browser, "#checkbox1")
        assert wd.find_element(self.browser, "#checkbox1").is_selected()
        # uncheck the checkbox
        wd.uncheck_checkbox(self.browser, "#checkbox1")
        assert not wd.find_element(self.browser, "#checkbox1").is_selected()
        # when called again, shoudl still be unchecked
        wd.uncheck_checkbox(self.browser, "#checkbox1")
        assert not wd.find_element(self.browser, "#checkbox1").is_selected()

    def test_select_multi_items(self):
        self.browser.get(PAGES['form'])
        assert_matches(wd.select_multi_items.regexp, 'select [test1, test2] from #select1')
        wd.select_multi_items(self.browser, "opt1,Test2", "#select1")
        wd.select_multi_items(self.browser, "Test5, opt2", "#select1")
        wd.select_multi_items(self.browser, '"opt3", opt2', "#select1")

    def test_select_single_item(self):
        self.browser.get(PAGES['form'])
        assert_matches(wd.select_single_item.regexp, 'Select "opt1" from #select1')
        wd.select_single_item(self.browser, "#select1", "opt1")

    def test_choose_radio(self):
        self.browser.get(PAGES['form'])
        assert_matches(wd.choose_radio.regexp, 'choose radio with value "rad"')
        wd.choose_radio(self.browser, "rad")

    def test_expect_content(self):
        self.browser.get(PAGES['basic_page'])
        assert_matches(wd.expect_content.regexp, 'expect to see content "Testing"')
        wd.expect_content(self.browser, "Testing")
        try:
            wd.expect_content(self.browser, "notfound")
        except AssertionError as ex:
            assert ex.message == "Could not find content."
        try:
            wd.expect_content(self.browser, "hidden")
        except AssertionError as ex:
            assert ex.message == "Could not find content."

    def test_expect_content_within(self):
        self.browser.get(PAGES['basic_page'])
        assert_matches(wd.expect_content_within.regexp, 'expect to see content "Testing" within 2.1 seconds')
        wd.expect_content_within(self.browser, "Testing", 1)

    def test_expect_exists(self):
        self.browser.get(PAGES['basic_page'])
        assert_matches(wd.expect_exists.regexp, 'expect exists "#test1"')
        wd.expect_exists(self.browser, "#test1")

    @raises(NoSuchElementException)
    def test_expect_exists_fail(self):
        wd.expect_exists(self.browser, "#notfound")

    def test_expect_exists_within(self):
        self.browser.get(PAGES['basic_page'])
        assert_matches(wd.expect_exists.regexp, 'expect exists "#test1" within 3.2 seconds')
        wd.expect_exists_within(self.browser, "#test1", 1)

    def test_expect_page_title(self):
        self.browser.get(PAGES['basic_page'])
        assert_matches(wd.expect_page_title.regexp, 'expect page title is "This is a test page"')
        wd.expect_page_title(self.browser, "This is a test page")

    @raises(AssertionError)
    def test_expect_page_title_faie(self):
        self.browser.get(PAGES['basic_page'])
        wd.expect_page_title(self.browser, "This is a test pge")

    def test_expect_page_title_within(self):
        self.browser.get(PAGES['basic_page'])
        assert_matches(wd.expect_page_title.regexp, 'expect page title is "This is a test page" within 9.9 seconds')
        wd.expect_page_title_within(self.browser, "This is a test page", 1)


# @directive(r'Expect (?P<elem>.+) contains "(?P<regexp>.+)"')
# def expect_elem_match_regexp(browser, elem, regexp):
#     assert re.search(regexp, find_element(browser, elem).text) is not None, "Could not find value in element"


# @directive(r'Expect (?P<elem>.+) contains "(?P<regexp>.+)" within (?P<seconds>\d+(\.\d+)?) seconds')
# def expect_elem_match_regexp_within(browser, elem, regexp, seconds):
#     return wait_for_result(expect_elem_match_regexp, [browser, elem, regexp], seconds)

# @directive(r'Expect (?P<elem>.+) does not contain "(?P<regexp>.+)"')
# def expect_elem_should_not_match_regexp(browser, elem, regexp):
#     assert re.search(regexp, find_element(browser, elem).text) is None, "Value was in element."

# @directive(r'Expect (?P<elem>.+) does not contain "(?P<regexp>.+) within (?P<seconds>\d+(\.\d+)?) seconds')
# def expect_elem_should_not_match_regexp_within(browser, elem, regexp, seconds):
#     return wait_for_result(expect_elem_should_not_match_regexp, [browser, regexp, elem], seconds)


# @directive(r'Expect (?P<elem>.+) to not exist', throws=NoSuchElementException)
# def expect_not_exist(browser, elem):
#     return find_element(browser, elem) is None


# @directive(r'Expect (?P<elem>.+) to not exist within (?P<seconds>\d+(\.\d+)?) seconds', throws=NoSuchElementException)
# def expect_not_exist_within(browser, elem, seconds):
#     return wait_for_result(expect_not_exist, [browser, elem], seconds)


# @directive(r'Expect (?P<elem>.+) is selected')
# def expect_checkbox_selected(browser, elem):
#     assert find_element(browser, elem).is_selected(), "Element is not selected"

# @directive(r'Expect (?P<elem>.+) is not selected')
# def expect_checkbox_not_selected(browser, elem):
#     assert not find_element(browser, elem).is_selected(), "Element is not selected"

# @directive(r'Expect link with url "(?P<url>.+)"')
# def expect_link_with_url(browser, url):
#     assert browser.find_element_by_xpath(str('//a[@href="%s"]' % url)) is not None, "No link found"


# @directive(r'Expect link with url "(?P<url>.+)" that contains text "(?P<text>.+)"')
# def expect_link_with_url_and_text(browser, url, text):
#     assert browser.find_element_by_xpath(str('//a[@href="%s"][contains(., %s)]' % (url, text))) is not None, "No link found"


# @directive(r'Expect url to be "(?P<url>.+)"')
# def expect_browser_url_to_be(browser, url):
#     assert browser.current_url == url, "URL was %s" % browser.current_url


# @directive(r'Expect url to be "(?P<url>.+)" within (?P<seconds>\d+(\.\d+)?) seconds')
# def eexpect_browser_url_to_be_within(browser, url, seconds):
#     return wait_for_result(expect_browser_url_to_be, [browser, url], seconds)


# @directive(r'Expect url to contain "(?P<url>.+)')
# def expect_browser_url_to_contain(browser, url):
#     assert url in browser.current_url, "URL was %s" % browser.current_url


# @directive(r'Expect url to contain "(?P<url>.+) within (?P<seconds>\d+(\.\d+)?) seconds')
# def expect_browser_url_to_contain_within(browser, url, seconds):
#     return wait_for_result(expect_browser_url_to_contain, [browser, url], seconds)


# @directive(r'Expect (?P<elem>.+) to have a value equal to "(?P<value>.+)"')
# def expect_element_to_have_value(browser, elem, value):
#     element = find_element(browser, elem)
#     assert element.get_attribute("value") == value, "Value was %s " % element.get_attribute("value")


# @directive(r'Expect (?P<elem>.+) to have a value equal to "(?P<value>.+)" within (?P<seconds>\d+(\.\d+)?) seconds')
# def expect_element_to_have_value_within(browser, elem, value, seconds):
#     return wait_for_result(expect_element_to_have_value, [browser, elem, value], seconds)


# @directive(r'Expect (?P<elem>.+) to contain a value of "(?P<regexp>.+)"')
# def expect_element_to_contain_value(browser, elem, regexp):
#     element = find_element(browser, elem)
#     assert re.search(regexp, element.get_attribute("value")) is not None, "Value was %s " % element.get_attribute("value")


# @directive(r'Expect (?P<elem>.+) to contain a value of "(?P<regexp>.+)" within (?P<seconds>\d+(\.\d+)?) seconds')
# def expect_element_to_contain_value_within(browser, elem, regexp, seconds):
#     return wait_for_result(expect_element_to_contain_value, [browser, elem, regexp], seconds)


# @directive('expect "(?P<value>.*?)" from (?P<select>.*?) should be selected')
# def assert_single_selected(browser, option_name, select_name):
#     option = None
#     try:
#         option = find_element(browser, "select[name='%s'] > option[value='%s']" % (select, value))
#     except NoSuchElementException:
#         option = find_element(browser, "select[id='%s'] > option[value='%s']" % (select, value))
    
#     assert option.is_selected(), "Option was not selected"

# @directive(r'expect \[(?P<list>.+)\] from (?P<select>.+) should be selected')
# def assert_multi_selected(browser, select, list):
#         options = list.split(',')
#         select_box = find_element(browser, select)
#         option_elems = select_box.find_elements_by_xpath(str('./option'))
#         for option in option_elems:
#             if option.get_attribute('id') in options or \
#                option.get_attribute('name') in options or \
#                option.get_attribute('value') in options or \
#                option.text in options:
#                 assert option.is_selected(), "Option %s was not selected" % option
#             else:
#                 assert not option.is_selected(), "Option %s was selected" % option


# @directive(r'Expect option "(?P<value>.+)" in selector (?P<select>.+)')
# def select_contains(browser, select, value):
#     try:
#         option = find_element(browser, "select[name='%s'] > option[value='%s']" % (select, value))
#     except NoSuchElementException:
#         option = find_element(browser, "select[id='%s'] > option[value='%s']" % (select, value))
#     assert option is not None, "Could not find option"

# @directive(r'Expect option "(?P<value>.+)" not in selector (?P<select>.+)', throws=NoSuchElementException)
# def select_does_not_contain(browser, select, value):
#     try:
#         option = find_element(browser, "select[name='%s'] > option[value='%s']" % (select, value))
#     except NoSuchElementException:
#         option = find_element(browser, "select[id='%s'] > option[value='%s']" % (select, value))
#     assert option is None, "Found option"


# @directive('Expect "(?P<value>.+)" radio should be selected')
# def assert_radio_selected(browser, value):
#     radio = find_element(browser, ('css_selector', 'input[type="radio"][value="%s"]' % value))
#     assert radio.is_selected(), "Radio not selected"


# @directive('Expect "(?P<value>.+)" radio should not be selected')
# def assert_radio_not_selected(browser, value):
#     radio = find_element(browser, ('css_selector', 'input[type="radio"][value="%s"]' % value))
#     assert not radio.is_selected(), "Radio is selected"


# @directive('Accept the alert')
# def accept_alert(browser):
#     try:
#         alert = Alert(browser)
#         alert.accept()
#     except WebDriverException:
#         pass


# @directive('Dismiss the alert')
# def dismiss_alert(browser):
#     try:
#         alert = Alert(browser)
#         alert.dismiss()
#     except WebDriverException:
#         pass


# @directive(r'Expect an alert with text "(?P<text>.+)"')
# def expect_alert(browser, text):
#     try:
#         alert = Alert(browser)
#         assert alert.text == text, "Alert text is %s" % alert.text
#     except WebDriverException:
#         pass


# @directive('Expect no alert displayed')
# def expect_no_alert(browser):
#     try:
#         alert = Alert(browser) 
#         assert alert is None, "Alert '%s' shown." % alert.text
#     except NoAlertPresentException:
#         pass
