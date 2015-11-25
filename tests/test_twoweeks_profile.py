import os
import json, string, random, unittest, cProfile
from twoweeks import app
from twoweeks.database import init_db
from twoweeks.database import db_session
import twoweeks.config as config
from twoweeks.models import User, Bill, Role, Payment_Plan, Payment_Plan_Item, Feedback
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import testUtils
from pstats import Stats

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



    def login(self, username, password):
        return self.app.post('/api/login',data=json.dumps({'username': username,'password': password}), content_type='application/json')

    def logout(self):
        return self.app.get('/api/logout', follow_redirects=True)


    @unittest.skip("testing skipping")
    def test_api_me_post_success(self):
        self.login(self.get_default_test_username(), self.get_default_test_password())

        self.pr = cProfile.Profile()
        self.pr.enable()

        #CREATING y BILLS
        for x in range(0, 100):
            self.apiCreateNewBill(testUtils.random_name_generator(), testUtils.random_number_generator())

        p = Stats (self.pr)
        p.strip_dirs()
        p.sort_stats ('cumtime')
        p.print_stats ()

        self.logout()

if __name__ == '__main__':
    unittest.main()