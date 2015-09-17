__author__ = 'davidlarrimore'

import json
from datetime import datetime

from flask import Flask, render_template, request, jsonify, abort, g , flash, url_for, redirect, session
import twoweeks.config as config
from datetime import timedelta




######################
# BASE CONFIGURATION #
######################

app = Flask(__name__)

app.debug = config.DEBUG
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config['TRAP_BAD_REQUEST_ERRORS'] = config.TRAP_BAD_REQUEST_ERRORS


# API CONFIG
from flask_restful import Resource, Api
api = Api(app)




##########################
# DATABASE CONFIGURATION #
##########################
from twoweeks.database import init_db
from twoweeks.database import db_session
from twoweeks.models import User, Bill, Role, Funds_Transfer, Bill_Funding_Item

init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



#######################
# EMAIL CONFIGURATION #
#######################
from threading import Thread
from flask.ext.mail import Mail, Message
from .decorators import async

app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER

mail = Mail(app)

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()



#TODO: LOGGING
#logging.basicConfig(filename='twoweeks.log',level=logging.DEBUG)



##################
# AUTHENTICATION #
##################
app.permanent_session_lifetime = timedelta(minutes=config.PERMANENT_SESSION_LIFETIME)


from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user, login_required
import base64

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id = user_id).first()


@app.route('/login')
def login():
    return '''
        <form action="/login/check" method="post">
            <p>Username: <input name="username" type="text"></p>
            <p>Password: <input name="password" type="password"></p>
            <input type="submit">
        </form>
    '''


@app.route('/login/check', methods=['post'])
def login_check():
    app.logger.info('User:' + request.form['username'] + ' attempting to login')
    # validate username and password
    if (request.form['username'] is not None and request.form['password'] is not None):
        user = User.query.filter_by(username = request.form['username']).first()
        app.logger.info(user.id);
        if (user is not None and user.verify_password(request.form['password'])):
            app.logger.info('Login Successful')
            login_user(user)
        else:
            app.logger.info('Username or password incorrect')
    else:
        app.logger.info('Please provide a username and password')

    return redirect(url_for('home'))



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('/'))


@app.route('/adminLogout')
def adminLogout():
    logout_user()
    return redirect(url_for('/admin/'))




#APILOGIN
class ApiLogin(Resource):
    def post(self):
        username = None
        password = None
        app.logger.info(request.accept_mimetypes)
        if request_is_json():
            app.logger.info('Attempting to login using JSON')
            data = request.get_json()
            app.logger.info(request.data)
            for key,value in data.iteritems():
                print key+'-'+value
                if key == 'username':
                    username = value
                if key == 'password':
                    password = value
        elif request_is_form_urlencode():
            app.logger.info('Attempting to login using x-www-form-urlencoded')
            requestData = json.loads(request.form['data'])
            username = requestData['email']
            password = requestData['password']
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ request.accept_mimetypes}


        # validate username and password
        if (username is not None and password is not None):
            user = User.query.filter_by(username = username).first()
            if (user is not None and user.verify_password(password)):
                app.logger.info('Login Successful')
                login_user(user)
                session['username']=username;
                return {"meta":buildMeta(), "data": None}
            else:
                app.logger.info('Username or password incorrect')
                return {"meta":buildMeta(), "error":"Username or password incorrect", "data": None}
        else:
            app.logger.info('Please provide a username and password')
            return {"meta":buildMeta(), "error":"Please provide a username and password", "data": None}


        return {"meta":buildMeta()}

api.add_resource(ApiLogin, '/api/login')




#APILOGOUT
class ApiLogout(Resource):
    def get(self):
        logout_user()
        return {"meta":buildMeta(), "error":"none", "data": ""}
api.add_resource(ApiLogout, '/api/logout/')



@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None



@login_manager.unauthorized_handler
def unauthorized_callback():
    app.logger.info(request)
    if '/admin' not in str(request):
        return redirect('/')
    else:
        return redirect('/admin/')



@app.route('/api/token')
@login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })






###############
# Base Routes #
###############

@app.route('/')
def index():
    #send_email('Test', ['david.larrimore@mixfin.com'], 'Test Flask Email', 'Test Flask Email')
    return render_template('index.html')

@app.route('/home/')
@login_required
def home():
    return render_template('home.html')

@app.route('/admin/')
def adminLogin():
    return render_template('adminLogin.html')


@app.route('/admin/home/')
@login_required
def adminHome():
    return render_template('admin.html')









############
# USER API #
############

