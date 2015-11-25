import os
import json, string, random, unittest, time
from twoweeks import app
from twoweeks.database import init_db
from twoweeks.database import db_session
import twoweeks.config as config
from twoweeks.models import User, Bill, Role, Payment_Plan, Payment_Plan_Item, Feedback
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import testUtils

class FlaskrTestCase(unittest.TestCase):
    default_user_id = None
    default_test_password = None
    default_test_name = None
    default_test_username = None
    default_test_date = None


    def setUp(self):
        self.set_default_test_password(testUtils.random_password_generator())
        self.set_default_test_name("~~~" + testUtils.random_name_generator() + "~~~")
        self.set_default_test_username(testUtils.random_email_generator())
        self.set_default_test_date(datetime.utcnow())

        app.debug = False
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()
        newUser = self.createNewUser(email=self.get_default_test_username(), new_password=self.get_default_test_password(), first_name=self.get_default_test_name(), last_name=self.get_default_test_name(), active=True, confirmed_at=True, next_pay_date=True)
        self.set_user_id(newUser.id)

    def tearDown(self):
        #Bill.query.filter(models.User.first_name=self.get_default_test_name()).delete()
        for row in User.query.filter_by(first_name=self.get_default_test_name(), last_name=self.get_default_test_name()):
            db_session.delete(row)

        db_session.commit()
        db_session.remove()
        self.logout()

    @unittest.skip("testing skipping")
    def test_api_me_post(self):
        self.login(self.get_default_test_username(), self.get_default_test_password())
        benchmark = 0.012

        y = 100

        t0 = time.time()
        for x in range(0, y):
            self.apiCreateNewUser(email=testUtils.random_email_generator(), new_password=self.get_default_test_password())
        t1 = time.time()
        total1 = t1-t0

        t0 = time.time()
        for x in range(0, y):
            self.apiCreateNewUser(email=testUtils.random_email_generator(), new_password=self.get_default_test_password())
        t1 = time.time()
        total2 = t1-t0

        t0 = time.time()
        for x in range(0, y):
            self.apiCreateNewUser(email=testUtils.random_email_generator(), new_password=self.get_default_test_password())
        t1 = time.time()
        total3 = t1-t0

        average = ((total1/y)+(total2/y)+(total3/y))/3

        print "User Average: " + str(average)
        print "User Percent Variance: "+ str(testUtils.percent_difference(benchmark,average))+"%"

        assert testUtils.percent_difference(benchmark,average) < 10

        self.logout()

    @unittest.skip("testing skipping")
    def test_api_bill_post(self):
        self.login(self.get_default_test_username(), self.get_default_test_password())
        benchmark = 0.015

        y = 100

        t0 = time.time()
        for x in range(0, y):
            self.apiCreateNewBill(testUtils.random_name_generator(), testUtils.random_number_generator())
        t1 = time.time()
        total1 = t1-t0

        t0 = time.time()
        for x in range(0, y):
            self.apiCreateNewBill(testUtils.random_name_generator(), testUtils.random_number_generator())
        t1 = time.time()
        total2 = t1-t0

        t0 = time.time()
        for x in range(0, y):
            self.apiCreateNewBill(testUtils.random_name_generator(), testUtils.random_number_generator())
        t1 = time.time()
        total3 = t1-t0

        average = ((total1/y)+(total2/y)+(total3/y))/3

        print "Bill Average: " + str(average)
        print "Bill Percent Variance: "+ str(testUtils.percent_difference(benchmark,average))+"%"

        assert testUtils.percent_difference(benchmark,average) < 10

        self.logout()



if __name__ == '__main__':
    unittest.main()