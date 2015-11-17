import os
import json, string, random, unittest
from twoweeks import app
from twoweeks.database import init_db
from twoweeks.database import db_session
import twoweeks.config as config
from twoweeks.models import User, Bill, Role, Payment_Plan, Payment_Plan_Item, Feedback
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash







DEFAULT_ALPHABET_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DEFAULT_ALPHABET_LOWER = "abcdefghijklmnopqrstuvwxyz"
DEFAULT_ALPHABET_NUMERIC = "0123456789"
DEFAULT_ALPHABET_SPECIAL = "!#$%&'*+-/=?^_`{|}~@^%()<>.,"

DEFAULT_ALPHABET_ALPHA = DEFAULT_ALPHABET_UPPER+DEFAULT_ALPHABET_LOWER
DEFAULT_ALPHABET_ALPHANUMERIC = DEFAULT_ALPHABET_UPPER+DEFAULT_ALPHABET_LOWER+DEFAULT_ALPHABET_NUMERIC
DEFAULT_ALPHABET_ALL = DEFAULT_ALPHABET_UPPER+DEFAULT_ALPHABET_LOWER+DEFAULT_ALPHABET_NUMERIC+DEFAULT_ALPHABET_SPECIAL







def random_string_generator(alphabet, string_length):
    mypw = ""
    for i in range(string_length):
        next_index = random.randrange(len(alphabet))
        mypw = mypw + alphabet[next_index]
    return mypw

def random_password_generator():
    alphabet = DEFAULT_ALPHABET_ALL
    return random_string_generator(alphabet, 16)

def random_name_generator():
    alphabet = DEFAULT_ALPHABET_ALPHA
    return random_string_generator(alphabet, 12)

def random_email_generator():
    alphabet = DEFAULT_ALPHABET_ALPHANUMERIC+"!#$%&'*+-/=?^_`{|}~"
    return random_string_generator(alphabet, 12)+str('@mixfin.com')

def random_number_generator(max=None):
    if max is None:
        max = 1000
    return random.randint(1,max)

def dump_datetime(value):
    if value is None:
        return None
    return value.strftime("%Y-%m-%d") + "T" + value.strftime("%H:%M:%S")

def dump_date(value):
    if value is None:
        return None
    return value.strftime("%Y-%m-%d")







#DEFAULT VARIABLES TO BE RE-USED THROUGHOUT TEST CASES FOR CONSISTENCY
DEFAULT_TEST_PASSWORD=random_password_generator()
DEFAULT_TEST_NAME="~~~"+random_name_generator()+"~~~"
DEFAULT_TEST_USERNAME=random_email_generator()
DEFAULT_DATE = datetime.utcnow()