#USERS
class ApiUser(Resource):
    @login_required
    def get(self, user_id=None):
        userID = None;

        if user_id is not None:
            userID = user_id
        elif request.args.get('user_id') is not None:
            userID = request.args.get('user_id')

        if userID is not None:
            app.logger.info("looking for user:" + userID)
            user = User.query.filter_by(id=userID).first()
            app.logger.info(user)

            if user is None:
                return {"meta":buildMeta(),"error": "No results returned for user id #"+ userID, "data": None}
            else:
                return jsonify(meta=buildMeta(), data=[user.serialize])
        else:
            users = [i.serialize for i in User.query.all()]
            #TODO: DO NOT RETURN PASSWORDS
            return {"meta":buildMeta(), "data":users}

    @login_required
    def put(self, user_id=None):
        app.logger.info('Accessing User.put')
        id = ''
        username = ''
        new_password = ''
        confirm_password = ''
        email = ''
        first_name = ''
        last_name = ''
        role_id = ''

        if user_id is not None:
            id = user_id
        elif request.args.get('user_id') is not None:
            id = request.args.get('user_id')


        user = User.query.filter_by(id=user_id).first()

        if user is not None:
            if request_is_json():
                app.logger.info('Updating user based upon JSON Request')
                print json.dumps(request.get_json())
                data = request.get_json()
                for key,value in data.iteritems():
                    print key+'-'+value
                    if key == 'new_password':
                        new_password = value
                    if key == 'confirm_password':
                        confirm_password = value
                    elif key == 'email':
                        email = value
                        username = value
                        user.username = value
                        user.email = value
                    elif key == 'first_name':
                        first_name = value
                        user.first_name = value
                    elif key == 'last_name':
                        last_name = value
                        user.last_name = value
            elif request_is_form_urlencode():
                # TODO: Handle nulls
                app.logger.info('Updating user '+username)
                requestData = json.loads(request.form['data'])
                user.username = requestData['email']
                user.email = requestData['email']
                user.last_name = requestData['last_name']
                user.first_name = requestData['first_name']
                confirm_password = requestData['confirm_password']
                password = requestData['password']
            else:
                return {"meta":buildMeta(), "error":"Unable to process "+ request.accept_mimetypes}

        else:
            return {"meta":buildMeta(), "error":"Could not find user id #"+id, "data": None}

        #TODO: PASSWORD and CONFIRM_PASSWORD comparison

        db_session.commit()
        return {"meta":buildMeta(), "data": "Updated Record with ID " + user_id, "data": None}


    @login_required
    def post(self, user_id=None):
        app.logger.info('Accessing User.post')

        username = ''
        password = ''
        confirm_password = ''
        email = ''
        first_name = ''
        last_name = ''
        role_id = ''

        if request_is_json():
            app.logger.info('Creating new user based upon JSON Request')
            print json.dumps(request.get_json())
            data = request.get_json()
            for key,value in data.iteritems():
                print key+'-'+value
                if key == 'password':
                    password = value
                if key == 'confirm_password':
                    confirm_password = value
                elif key == 'email':
                    username = value
                    email = value
                elif key == 'first_name':
                    first_name = value
                elif key == 'last_name':
                    last_name = value
        elif request_is_form_urlencode():
            app.logger.info('Creating new user based upon other Request')
            requestData = json.loads(request.form['data'])
            username = requestData['email']
            email = requestData['email']
            last_name = requestData['last_name']
            first_name = requestData['first_name']
            confirm_password = requestData['confirm_password']
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ request.accept_mimetypes}

        #TODO: PASSWORD and CONFIRM_PASSWORD comparison
        if email is None or password is None:
            return {"meta":buildMeta(), "error":"Email and Password is required", "data": None}

        if User.query.filter_by(username = username).first() is not None:
            return {"meta":buildMeta(), "error":"Username already exists", "data": None}

        newUser = User(username=username, password=password, email=email, first_name=first_name, last_name=last_name)

        db_session.add(newUser)
        db_session.commit()

        return {"meta":buildMeta()}

    @login_required
    def delete(self, user_id):
        app.logger.info("Deleting User #: " + user_id)
        user = User.query.filter_by(id=user_id).first()
        db_session.delete(user)
        db_session.commit()

        return {"meta":buildMeta(), "data": None}

api.add_resource(ApiUser, '/api/user', '/api/user/', '/api/user/<string:user_id>', '/api/users/', '/api/users/<string:user_id>')










############
# BILL API #
############

