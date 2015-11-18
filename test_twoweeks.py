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
        self.set_default_test_password(random_password_generator())
        self.set_default_test_name("~~~"+random_name_generator()+"~~~")
        self.set_default_test_username(random_email_generator())
        self.set_default_test_date(datetime.utcnow())

        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()
        newUser = self.createNewUser(email=self.get_default_test_username(), password=self.get_default_test_password(), first_name=self.get_default_test_name(), last_name=self.get_default_test_name(), active=True, confirmed_at=True, next_pay_date=True)
        self.set_user_id(newUser.id)

    def tearDown(self):
        #Bill.query.filter(models.User.first_name=self.get_default_test_name()).delete()
        for row in User.query.filter_by(first_name=self.get_default_test_name(), last_name=self.get_default_test_name()):
            db_session.delete(row)

        db_session.commit()
        db_session.remove()
        self.logout()

    def apiCreateNewUser(self, **kwargs):
        password = kwargs.get('password')
        email = kwargs.get('email')
        first_name = self.default_test_name
        last_name = self.default_test_name
        next_pay_date = kwargs.get('next_pay_date')
        pay_recurrance_flag = kwargs.get('pay_recurrance_flag')
        confirmed_at = kwargs.get('confirmed_at')

        if email is None:
            email = random_name_generator()

        if password is None:
            password = random_password_generator()

        if isinstance(next_pay_date, datetime):
            next_pay_date = next_pay_date.strftime("%Y-%m-%d")
        elif next_pay_date is True:
            next_pay_date = self.get_default_test_date().strftime("%Y-%m-%d")
        elif next_pay_date is False:
            next_pay_date = None
        else:
            next_pay_date = self.get_default_test_date().strftime("%Y-%m-%d")

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
             'confirm_new_password':password,
             'first_name': first_name,
             'last_name': last_name,
             'confirmed_at': confirmed_at,
             'pay_recurrance_flag': pay_recurrance_flag,
             'next_pay_date': next_pay_date}), content_type='application/json')

    def createNewUser(self, **kwargs):
        password = kwargs.get('password')
        email = kwargs.get('email')
        first_name = self.default_test_name
        last_name = self.default_test_name
        next_pay_date = kwargs.get('next_pay_date')
        pay_recurrance_flag = kwargs.get('pay_recurrance_flag')
        confirmed_at = kwargs.get('confirmed_at')
        active = kwargs.get('active')

        if email is None:
            email = random_email_generator()

        if password is None:
            password = random_password_generator()

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
        due_date = datetime.utcnow() + timedelta(days=random_number_generator(45))
        if total_due is None:
            total_due = random_number_generator()
        return self.app.post('api/bill/', data=json.dumps(
            {'name':name,
             'total_due': total_due,
             'due_date': due_date.strftime("%Y-%m-%d")}), content_type='application/json')


    def login(self, username, password):
        return self.app.post('/api/login',data=json.dumps({'username': username,'password': password}), content_type='application/json')

    def logout(self):
        return self.app.get('/api/logout', follow_redirects=True)

    def test_api_login_and_logout(self):
        rv = self.login(self.get_default_test_username(), self.get_default_test_password())
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
             'new_password':self.get_default_test_password(),
             'confirm_new_password':self.get_default_test_password(),
             'first_name': self.get_default_test_name(),
             'last_name': self.get_default_test_name(),
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
             'new_password':self.get_default_test_password(),
             'confirm_new_password':wrongPassword,
             'first_name': self.get_default_test_name(),
             'last_name': self.get_default_test_name(),
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Passwords do not match' in data['error']

    def test_api_me_post_fail_duplicate_email(self):
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':self.get_default_test_username(),
             'confirm_email':self.get_default_test_username(),
             'new_password':self.get_default_test_password(),
             'confirm_new_password':self.get_default_test_password(),
             'first_name': self.get_default_test_name(),
             'last_name': self.get_default_test_name(),
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Username already exists' == data['error']

    def test_api_me_post_fail_required(self):

        #NO CONFIRM EMAIL
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':self.get_default_test_username(),
             'new_password':self.get_default_test_password(),
             'confirm_new_password':self.get_default_test_password(),
             'first_name': self.get_default_test_name(),
             'last_name': self.get_default_test_name(),
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Email and confirmation email is required' == data['error']

        #NO EMAIL
        rv = self.app.post('api/me/', data=json.dumps(
            {'confirm_email':self.get_default_test_username(),
             'new_password':self.get_default_test_password(),
             'confirm_new_password':self.get_default_test_password(),
             'first_name': self.get_default_test_name(),
             'last_name': self.get_default_test_name(),
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Email and confirmation email is required' == data['error']

        #NO FIRST NAME
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':self.get_default_test_username(),
             'confirm_email':self.get_default_test_username(),
             'new_password':self.get_default_test_password(),
             'confirm_new_password':self.get_default_test_password(),
             'last_name': self.get_default_test_name(),
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'First and last name is required' == data['error']

        #NO LAST NAME
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':self.get_default_test_username(),
             'confirm_email':self.get_default_test_username(),
             'new_password':self.get_default_test_password(),
             'confirm_new_password':self.get_default_test_password(),
             'first_name': self.get_default_test_name(),
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'First and last name is required' == data['error']

        #NO PAY RECURRANCE DATE
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':self.get_default_test_username(),
             'confirm_email':self.get_default_test_username(),
             'new_password':self.get_default_test_password(),
             'confirm_new_password':self.get_default_test_password(),
             'first_name': self.get_default_test_name(),
             'last_name': self.get_default_test_name(),
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Pay Recurrance and Next Pay Date is Required' == data['error']

        #NO LAST NAME
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':self.get_default_test_username(),
             'confirm_email':self.get_default_test_username(),
             'new_password':self.get_default_test_password(),
             'confirm_new_password':self.get_default_test_password(),
             'first_name': self.get_default_test_name(),
             'last_name': self.get_default_test_name(),
             'pay_recurrance_flag': 'B'}), content_type='application/json')
        data = json.loads(rv.data)
        assert 'Pay Recurrance and Next Pay Date is Required' == data['error']

    def test_api_me_put_change_password(self):
        password = random_password_generator()
        wrongPassword = random_password_generator()
        username = random_email_generator()
        rv = self.apiCreateNewUser(email = username, password = self.get_default_test_password())

        self.login(username, self.get_default_test_password())

        rv = self.app.put('api/me/', data=json.dumps(
            {'email':username,
             'current_password': wrongPassword,
             'new_password':password,
             'confirm_new_password':password}), content_type='application/json')
        data = json.loads(rv.data)
        assert data['error'] is not None

        rv = self.app.put('api/me/', data=json.dumps(
            {'email':username,
             'current_password': self.get_default_test_password(),
             'new_password':password,
             'confirm_new_password':wrongPassword}), content_type='application/json')
        data = json.loads(rv.data)
        assert data['error'] is not None

        rv = self.app.put('api/me/', data=json.dumps(
            {'email':username,
             'current_password': self.get_default_test_password(),
             'new_password':password,
             'confirm_new_password':password}), content_type='application/json')
        data = json.loads(rv.data)
        assert data['error'] is None

        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.verify_password(password)

        self.logout()

        rv = self.login(username, self.get_default_test_password())
        data = json.loads(rv.data)
        assert data['error'] is not None

        rv = self.login(username, password)
        data = json.loads(rv.data)
        assert data['error'] is None

        self.logout()

    def test_api_me_get(self):
        self.login(self.get_default_test_username(), self.get_default_test_password())
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

        assert first_name == self.get_default_test_name()
        assert last_name == self.get_default_test_name()
        assert email == self.get_default_test_username()
        assert username == self.get_default_test_username()

        #NOTE: Set to >= to account for lag
        assert str(next_pay_date) >= dump_datetime(self.get_default_test_date())

        assert pay_recurrance_flag == 'B'
        self.logout()

    def test_api_confirm_email_post(self):
        username = random_email_generator()
        rv = self.apiCreateNewUser(email = username, password = self.get_default_test_password())
        data = json.loads(rv.data)
        if data['error'] is not None:
            print data['error']
        assert data['error'] is None

        self.login(username, self.get_default_test_password())
        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.confirmed_at is None

        oldToken = user.confirm_token

        rv = self.app.post('api/confirm_email')
        data = json.loads(rv.data)
        if data['error'] is not None:
            print data['error']
        assert data['error'] is None

        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.confirm_token != oldToken

        self.logout()

    def test_api_confirm_email_put(self):
        username = random_email_generator()
        self.apiCreateNewUser(email=username, password=self.get_default_test_password())
        self.login(username, self.get_default_test_password())
        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.confirmed_at is None

        #FIRST WE TEST A FAILURE USING A BAD TOKEN
        rv = self.app.put('api/confirm_email/', data=json.dumps(
            {'user_id':user.id, 'email_token':'blahblahblah'}), content_type='application/json')

        data = json.loads(rv.data)
        assert data['error'] == 'Incorrect token was provided'

        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.confirm_token is not None
        assert user.confirmed_at is None

        #NOW WE TEST A GOOD TOKEN
        rv = self.app.put('api/confirm_email/', data=json.dumps(
            {'user_id':user.id, 'email_token':str(user.confirm_token)}), content_type='application/json')

        data = json.loads(rv.data)
        if data['error'] is not None:
            print data['error']
        assert data['error'] is None

        user = User.query.filter_by(username=username).first()
        assert user is not None
        assert user.confirm_token is None
        assert user.confirmed_at is not None

        self.logout()

    def test_api_bill_post_success(self):
        bill_name = random_name_generator()
        self.login(self.get_default_test_username(), self.get_default_test_password())

        rv = self.apiCreateNewBill(bill_name)
        assert rv.data is not None
        data = json.loads(rv.data)
        assert data['error'] is None
        self.logout()

    def test_api_bill_post_fail_no_name(self):
        self.login(self.get_default_test_username(), self.get_default_test_password())

        rv = self.apiCreateNewBill(None)
        assert rv.data is not None
        data = json.loads(rv.data)
        assert data['error'] is not None
        assert data['data'] is None
        self.logout()

    def test_api_bill_get_single(self):
        bill_name = random_name_generator()
        bill_total_due = random_number_generator()
        self.login(self.get_default_test_username(), self.get_default_test_password())
        self.apiCreateNewBill(bill_name, bill_total_due)
        bill = Bill.query.filter_by(name=bill_name, user_id=self.get_user_id()).first()
        assert bill is not None

        rv = self.app.get('/api/bill/'+str(bill.id))
        data = json.loads(rv.data)
        assert data['error'] is None
        assert data['data'] is not None

        payee_id = None
        name = None
        description = None
        due_date = None
        billing_period = None
        total_due = None
        paid_flag = None
        paid_date = None
        check_number = None
        payment_type = None
        payment_type_ind = None
        payment_processing_flag = None

        data = json.loads(rv.data)
        #print(data['data'][0])
        for key,value in data['data'][0].iteritems():
            #print(key+'-'+str(value))
            if key == 'name':
                name = value
            if key == 'description':
                description = value
            elif key == 'due_date':
                due_date = value
            elif key == 'billing_period':
                billing_period = value
            elif key == 'total_due':
                total_due = value
            elif key == 'paid_flag':
                paid_flag = value
            elif key == 'paid_date':
                paid_date = value
            elif key == 'check_number':
                check_number = value
            elif key == 'payment_type':
                payment_type = value
            elif key == 'payment_type_ind':
                payment_type = value
            elif key == 'payment_processing_flag':
                payment_processing_flag = value

        assert bill_name == name
        assert total_due == bill_total_due
        assert check_number is None
        assert paid_flag is False
        #NOTE: Set to >= to account for lag
        assert due_date is not None
        assert payment_processing_flag is False
        assert description is None
        assert paid_date is None

        self.logout()

    def test_api_bill_get_multiple(self):
        self.login(self.get_default_test_username(), self.get_default_test_password())

        #SETTING TOTAL NUMBER TO ATTEMPT TO CREATE
        y = 3

        #CREATING y BILLS
        for x in range(0, y):
            self.apiCreateNewBill(random_name_generator(), random_number_generator())

        rv = self.app.get('/api/bill/')
        data = json.loads(rv.data)
        assert data['error'] is None
        assert data['data'] is not None

        datas = json.loads(rv.data)
        #print(data['data'][0])

        assert len(datas['data']) == y

        for data in datas['data']:
            payee_id = None
            name = None
            description = None
            due_date = None
            billing_period = None
            total_due = None
            paid_flag = None
            paid_date = None
            check_number = None
            payment_type = None
            payment_type_ind = None
            payment_processing_flag = None

            for key,value in data.iteritems():
                #print(key+'-'+str(value))
                if key == 'name':
                    name = value
                if key == 'description':
                    description = value
                elif key == 'due_date':
                    due_date = value
                elif key == 'billing_period':
                    billing_period = value
                elif key == 'total_due':
                    total_due = value
                elif key == 'paid_flag':
                    paid_flag = value
                elif key == 'paid_date':
                    paid_date = value
                elif key == 'check_number':
                    check_number = value
                elif key == 'payment_type':
                    payment_type = value
                elif key == 'payment_type_ind':
                    payment_type = value
                elif key == 'payment_processing_flag':
                    payment_processing_flag = value

            #assert bill_name == name
            #assert total_due == bill_total_due
            assert check_number is None
            assert paid_flag is False
            #NOTE: Set to >= to account for lag
            assert due_date is not None
            assert payment_processing_flag is False
            assert description is None
            assert paid_date is None

        self.logout()



if __name__ == '__main__':
    unittest.main()