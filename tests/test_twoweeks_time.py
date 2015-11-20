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

    def set_default_test_date(self, date):
        self.default_test_date = date

    def get_default_test_date(self):
        return self.default_test_date

    def set_default_test_username(self, username):
        self.default_test_username = username

    def get_default_test_username(self):
        return self.default_test_username

    def set_default_test_name(self, name):
        self.default_test_name = name

    def get_default_test_name(self):
        return self.default_test_name

    def set_default_test_password(self, password):
        self.default_test_password = password

    def get_default_test_password(self):
        return self.default_test_password

    def set_user_id(self, id):
        self.default_user_id = id

    def get_user_id(self):
        return self.default_user_id

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


    def apiCreateNewUser(self, **kwargs):
        password = kwargs.get('new_password')
        confirm_password = kwargs.get('confirm_new_password')
        email = kwargs.get('email')
        next_pay_date = kwargs.get('next_pay_date')
        pay_recurrance_flag = kwargs.get('pay_recurrance_flag')
        confirmed_at = kwargs.get('confirmed_at')

        if email is None:
            email = testUtils.random_name_generator()

        if password is None and confirm_password is None:
            val = testUtils.random_password_generator()
            password = val
            confirm_password = val

        if password == self.get_default_test_password() and confirm_password is None:
            confirm_password = self.get_default_test_password()

        if isinstance(next_pay_date, datetime):
            next_pay_date = next_pay_date
        elif next_pay_date is True:
            next_pay_date = self.get_default_test_date()
        elif next_pay_date is False:
            next_pay_date = None
        else:
            next_pay_date = self.get_default_test_date()

        if pay_recurrance_flag is None:
            pay_recurrance_flag = "B"

        if isinstance(confirmed_at, datetime):
            confirmed_at = confirmed_at
        if confirmed_at:
            confirmed_at = self.get_default_test_date()
        else:
            confirmed_at = None

        return self.app.post('api/me/', data=json.dumps(
            {'email':email,
             'confirm_email':email,
             'new_password':password,
             'confirm_new_password':confirm_password,
             'first_name': self.get_default_test_name(),
             'last_name': self.get_default_test_name(),
             'confirmed_at': testUtils.dump_date(confirmed_at),
             'pay_recurrance_flag': pay_recurrance_flag,
             'next_pay_date': testUtils.dump_date(next_pay_date)}), content_type='application/json')

    def createNewUser(self, **kwargs):
        password = kwargs.get('new_password')
        email = kwargs.get('email')
        next_pay_date = kwargs.get('next_pay_date')
        pay_recurrance_flag = kwargs.get('pay_recurrance_flag')
        confirmed_at = kwargs.get('confirmed_at')
        active = kwargs.get('active')

        if email is None:
            email = testUtils.random_email_generator()

        if password is None:
            password = testUtils.random_password_generator()

        if isinstance(next_pay_date, datetime):
            next_pay_date = next_pay_date
        elif next_pay_date is True:
            next_pay_date = self.get_default_test_date()
        elif next_pay_date is False:
            next_pay_date = None
        else:
            next_pay_date = self.get_default_test_date()

        if pay_recurrance_flag is None:
            pay_recurrance_flag = "B"

        if isinstance(confirmed_at, datetime):
            confirmed_at = confirmed_at
        elif confirmed_at is True:
            confirmed_at = self.get_default_test_date()
        elif confirmed_at is False:
            confirmed_at = None
        else:
            confirmed_at = None

        newUser = User(username=email, password=password, email=email, first_name=self.get_default_test_name(), last_name=self.get_default_test_name(), next_pay_date=next_pay_date, pay_recurrance_flag = pay_recurrance_flag,  confirmed_at=confirmed_at, active=active)
        db_session.add(newUser)
        db_session.commit()
        return newUser

    def apiCreateNewBill(self, name=None, total_due=None):
        due_date = datetime.utcnow() + timedelta(days=testUtils.random_number_generator(45))
        if total_due is None:
            total_due = testUtils.random_number_generator()
        return self.app.post('api/bill/', data=json.dumps(
            {'name':name,
             'total_due': total_due,
             'due_date': due_date.strftime("%Y-%m-%d")}), content_type='application/json')


    def login(self, username, password):
        return self.app.post('/api/login',data=json.dumps({'username': username,'password': password}), content_type='application/json')

    def logout(self):
        return self.app.get('/api/logout', follow_redirects=True)


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