class ApiBill(Resource):
    @login_required
    def get(self, bill_id=None):
        billId = None;

        #TODO: BIND Bill with User ID based upon session
        if bill_id is not None:
            billId = bill_id
        elif request.args.get('user_id') is not None:
            billId = request.args.get('user_id')

        if billId is not None:
            app.logger.info("looking for bill:" + billId)
            bill = Bill.query.filter_by(id=billId).first()
            app.logger.info(bill)

            if bill is None:
                return {"meta":buildMeta(), 'data':[]}
            else:
                return jsonify(meta=buildMeta(), data=[bill.serialize])
        else:
            bills = [i.serialize for i in Bill.query.all()]
            return {"meta":buildMeta(), "data":bills}

    @login_required
    def put(self, bill_id=None):
        app.logger.info('Accessing Bill.put')

        #TODO: Handle update
        user_id = None
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

        user = None

        if 'username' in session:
            user=User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}

        if bill_id is not None:
            id = bill_id
        elif request.args.get('user_id') is not None:
            id = request.args.get('user_id')


        bill = Bill.query.filter_by(id=bill_id).first()
        bill.user_id = user.id

        if bill is not None:
            if request_is_json():
                app.logger.info('Updating bill based upon JSON Request')
                print json.dumps(request.get_json())
                data = request.get_json()
                for key,value in data.iteritems():
                    print key+'-'+value
                    if key == 'name':
                        bill.name = value
                    if key == 'description':
                        bill.description = value
                    elif key == 'due_date':
                        bill.due_date = value
                    elif key == 'billing_period':
                        bill.billing_period = value
                    elif key == 'total_due':
                        bill.total_due = value
                    elif key == 'paid_flag':
                        bill.paid_flag = value
                    elif key == 'paid_date':
                        bill.paid_date = value
                    elif key == 'check_number':
                        bill.check_number = value
                    elif key == 'payment_type':
                        bill.payment_type = value
            elif request_is_form_urlencode():
                app.logger.info('Updating bill #'+bill_id)
                requestData = json.loads(request.form['data'])

                bill.name = requestData['name']
                bill.description = requestData['description']
                bill.due_date = requestData['due_date']
                bill.billing_period = requestData['billing_period']
                bill.total_due = requestData['total_due']
                bill.paid_flag = requestData['paid_flag']
                bill.paid_date = requestData['paid_date']
                bill.check_number = requestData['check_number']
                bill.payment_type = requestData['payment_type']

            else:
                return {"meta":buildMeta(), "error":"Unable to process "+ request.accept_mimetypes}

        else:
            return {"meta":buildMeta(), "error":"Could not find bill id #"+id}

        #TODO: PASSWORD and CONFIRM_PASSWORD comparison

        db_session.commit()
        return {"meta":buildMeta(), "data": bill.serialize}, 201

    @login_required
    def post(self, bill_id=None):
        app.logger.info('Accessing Bill.post')

        user = None

        user_id = None
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




        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()

        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}

        if request_is_json():
            app.logger.info('Creating new user based upon JSON Request')
            print json.dumps(request.get_json())
            data = request.get_json()
            for key,value in data.iteritems():
                print key+'-'+value
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
        elif request_is_form_urlencode():
            app.logger.info('Creating new user based upon other Request')
            requestData = json.loads(request.form['data'])
            name = requestData['name']
            description = requestData['description']
            due_date = requestData['due_date']
            billing_period = requestData['billing_period']
            total_due = requestData['total_due']
            paid_flag = requestData['paid_flag']
            paid_date = requestData['paid_date']
            check_number = requestData['check_number']
            payment_type = requestData['payment_type']
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ request.accept_mimetypes}

        if Bill.query.filter_by(name = name, user_id = user_id).first() is not None:
            return {"meta":buildMeta(), "error":"Bill already exists"}

        newBill = Bill(user_id=user.id, name=name, description=description, due_date=due_date, billing_period=billing_period, total_due=total_due, paid_flag=paid_flag, paid_date=paid_date, payment_type=payment_type, check_number=check_number)

        db_session.add(newBill)
        db_session.commit()

        return {"meta":buildMeta(), 'data':newBill.serialize}, 201

    @login_required
    def delete(self, user_id):
        app.logger.info("Deleting User #: " + user_id)
        user = User.query.filter_by(id=user_id).first()
        db_session.delete(user)
        db_session.commit()

        return {"meta":buildMeta(), "data" : "Deleted Record with ID " + user_id}

api.add_resource(ApiBill, '/api/bill', '/api/bill/', '/api/bill/<string:bill_id>')




























####################
# HELPER FUNCTIONS #
####################

def request_is_json():
    if 'application/json' in request.accept_mimetypes:
        return True;
    else:
        return False



def request_is_form_urlencode():
    if 'application/x-www-form-urlencoded' in request.accept_mimetypes:
        return True;
    else:
        return False


def buildMeta():
    return [{"authors":["David Larrimore", "Robert Donovan"], "copyright": "Copyright 2015 MixFin LLC.", "version": "0.1"}]






########
# main #
########
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
