"""
Selenium-based Google account password history clearing script

Wanted to use one of previously-used passwords with a Google account,
but Google remembers last 100 uses passwords and does not allow reuse of them.

This script will flush out the password history by changing the password enough
times to push all previously-used passwords from history.

Found these but it's for Windows only (and for very old version of Google site), which
does not work for me:

http://roozbeh-eng.blogspot.com/2013/04/an-updated-script-to-change-your-gmail.html
https://gist.github.com/bjarki/9886887


In order to run this, you need Selenium's Python bindings and ChromeDriver for Selenium.

ChromeDriver:
https://sites.google.com/a/chromium.org/chromedriver/downloads
(update CHROMEDRIVER_BINARY_PATH value below)

Selenium Python bindings:
`virtualenv .venv/`
`source .venv/bin/activate`
`pip install -r requirements.txt`

Run:
Make sure to set several password recovery options before you run this.

`python main.py 'my.email@gmail.com' 'current password' 'desired password'`

"""

import sys
import time

from selenium.webdriver import Remote, DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


CHROMEDRIVER_BINARY_PATH = '/path/to/chromedriver'

def Selector(value, by_condition=By.ID, timeout=0):
    return dict(
        value = value,
        by_condition = by_condition,
        timeout = timeout
    )


class BareBonesAPI(object):

    def __init__(self, driver):
        self.driver = driver
        """type: Chrome"""

    @classmethod
    def init_against_external_service(cls):

        service = Service(CHROMEDRIVER_BINARY_PATH)
        service.start()
        service_url = service.service_url

        # # for manually-run server
        # service_url = 'http://localhost:9515'

        driver = Remote(service_url, DesiredCapabilities.CHROME)

        return cls(driver)
        # driver.close()
        # service.stop()

    def go(self, url):
        self.driver.get(url)

    def get_elements(self, by_condition, value, timeout=0, expected_element_condition=EC.presence_of_all_elements_located):
        """
        Example::

            e = get_element(By.ID, 'email', timeout=10) # 10 seconds for timeout.

        :param By by_condition:
        :param str value:
        :param Chrome driver:
        :param int timeout:
        :param callable expected_element_condition:
        :return:
        """

        driver = self.driver

        return WebDriverWait(
            driver, timeout
        ).until(
            expected_element_condition((by_condition, value))
        )

    def process_form(self, form_elements_data, auto_submit=True):
        e = None
        for selector, value in form_elements_data:
            for e in self.get_elements(**selector):
                e.clear()
                e.send_keys(value)
        if e and auto_submit:
            e.send_keys(Keys.RETURN)


class GoogleAccountPasswordCycler(BareBonesAPI):

    default_timeout = 10

    def initial_login(self, email_address, present_password):

        self.go('https://accounts.google.com/Login')
        self.process_form([
            (
                Selector('Email', timeout=self.default_timeout),
                email_address
            )
        ])

        # just waiting for page to load
        e = self.get_elements(**Selector('Passwd', timeout=self.default_timeout))

        # and checking for presense of capcha
        try:
            e = self.driver.find_element_by_id('logincaptcha')
            timeout = 40 # seconds enough to type the capcha
            auto_submit = False
        except NoSuchElementException:
            timeout = 10
            auto_submit = True

        self.process_form(
            [
                (
                    Selector('Passwd', timeout=self.default_timeout),
                    present_password
                )
            ],
            auto_submit=auto_submit
        )

        be_done_by_time = time.time() + timeout
        while True:
            if 'My Account' in self.driver.title:
                break
            time.sleep(1)
            if be_done_by_time < time.time():
                raise Exception('Could not confirm successful login')


    def change_password(self, present_password, desired_password):
        self.go('https://myaccount.google.com/security/signinoptions/password')

        # and checking for presense of capcha for which I did not bother to automate
        try:
            e = self.driver.find_element_by_id('logincaptcha')
            timeout = 40 # seconds enough to type the capcha manually
            auto_submit = False
        except NoSuchElementException:
            timeout = 10
            auto_submit = True

        # for validation Google asks for pass again
        self.process_form(
            [
                (
                    Selector('Passwd', timeout=self.default_timeout),
                    present_password
                )
            ],
            auto_submit=auto_submit
        )

        be_done_by_time = time.time() + timeout
        while True:
            if 'Password' in self.driver.title:
                break
            time.sleep(1)
            if be_done_by_time < time.time():
                raise Exception('Could not confirm successful login')

        print 'Changing from: "{}" to "{}"'.format(present_password, desired_password)
        self.process_form(
            [
                (
                    Selector("//input[@type='password']", by_condition=By.XPATH, timeout=self.default_timeout),
                    desired_password
                )
            ],
            auto_submit=auto_submit
        )

        be_done_by_time = time.time() + timeout
        while True:
            if 'Sign-in & security' in self.driver.title:
                break
            time.sleep(1)
            if be_done_by_time < time.time():
                raise Exception('Could not confirm successful password change')


    def do_work(self, email_address, current_passord, desired_password):
        number_of_changes_required_to_return_to_desired = 102

        self.initial_login(email_address, current_passord)

        original_password = current_passord

        # this forces the password history to fall off the cliff
        for i in range(number_of_changes_required_to_return_to_desired):
            print "-- on {} iteration out of {} --".format(i+1, number_of_changes_required_to_return_to_desired)
            temp_password = u'{}-{}'.format(original_password, i)
            self.change_password(current_passord, temp_password)
            current_passord = temp_password

        # finally setting the pass we want
        self.change_password(current_passord, desired_password)


def doit(email_address, current_passord, desired_password):
    o = GoogleAccountPasswordCycler.init_against_external_service()
    o.do_work(email_address, current_passord, desired_password)


if __name__ == '__main__':

    script_name = sys.argv[0]
    args = sys.argv[1:]

    try:
        email_address, current_passord, desired_password = args
    except:
        print "Run this as: python {} 'email address here' 'current password here' 'desired password here'".format(script_name)
        sys.exit()

    print email_address, current_passord, desired_password
    doit(email_address, current_passord, desired_password)
