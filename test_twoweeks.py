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

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()




    def tearDown(self):
        user = User.query.filter_by(username='d.avidlarrimore@gmail.com').first()
        if user is not None:
            db_session.delete(user)

        db_session.remove()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])



    def login(self, username, password):
        return self.app.post('/api/login',data=json.dumps({'username': username,'password': password}), content_type='application/json')


    def logout(self):
        return self.app.get('/api/logout', follow_redirects=True)



    def test_register_user(self):
        return self.app.post('api/me/', data=json.dumps(
            {'email':'d.avidlarrimore@gmail.com',
             'new_password':'12345678May!!!',
             'confirm_new_password':'12345678May!!!',
             'first_name': 'david',
             'last_name': 'larrimore',
             'pay_recurrance_flag': 'B',
             'next_pay_date': datetime.utcnow().strftime("%Y-%m-%d")}), content_type='application/json')

        data = json.loads(rv.data)
        app.logger.debug(data['error'])
        assert data['error'] is None


    def test_empty_db(self):
        rv = self.app.get('/api/user/1')
        assert rv.data is not None


    def test_login_logout(self):
        rv = self.login(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)
        data = json.loads(rv.data)
        assert data['error'] is None

        rv = self.logout()
        data = json.loads(rv.data)
        assert data['error'] is None



if __name__ == '__main__':
    unittest.main()