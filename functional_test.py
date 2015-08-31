__author__ = 'Robert Donovan'
# I hate Pycharm right now
# Get Selenium for Automated browser testing

import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class NewVisitorTest(unittest.TestCase):  #

    def setUp(self):
        # Use Chrome
        self.browser = webdriver.Chrome('C:\Python34\Scripts\chromedriver')  # Bullshit Windows location for Robert.
        self.browser.get('http://www.google.com/xhtml')
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retieve_it_later(self):
        # Open the site and check out the home page
        self.browser.get('http://localhost:5000')

        # What does the page title of the homepage?
        self.assertIn('MIXFIN App', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('MIXFIN', header_text)

        # The user needs to enter a to-do item
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # User types in a value into the text box
        inputbox.send_keys('Buy peacock feathers')

        # When they press enter the page updates and not the page lists that value in the list
        inputbox.send_keys(Keys.ENTER)

        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_element_by_tag_name('tr')
        self.assertTrue(
            any(row.text == '1: Buy peacock feathers' for row in rows)
        )

        self.fail('Finish the test!')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
