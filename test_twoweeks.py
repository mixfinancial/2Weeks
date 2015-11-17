import os
import json
from twoweeks import app
from twoweeks.database import init_db
from twoweeks.database import db_session
import twoweeks.config as config
from twoweeks.models import User, Bill, Role, Payment_Plan, Payment_Plan_Item, Feedback
from datetime import datetime
import unittest
import tempfile


#DEFAULT VARIABLES TO BE RE-USED THROUGHOUT TEST CASES FOR CONSISTENCY
DEFAULT_TEST_PASSWORD='12345678May!!!'
DEFAULT_TEST_NAME='xxxTESTxxx'
DEFAULT_TEST_USERNAME='d.avidlarrimore@gmail.com'




class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()
        newUser = User(username=DEFAULT_TEST_USERNAME, password=DEFAULT_TEST_PASSWORD, email=DEFAULT_TEST_USERNAME, first_name=DEFAULT_TEST_NAME, last_name=DEFAULT_TEST_NAME, next_pay_date = datetime.utcnow(), pay_recurrance_flag = 'B',  confirmed_at=datetime.utcnow(), active=True)
        db_session.add(newUser)
        db_session.commit()


    def tearDown(self):
        User.query.filter_by(first_name=DEFAULT_TEST_NAME, last_name=DEFAULT_TEST_NAME).delete()
        db_session.commit()
        db_session.remove()


    def login(self, username, password):
        return self.app.post('/api/login',data=json.dumps({'username': username,'password': password}), content_type='application/json')

    def logout(self):
        return self.app.get('/api/logout', follow_redirects=True)



    def test_register_user_success(self):
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':'d.a.vidlarrimore@gmail.com',
             'confirm_email':'d.a.vidlarrimore@gmail.com',
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':DEFAULT_TEST_PASSWORD,
             'first_name': DEFAULT_TEST_NAME,
             'last_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')

        data = json.loads(rv.data)
        assert data['error'] is None




    def test_register_user_fail_password_compare(self):
        rv = self.app.post('api/me/', data=json.dumps(
            {'email':'d.a.v.idlarrimore@gmail.com',
             'confirm_email':'d.a.v.idlarrimore@gmail.com',
             'new_password':DEFAULT_TEST_PASSWORD,
             'confirm_new_password':'notthetestpassword1!;lkj',
             'first_name': DEFAULT_TEST_NAME,
             'last_name': DEFAULT_TEST_NAME,
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')

        data = json.loads(rv.data)
        assert 'Passwords do not match' in data['error']




    def test_register_user_fail_duplicate_email(self):
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



    def test_empty_db(self):
        rv = self.app.get('/api/user/1')
        assert rv.data is not None


    def test_login_logout(self):
        rv = self.login(DEFAULT_TEST_USERNAME, DEFAULT_TEST_PASSWORD)
        data = json.loads(rv.data)
        assert data['error'] is None

        rv = self.logout()
        data = json.loads(rv.data)
        assert data['error'] is None



if __name__ == '__main__':
    unittest.main()