class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()
        newUser = User(username=DEFAULT_TEST_USERNAME, password=DEFAULT_TEST_PASSWORD, email=DEFAULT_TEST_USERNAME, first_name=DEFAULT_TEST_NAME, last_name=DEFAULT_TEST_NAME, next_pay_date=DEFAULT_DATE, pay_recurrance_flag = 'B',  confirmed_at=DEFAULT_DATE, active=True)
        db_session.add(newUser)
        db_session.commit()


    def creatNewUser(self, username, password):
        return self.app.post('api/me/', data=json.dumps(
            {'email':username,
             'confirm_email':username,
             'new_password':password,
             'confirm_new_password':password,
             'first_name': DEFAULT_TEST_NAME,
             'last_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')

    def creatNewBill(self, name, total_due=None):
        due_date = datetime.utcnow() + timedelta(days=random_number_generator(45))
        if total_due is None:
            total_due = random_number_generator()
        return self.app.post('api/bill/', data=json.dumps(
            {'name':name,
             'total_due': total_due,
             'due_date': due_date.strftime("%Y-%m-%d")}), content_type='application/json')

    def tearDown(self):
        #Bill.query.filter(models.User.first_name=DEFAULT_TEST_NAME).delete()
        for row in User.query.filter_by(first_name=DEFAULT_TEST_NAME, last_name=DEFAULT_TEST_NAME):
            db_session.delete(row)

        db_session.commit()
        db_session.remove()

    def login(self, username, password):
        return self.app.post('/api/login',data=json.dumps({'username': username,'password': password}), content_type='application/json')

    def logout(self):
        return self.app.get('/api/logout', follow_redirects=True)

    def test_api_login_and_logout(self):
        rv = self.login(DEFAULT_TEST_USERNAME, DEFAULT_TEST_PASSWORD)
        data = json.loads(rv.data)
        assert data['error'] is None

        rv = self.logout()
        data = json.loads(rv.data)
        assert data['error'] is None

    def test_api_me_post_success(self):
        email = random_email_generator()
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':email,
             'confirm_email':email,
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':DEFAULT_TEST_PASSWORD,
             'first_name': DEFAULT_TEST_NAME,
             'last_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')

        data = json.loads(rv.data)
        assert data['error'] is None

    def test_api_me_post_fail_password_compare(self):
        email = random_email_generator()
        wrongPassword = random_password_generator()
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':email,
             'confirm_email':email,
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':wrongPassword,
             'first_name': DEFAULT_TEST_NAME,
             'last_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Passwords do not match' in data['error']



    def test_api_me_post_fail_duplicate_email(self):
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':DEFAULT_TEST_USERNAME,
             'confirm_email':DEFAULT_TEST_USERNAME,
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':DEFAULT_TEST_PASSWORD,
             'first_name': DEFAULT_TEST_NAME,
             'last_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Username already exists' == data['error']




    def test_api_me_post_fail_required(self):

        #NO CONFIRM EMAIL
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':DEFAULT_TEST_USERNAME,
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':DEFAULT_TEST_PASSWORD,
             'first_name': DEFAULT_TEST_NAME,
             'last_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Email and confirmation email is required' == data['error']


        #NO EMAIL
        rv = self.app.post('api/me/', data=json.dumps(
            {'confirm_email':DEFAULT_TEST_USERNAME,
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':DEFAULT_TEST_PASSWORD,
             'first_name': DEFAULT_TEST_NAME,
             'last_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Email and confirmation email is required' == data['error']


        #NO FIRST NAME
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':DEFAULT_TEST_USERNAME,
             'confirm_email':DEFAULT_TEST_USERNAME,
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':DEFAULT_TEST_PASSWORD,
             'last_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'First and last name is required' == data['error']


        #NO LAST NAME
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':DEFAULT_TEST_USERNAME,
             'confirm_email':DEFAULT_TEST_USERNAME,
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':DEFAULT_TEST_PASSWORD,
             'first_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'First and last name is required' == data['error']


        #NO PAY RECURRANCE DATE
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':DEFAULT_TEST_USERNAME,
             'confirm_email':DEFAULT_TEST_USERNAME,
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':DEFAULT_TEST_PASSWORD,
             'first_name': DEFAULT_TEST_NAME,
             'last_name': DEFAULT_TEST_NAME,
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Pay Recurrance and Next Pay Date is Required' == data['error']


        #NO LAST NAME
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':DEFAULT_TEST_USERNAME,
             'confirm_email':DEFAULT_TEST_USERNAME,
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':DEFAULT_TEST_PASSWORD,
             'first_name': DEFAULT_TEST_NAME,
             'last_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B'}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Pay Recurrance and Next Pay Date is Required' == data['error']



    def test_api_me_put_change_password(self):
        password = random_password_generator()
        wrongPassword = random_password_generator()
        username = random_email_generator()
        rv = self.creatNewUser(username, DEFAULT_TEST_PASSWORD)

        self.login(username, DEFAULT_TEST_PASSWORD)

        rv = self.app.put('api/me/', data=json.dumps(
            {'email':username,
             'current_password': wrongPassword,
             'new_password':password,
             'confirm_new_password':password}), content_type='application/json')
        data = json.loads(rv.data)
        assert data['error'] is not None


        rv = self.app.put('api/me/', data=json.dumps(
            {'email':username,
             'current_password': DEFAULT_TEST_PASSWORD,
             'new_password':password,
             'confirm_new_password':wrongPassword}), content_type='application/json')
        data = json.loads(rv.data)
        assert data['error'] is not None


        rv = self.app.put('api/me/', data=json.dumps(
            {'email':username,
             'current_password': DEFAULT_TEST_PASSWORD,
             'new_password':password,
             'confirm_new_password':password}), content_type='application/json')
        data = json.loads(rv.data)
        assert data['error'] is None

        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.verify_password(password)

        self.logout()

        rv = self.login(username, DEFAULT_TEST_PASSWORD)
        data = json.loads(rv.data)
        assert data['error'] is not None

        rv = self.login(username, password)
        data = json.loads(rv.data)
        assert data['error'] is None

        self.logout()



    def test_api_me_get(self):
        self.login(DEFAULT_TEST_USERNAME, DEFAULT_TEST_PASSWORD)
        rv = self.app.get('/api/me/')
        assert rv.data is not None

        username = None
        email = None
        first_name = None
        last_name = None
        next_pay_date = None
        pay_recurrance_flag = None

        data = json.loads(rv.data)
        #print(data['data'][0])
        for key,value in data['data'][0].iteritems():
            #print(key+'-'+str(value))
            if key == 'email':
                email = value
                username = value
            elif key == 'first_name':
                first_name = value
            elif key == 'last_name':
                last_name = value
            elif key == 'next_pay_date':
                next_pay_date = value
            elif key == 'pay_recurrance_flag':
                pay_recurrance_flag = value
            elif key == 'average_paycheck_amount':
                average_paycheck_amount = value
            elif key == 'account_balance_amount':
                account_balance_amount = value

        assert first_name == DEFAULT_TEST_NAME
        assert last_name == DEFAULT_TEST_NAME
        assert email == DEFAULT_TEST_USERNAME
        assert username == DEFAULT_TEST_USERNAME

        #NOTE: Set to >= to account for lag
        assert str(next_pay_date) >= dump_datetime(DEFAULT_DATE)

        assert pay_recurrance_flag == 'B'

        self.logout()




    def test_api_bill_post_success(self):
        username = random_email_generator()
        bill_name = random_name_generator()
        self.creatNewUser(username, DEFAULT_TEST_PASSWORD)
        self.login(username, DEFAULT_TEST_PASSWORD)

        rv = self.creatNewBill(bill_name, DEFAULT_TEST_PASSWORD)
        assert rv.data is not None
        data = json.loads(rv.data)
        assert data['error'] is None

        self.logout()




if __name__ == '__main__':
    unittest.main()