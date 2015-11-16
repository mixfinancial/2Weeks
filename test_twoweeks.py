import os
import json
from twoweeks import app
from twoweeks.database import init_db
import twoweeks.config as config
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])


    def login(self, username, password):
        return self.app.post('/api/login',data=json.dumps({'username': username,'password': password}), content_type='application/json')

    def logout(self):
        return self.app.get('/api/logout', follow_redirects=True)


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