__author__ = 'Robert Donovan'
# I hate Pycharm right now
# Get Selenium for Automated browser testing

import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class NewVisitorTest(unittest.TestCase):


    def setUp(self):
        # Use Chrome
        self.browser = webdriver.Chrome('C:\Python34\Scripts\chromedriver')  # Bullshit Windows location for Robert.
        self.browser.get('http://www.google.com/xhtml')
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id("main_tbl")
        rows = table.find_element_by_tag_name('tr')
        self.assertTrue(row_text, [row.text for row in rows])

    def test_can_start_a_list_and_retrieve_it_later(self):
        # Open the site and check out the home page
        self.browser.get('http://localhost:5000')

        # What does the page title of the homepage?
        self.assertIn('2Weeks', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('2Weeks', header_text)

        # The user needs to enter a to-do item
        inputbox = self.browser.find_element_by_xpath("//input")
        # print(inputbox)
        # self.assertEqual(
        #    inputbox.get_attribute('placeholder'),
        #    'Enter a to-do item'
        # )

        # User types in a value into the text box
        inputbox.send_keys('Jake')

        # When they press enter the page updates and not the page lists that value in the list
        inputbox.send_keys(Keys.ENTER)

        self.check_for_row_in_list_table('Jake')

        self.fail('Finish the test!')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
