__author__ = 'davidlarrimore'

import json
from datetime import datetime

from flask import Flask, render_template, request, jsonify, abort, g , flash, url_for, redirect, session, make_response
import twoweeks.config as config
from datetime import timedelta
from twoweeks.token import generate_confirmation_token, confirm_token


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
from twoweeks.models import User, Bill, Role, Payment_Plan, Payment_Plan_Item, Feedback
from sqlalchemy.sql import func

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

def send_email(subject, recipients, text_body=None, html_body=None):
    if app.config['TESTING'] is not True:
        msg = Message(subject, recipients=recipients)
        if text_body is not None:
            msg.body = text_body
        if html_body is not None:
            msg.html = html_body

        if text_body is not None and html_body is not None:
            thr = Thread(target=send_async_email, args=[app, msg])
            thr.start()

        app.logger.info("Sent Email")
    else:
        app.logger.debug("In Test mode. not sending email")



#TODO: LOGGING
#logging.basicConfig(filename='twoweeks.log',level=logging.DEBUG)



##################
# AUTHENTICATION #
##################
app.permanent_session_lifetime = timedelta(minutes=config.PERMANENT_SESSION_LIFETIME)
from werkzeug.security import generate_password_hash

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
            app.logger.info('User '+user.username+' is already logged in')
            login_user(user)
        else:
            app.logger.info('Username or password incorrect')
    else:
        app.logger.info('Please provide a username and password')

    return redirect(url_for('home'))


#APILOGIN
class ApiLoginCheck(Resource):
    @login_required
    def get(self):
        user = None
        if 'username' in session and session['username'] is not '':
            user=User.query.filter_by(username=session['username']).first()
            if user:
                return {"meta":buildMeta(), "error": None, "data":[user.serialize]}, 200
            else:
                return {"meta":buildMeta(), "error":"No Session Found for '"+session['username']+"'", "data":None}, 401
        else:
            return {"meta":buildMeta(), "error":"No Session Found", "data":None}, 401

api.add_resource(ApiLoginCheck, '/api/login_check', '/api/login_check/')








@app.route('/logout')
def logout():
    session['username']= ''
    logout_user()
    return redirect(url_for('/'))


@app.route('/adminLogout')
def adminLogout():
    session['username']= ''
    logout_user()
    return redirect(url_for('/admin/'))




#APILOGIN
class ApiLogin(Resource):
    def get(self):
        return {"meta":buildMeta(), "error":None, "data":None}, 200

    def post(self):
        #app.logger.info('Attempting to login user')
        username = None
        password = None
        #app.logger.info(str(request.content_type))
        if request_is_json():
            data = request.get_json()
            #app.logger.debug(request.data)
            for key,value in data.iteritems():
                #app.logger.debug(key+'-'+value)
                if key == 'username':
                    username = value
                if key == 'password':
                    password = value
        elif request_is_form_urlencode():
            requestData = json.loads(request.form['data'])
            username = requestData['email']
            password = requestData['password']
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type)}


        # validate username and password
        if (username is not None and password is not None):
            user = User.query.filter_by(username = username).first()
            if user is None:
                app.logger.debug('User Not Found')
            if (user is not None and user.verify_password(password)):
                app.logger.info('Successfully logged in as '+username)
                login_user(user)
                session['username']=username
                return {"meta":buildMeta(), "data": None, "error":None}, 200
            elif (config.DEBUG == True and username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD):
                app.logger.info('Attempting to login as root user')
                user = User.query.filter_by(username = username).first()
                if (user is None):
                    app.logger.info('No root user found, creating '+ config.ADMIN_USERNAME)
                    newUser = User(username=config.ADMIN_USERNAME, password=config.ADMIN_PASSWORD, email=config.ADMIN_EMAIL, first_name='Admin', last_name='Admin')
                    db_session.add(newUser)
                    db_session.commit()
                    login_user(newUser)
                    session['username']=username
                    return {"meta":buildMeta(), "data": None, "error":None}, 200
                else:
                    app.logger.info('Successfully logged in as '+username)
                    login_user(user)
                    session['username']=username
                    return {"meta":buildMeta(), "data": None, "error":None}, 200
            else:
                app.logger.info('User is None or Password did not verify')
                return {"meta":buildMeta(), "error":"Username or password incorrect", "data": None}, 403
        else:
            app.logger.info('Please provide a username and password')
            return {"meta":buildMeta(), "error":"Please provide a username and password", "data": None}, 403


        return {"meta":buildMeta(), "error":None, "data":None}, 201

api.add_resource(ApiLogin, '/api/login')




#APILOGOUT
class ApiLogout(Resource):
    def get(self):
        logout_user()
        session['username']= ''
        return {"meta":buildMeta(), "error":None, "data": None}, 200
api.add_resource(ApiLogout, '/api/logout', '/api/logout/')



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




# Unauthorized_handler is the action that is performed if user is not authenticated
@login_manager.unauthorized_handler
def unauthorized_callback():
    app.logger.info(request)
    if '/api' in str(request):
        return {"meta":buildMeta(), "error":"User is not authenticated, please login", "data":None}, 401
    elif '/admin' in str(request):
        return redirect('/admin/#/login')
    else:
        theURL = str(request.url)
        app.logger.info('theURL: ' + theURL)
        if "?" in theURL:
            urlParams = theURL[theURL.index('?'):len(theURL)]
            if urlParams is not None:
                app.logger.info('urlParams: ' + urlParams)
                return redirect('/#/'+urlParams+'&auth_check=true')
            else:
                return redirect('/#/login/')
        else:
            return redirect('/#/login/')




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
    return render_template('index.html')


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
                return {"meta":buildMeta(),"error": "No results returned for user id #"+ userID, "data":None}, 200
            else:
                return jsonify(meta=buildMeta(), data=[user.serialize])
        else:
            return {"meta":buildMeta(), "data":[i.serialize for i in User.query.all()], "error":None}, 200

    @login_required
    def put(self, user_id=None):
        app.logger.debug('Accessing User.put')
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
                app.logger.debug(json.dumps(request.get_json()))
                data = request.get_json()
                for key,value in data.iteritems():
                    #app.logger.debug(key+'-'+str(value))
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
            elif request.content_type is None:
                return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}
            else:
                return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}

        else:
            return {"meta":buildMeta(), "error":"Could not find user", "data": None}, 202

        #TODO: PASSWORD and CONFIRM_PASSWORD comparison

        db_session.commit()
        return {"meta":buildMeta(), "data": "Updated Record with ID " + user_id, "data": None}


    @login_required
    def post(self, user_id=None):
        app.logger.debug('Accessing User.post')

        username = ''
        password = ''
        confirm_password = ''
        email = ''
        first_name = ''
        last_name = ''
        role_id = ''

        if request_is_json():
            app.logger.info('Creating new user based upon JSON Request')
            app.logger.debug(json.dumps(request.get_json()))
            data = request.get_json()
            for key,value in data.iteritems():
                #app.logger.debug(key+'-'+str(value))
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
        elif request.content_type is None or not request.content_type:
            return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202

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
    def delete(self, user_id = None):

        if user_id is None:
            return {"meta":buildMeta(), "data": None, "error":"User ID is Required"}, 202

        app.logger.info("Deleting User #: " + user_id)
        user = User.query.filter_by(id=user_id).first()
        db_session.delete(user)
        db_session.commit()

        return {"meta":buildMeta(), "data":None, "error":None}, 200

api.add_resource(ApiUser, '/api/user', '/api/user/', '/api/user/<string:user_id>', '/api/users/', '/api/users/<string:user_id>')


















##########
# ME API #
##########

# the ME API covers the logged in user.
class ApiMe(Resource):
    @login_required
    def get(self, user_id=None):
        user = None

        if 'username' in session:
            user=User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403

        if user is None:
            return {"meta":buildMeta(),"error": "No results returned for "+ session['username'], "data": None}
        else:
            return {"meta":buildMeta(),"error": None, "data":[user.serialize]}, 200



    ####################
    # EDIT USER ACTION #
    ####################
    @login_required
    def put(self, user_id=None):
        app.logger.debug('Accessing User.put')
        id = ''
        username = None
        new_password = None
        current_password = None
        new_password = None
        confirm_new_password = None
        email = None
        first_name = None
        last_name = None
        account_balance_amount = None

        average_paycheck_amount = None
        next_pay_date = None
        pay_recurrance_flag = None


        if 'username' in session:
            user=User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403

        if user is not None:
            if request_is_json():
                app.logger.info('Updating user based upon JSON Request')
                app.logger.debug(json.dumps(request.get_json()))
                data = request.get_json()
                if data:
                    for key,value in data.iteritems():
                        #app.logger.debug(key+'-'+str(value))
                        if key == 'new_password':
                            new_password = value
                        elif key == 'current_password':
                            current_password = value
                        elif key == 'confirm_new_password':
                            confirm_new_password = value
                        elif key == 'email':
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
                else:
                    return {"meta":buildMeta(), "error":"No Data Sent", "data": None}
            elif request_is_form_urlencode():
                # TODO: Handle nulls
                app.logger.info('Updating user '+username)
                requestData = json.loads(request.form['data'])
                username = requestData['email']
                email = requestData['email']
                last_name = requestData['last_name']
                first_name = requestData['first_name']
                confirm_new_password = requestData['confirm_new_password']
                new_password = requestData['new_password']
                current_password = requestData['current_password']
                password = requestData['password']
                next_pay_date = requestData['next_pay_date']
                pay_recurrance_flag = requestData['pay_recurrance_flag']
                average_paycheck_amount = requestData['average_paycheck_amount']
                account_balance_amount = requestData['account_balance_amount']
            elif request.content_type is None or not request.content_type:
                return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
            else:
                return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202

        else:
            return {"meta":buildMeta(), "error":"Could not find user id #"+id, "data": None}

        #TODO: Prevent Username or Email Change without confirmation token!?!


        if first_name:
            user.first_name = first_name;
        if last_name:
            user.last_name = last_name;
        if pay_recurrance_flag:
            user.pay_recurrance_flag = pay_recurrance_flag;
        if next_pay_date:
            user.next_pay_date = next_pay_date;
        if average_paycheck_amount:
            user.average_paycheck_amount = average_paycheck_amount
        if account_balance_amount:
            user.account_balance_amount = account_balance_amount

        #Password Change Logic
        if current_password and new_password and confirm_new_password:
            app.logger.info('Current Password:'+user.password+', Proposed Password:'+generate_password_hash(new_password))
            if new_password == confirm_new_password and user.verify_password(current_password) and current_password != new_password:
                app.logger.info("Everything checks out, creating new password")
                user.password = generate_password_hash(new_password)
            elif current_password == new_password:
                app.logger.info("Your new password must be different than your own password")
                return {"meta":buildMeta(), "error":"Your new password must be different than your own password"}
            elif user.verify_password(current_password) == False:
                app.logger.info("Current password does not match our records. Please try again")
                return {"meta":buildMeta(), "error":"Current password does not match our records. Please try again"}
            elif new_password != confirm_new_password:
                return {"meta":buildMeta(), "error":"New passwords do not match"}
            else:
                return {"meta":buildMeta(), "error":"Failed to update Password"}
            #TODO: ADD LOGIC TO MEET PASSWORD COMPLEXITY REQUIREMENTS
        elif new_password and not confirm_new_password:
            return {"meta":buildMeta(), "error":"When changing passwords, both password and confirmation are required"}
        elif confirm_new_password and not new_password:
            return {"meta":buildMeta(), "error":"When changing passwords, both password and confirmation are required"}
        elif current_password and not confirm_new_password or new_password:
            return {"meta":buildMeta(), "error":"New Password not provided, ignoring"}
        elif current_password and not confirm_new_password or new_password:
            return {"meta":buildMeta(), "error":"All required information was not provided to change password"}



        user.last_updated = datetime.utcnow()
        db_session.commit()
        return {"meta":buildMeta(), "data": [user.serialize], "error":None}, 200




    ########################
    # REGISTER USER ACTION #
    ########################
    def post(self, user_id=None):
        app.logger.debug('Accessing Me.post (Registering New User)')

        id = ''
        username = None
        new_password = None
        confirm_new_password = None
        email = None
        first_name = None
        last_name = None
        account_balance_amount = None
        confirm_email = None

        average_paycheck_amount = None
        next_pay_date = None
        pay_recurrance_flag = None

        if request_is_json():
            #app.logger.debug(json.dumps(request.get_json()))
            data = request.get_json()
            if data:
                for key,value in data.iteritems():
                    #app.logger.debug(key+'-'+str(value))
                    if key == 'new_password':
                        new_password = value
                    elif key == 'confirm_new_password':
                        confirm_new_password = value
                    elif key == 'email':
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
                    elif key == 'confirm_email':
                        confirm_email = value
            else:
                return {"meta":buildMeta(), "error":"No Data Sent", "data": None}, 202
        elif request_is_form_urlencode():
            # TODO: Handle nulls
            app.logger.info('Updating user '+username)
            requestData = json.loads(request.form['data'])
            username = requestData['email']
            email = requestData['email']
            last_name = requestData['last_name']
            first_name = requestData['first_name']
            confirm_new_password = requestData['confirm_new_password']
            new_password = requestData['new_password']
            password = requestData['password']
            next_pay_date = requestData['next_pay_date']
            pay_recurrance_flag = requestData['pay_recurrance_flag']
            average_paycheck_amount = requestData['average_paycheck_amount']
            account_balance_amount = requestData['account_balance_amount']
            confirm_email = requestData['confirm_email']
        elif request.content_type is None or not request.content_type:
            return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202



        #TODO: PASSWORD and CONFIRM_PASSWORD comparison
        #TODO: CONFIRM EMAIL IS VALID EMAIL ADDRESS
        # REQUIRED FIELD CHECKS
        if email is None or confirm_email is None:
            app.logger.debug("Registration Failed, email was not provied")
            return {"meta":buildMeta(), "error":"Email and confirmation email is required", "data": None}
        if email is None or confirm_email is None:
            app.logger.debug("User '"+email+"' Registration failed, Confirm password was not provided")
            return {"meta":buildMeta(), "error":"Email and confirmation email is required", "data": None}
        if new_password is None:
            app.logger.debug("User '"+email+"' Registration failed, password was not provided")
            return {"meta":buildMeta(), "error":"Password is required", "data": None}
        if new_password != confirm_new_password:
            app.logger.debug("User '"+email+"' Registration failed, new_password does not match confirm_new_password")
            return {"meta":buildMeta(), "error":"Passwords do not match", "data": None}
        if first_name is None or last_name is None:
            app.logger.debug("User '"+email+"' Registration failed, First and Last name is required")
            return {"meta":buildMeta(), "error":"First and last name is required", "data": None}
        if  pay_recurrance_flag is None or next_pay_date is None:
            #TODO: Verify pay_recurrance_flag is in list
            app.logger.debug("User '"+email+"' Registration failed, Pay Recurrance and Next Pay Date is Required")
            return {"meta":buildMeta(), "error":"Pay Recurrance and Next Pay Date is Required", "data": None}

        if email != confirm_email:
            return {"meta":buildMeta(), "error":"Email and confirmation email do not match", "data": None}


        if User.query.filter_by(username = username).first() is not None:
            return {"meta":buildMeta(), "error":"Username already exists", "data": None}

        confirm_token = generate_confirmation_token(email)

        #app.logger.info(confirm_token);


        #print due_date
        if next_pay_date is not None:
            next_pay_date = datetime.strptime(next_pay_date, "%Y-%m-%d")


        newUser = User(username=email, password=new_password, email=email, first_name=first_name, last_name=last_name, next_pay_date = next_pay_date, pay_recurrance_flag = pay_recurrance_flag,  account_balance_amount=account_balance_amount,  confirm_token=confirm_token)

        db_session.add(newUser)
        db_session.commit()

        send_email_confirmation_email(first_name, last_name, email, confirm_token)

        login_user(newUser)
        session['username']=email

        return {"meta":buildMeta(), "error":None, "data":None}

    @login_required
    def delete(self, user_id = None):
        return {"meta":buildMeta(), "data": "Tisk, tisk. You cannot just simply 'DELETE' an account! there are protocols!", "error": None}, 200

api.add_resource(ApiMe, '/api/me', '/api/me/', '/api/me/<string:user_id>', '/api/me/', '/api/me/<string:user_id>')














############
# BILL API #
############

class ApiBill(Resource):
    @login_required
    def get(self, bill_id=None):
        billId = None
        paid_flag = None
        funded_flag = None
        newDict = {}

        if 'username' in session:
            user=User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403



        #TODO: BIND Bill with User ID based upon session
        if bill_id is not None:
            billId = bill_id
        elif request.args.get('bill_id') is not None:
            billId = request.args.get('bill_id')

        if request.args.get('paid_flag') is not None:
            if request.args.get('paid_flag').upper() == 'TRUE':
                app.logger.info('paid flag is TRUE')
                paid_flag = True
                newDict['paid_flag'] = True
            elif request.args.get('paid_flag').upper() == 'FALSE':
                app.logger.info('paid flag is FALSE')
                paid_flag = False
                newDict['paid_flag'] = False

        if request.args.get('funded_flag') is not None:
            if request.args.get('funded_flag').upper() == 'TRUE':
                app.logger.info('funded flag is TRUE')
                funded_flag = True
                newDict['funded_flag'] = True
            elif request.args.get('funded_flag').upper() == 'FALSE':
                app.logger.info('funded flag is FALSE')
                funded_flag = False
                newDict['funded_flag'] = False

        if billId is not None:
            app.logger.info("looking for bill:" + billId)
            bill = Bill.query.filter_by(id=billId, user_id=user.id).first()
            #app.logger.debug(bill)

            if bill is None:
                return {"meta":buildMeta(), "data":[], "error":None}
            else:
                return jsonify(meta=buildMeta(), data=[bill.serialize], error=None)
        else:

            app.logger.debug(request.args)
            return {"meta":buildMeta(), "data":[i.serialize for i in Bill.query.filter_by(**newDict).all()], "error":None}



    @login_required
    def put(self, bill_id=None):
        app.logger.debug('Accessing Bill.put')

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
        payment_type_ind = None
        payment_processing_flag = None
        user = None

        if 'username' in session:
            user=User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403

        if request_is_json():
            app.logger.info('Updating bill based upon JSON Request')
            app.logger.debug(json.dumps(request.get_json()))
            data = request.get_json()
            if data:
                for key,value in data.iteritems():
                    #app.logger.debug(key+'-'+str(value))
                    if key == 'name':
                        name = value
                    if key == 'bill_id':
                        bill_id = value
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
                        payment_type_ind = value
                    elif key == 'payment_processing_flag':
                        payment_processing_flag = value
        elif request_is_form_urlencode():
            app.logger.info('Updating bill #'+bill_id)
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
            payment_type_ind = requestData['payment_type_ind']
            payment_processing_flag = requestData['payment_processing_flag']
        elif request.content_type is None or not request.content_type:
            return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202


        if bill_id is None:
            if request.args.get('bill_id') is not None:
                bill_id = request.args.get('bill_id')
            else:
                return {"meta":buildMeta(), "error":"No Bill ID Provided"}

        bill = Bill.query.filter_by(id=bill_id, user_id=user.id).first()

        if bill is None:
            return {"meta":buildMeta(), "error":"Could not find bill", "data":None}


        if name:
            bill.name = name
        if description:
            bill.description = description
        if due_date:
            bill.due_date = due_date
        if billing_period:
            bill.billing_period = billing_period
        if total_due:
            bill.total_due = total_due
        #TODO: Prevent amount changes if bill is funded or paid

        if paid_flag is not None:
            bill.paid_flag = paid_flag
            if paid_flag and paid_date is None:
                bill.paid_date = datetime.utcnow()

        if paid_date:
            bill.paid_date = paid_date
            bill.paid_flag = True


        if check_number:
            bill.check_number = check_number
        if payment_type:
            bill.payment_type = payment_type
        if payment_type_ind:
            bill.payment_type_ind = payment_type_ind
        if payment_processing_flag is not None:
            bill.payment_processing_flag = payment_processing_flag

        if bill.name is None or bill.name =='' or not bill.name:
            return {"meta":buildMeta(), "error":"Name is required", "data":None}
        else:
            db_session.commit()
            return {"meta":buildMeta(), "data": bill.serialize, "error":None}, 201



    @login_required
    def post(self, bill_id=None):
        app.logger.debug('Accessing Bill.post')

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
        payment_type_ind = None
        payment_processing_flag = None



        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()

        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403

        if request_is_json():
            app.logger.info('Creating new user based upon JSON Request')
            app.logger.debug(json.dumps(request.get_json()))
            data = request.get_json()
            for key,value in data.iteritems():
                #app.logger.debug(key+'-'+str(value))
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
            payment_type_ind = requestData['payment_type_ind']
            payment_processing_flag = requestData['payment_processing_flag']
        elif request.content_type is None or not request.content_type:
            return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202


        #print due_date
        if due_date is not None:
            due_date = datetime.strptime(due_date, "%Y-%m-%d")

        if name is None or total_due is None:
            return {"meta":buildMeta(), "error":"Bills require a name and Total amount due", "data":None}

        #TODO: THIS SHOULD NOT BE A REQUIREMENT
        if Bill.query.filter_by(name = name, user_id = user_id).first() is not None:
            return {"meta":buildMeta(), "error":"Bill already exists", "data":None}



        newBill = Bill(user_id=user.id, name=name, description=description, due_date=due_date, billing_period=billing_period, total_due=total_due, paid_flag=paid_flag, paid_date=paid_date, payment_type_ind=payment_type_ind, check_number=check_number, payment_processing_flag=payment_processing_flag)

        db_session.add(newBill)
        db_session.commit()

        return {"meta":buildMeta(), 'data':newBill.serialize, "error":None}, 201

    @login_required
    def delete(self, bill_id = None):


        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403


        #TODO: LOOK FOR CONTENT_TYPE
        if bill_id is None:
            return {"meta":buildMeta(), "error":"Could not find bill"}, 202


        app.logger.info("Deleting Bill #: " + bill_id)
        bill = Bill.query.filter_by(id=bill_id, user_id=user.id).first()
        if bill is not None:
            db_session.delete(bill)
            db_session.commit()
            return {"meta":buildMeta(), "data" : None}
        else:
            return {"meta":buildMeta(), "error":"Bill #"+bill_id+" Could not be found", "data" : None}

api.add_resource(ApiBill, '/api/bill', '/api/bill/', '/api/bill/<string:bill_id>')
















####################
# PAYMENT PLAN API #
####################

class ApiPaymentPlan(Resource):
    @login_required
    def get(self, payment_plan_id=None):
        paymentPlanId = None
        accepted_flag = None
        bill_id = None

        if 'username' in session:
            user=User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found", "data":None}, 401

        #TODO: BIND payment_plan with User ID based upon session
        if payment_plan_id is not None:
            paymentPlanId = payment_plan_id
        elif request.args.get('payment_plan_id') is not None:
            paymentPlanId = request.args.get('payment_plan_id')

        if request.args.get('accepted_flag') is not None:
            if request.args.get('accepted_flag').upper() == 'TRUE':
                app.logger.info('accepted_flag is true')
                accepted_flag = True
            elif request.args.get('accepted_flag').upper() == 'FALSE':
                app.logger.info('accepted_flag is false')
                accepted_flag = False

        if request.args.get('bill_id') is not None:
            bill_id = request.args.get('bill_id')

        #TODO: Add some logic for "Base_flag" filtering
        if paymentPlanId is not None:
            app.logger.info("looking for payment plan:" + paymentPlanId)
            payment_plan = Payment_Plan.query.filter_by(id=paymentPlanId, user_id=user.id).first()
            app.logger.info(payment_plan)

            if payment_plan is None:
                return {"meta":buildMeta(), 'data':[], "error":None}, 200
            else:
                return jsonify(meta=buildMeta(), data=[payment_plan.serialize])
        else:
            if accepted_flag is not None:
                #There should only be 1 record with accepted_flag of false...if there are no records, create one
                if accepted_flag is False:
                    payment_plan = Payment_Plan.query.filter_by(user_id=user.id, accepted_flag=accepted_flag).first()
                    if payment_plan is None:
                        #User does not have a working payment plan...creating new one
                        app.logger.info('User does not have a working payment plan...creating new one')
                        newPaymentPlan = Payment_Plan(user_id=user.id, accepted_flag=False, base_flag=False, amount=0)
                        db_session.add(newPaymentPlan)
                        db_session.commit()
                        payment_plan = newPaymentPlan.serialize
                        return {"meta":buildMeta(), "data":payment_plan, "error":None}, 200
                    else:
                        return {"meta":buildMeta(), "data":payment_plan.serialize, "error":None}, 200
                #Get existing payment plans
                else:
                    if bill_id is not None:
                        items = Payment_Plan_Item.query.filter_by(bill_id=bill_id)
                        idList = list();
                        for item in items:
                            idList.append(item.payment_plan_id)

                        payment_plans = [i.serialize for i in Payment_Plan.query.filter(Payment_Plan.id.in_(idList)).all()]

                    else:
                        payment_plans = [i.serialize for i in Payment_Plan.query.filter_by(user_id=user.id, accepted_flag=accepted_flag)]
            else:
                payment_plans = [i.serialize for i in Payment_Plan.query.filter_by(user_id=user.id)]

            return {"meta":buildMeta(), "data":payment_plans, "error":None}, 200

    @login_required
    def post(self, payment_plan_id=None):
        #TODO: MAKE A POST
        return {"meta":buildMeta(), "data":None, "error":None}, 202

    @login_required
    def put(self, payment_plan_id=None):
        app.logger.debug('Accessing PaymentPlan.put')

        #TODO: Handle update
        user_id = None
        user = None
        amount = None
        base_flag = None
        transfer_date = None
        date_created = None
        last_updated = None
        accepted_flag = None
        payment_plan_items = None


        if 'username' in session:
            user=User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403

        if request_is_json():
            app.logger.info('Updating Payment Plan based upon JSON Request')
            app.logger.debug(json.dumps(request.get_json()))
            data = request.get_json()
            if data is not None:
                for key,value in data.iteritems():
                    #app.logger.debug(key+'-'+str(value))
                    if key == 'transfer_date':
                        transfer_date = value
                    elif key == 'payment_plan_id':
                        payment_plan_id = value
                    elif key == 'accepted_flag':
                        accepted_flag = value
                    elif key == 'payment_plan_items':
                        payment_plan_items = value
                    elif key == 'amount':
                        amount = value
            else:
                return {"meta":buildMeta(), "error":"No JSON Data Sent"}
        elif request_is_form_urlencode():
            app.logger.info('Updating Payment Plan based upon form Request')
            requestData = json.loads(request.form['data'])
            if requestData is not None:
                payment_plan_id = requestData['payment_plan_id']
                transfer_date = requestData['transfer_date']
                accepted_flag = requestData['accepted_flag']
                payment_plan_items = requestData['payment_plan_items']
                amount = requestData['amount']
            else:
                return {"meta":buildMeta(), "error":"No form Data Sent"}
        elif request.content_type is None or not request.content_type:
            return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202

        if payment_plan_id is None:
            if request.args.get('payment_plan_id') is not None:
                payment_plan_id = request.args.get('payment_plan_id')
            else:
                return {"meta":buildMeta(), "error":"No Payment Plan ID Provided"}, 202

        payment_plan = Payment_Plan.query.filter_by(id=payment_plan_id, user_id=user.id).first()

        if payment_plan is None:
            return {"meta":buildMeta(), 'error':'Could not find Payment Plan', 'data':[]}, 200

        if amount is not None:
            payment_plan.amount = amount

        if payment_plan_items is not None:
            #app.logger.debug("Payment_Plan_Items")
            new_payment_plan_items = list()
            for payment_plan_item in payment_plan_items:
                new_payment_plan_items.append(Payment_Plan_Item(payment_plan_id=payment_plan_id, user_id=payment_plan_item['user_id'], bill_id=payment_plan_item['bill_id'], amount=payment_plan_item['amount']))

            Payment_Plan_Item.query.filter_by(payment_plan_id=payment_plan_id).delete()
            db_session.commit()

            payment_plan.payment_plan_items = new_payment_plan_items
            db_session.commit()



        if accepted_flag is not None:
            if str(accepted_flag).upper() == 'TRUE':
                accepted_flag = True
            elif str(accepted_flag).upper() == 'FALSE':
                accepted_flag = False


            if accepted_flag is True:
                payment_plan.accepted_flag = True
                #TODO: NEED TO CHECK TO SEE IF WE HAVE OVER PAID A BILL?

                #TODO: NEED TO UPDATE PAYMENT PLAN ITEMS ACCEPTED FLAG
                payment_plan_items = Payment_Plan_Item.query.filter_by(user_id=user.id, payment_plan_id=payment_plan_id)
                payment_plan_items_list = payment_plan_items.all()
                for payment_plan_item in payment_plan_items_list:
                    payment_plan_item.accepted_flag = True

                payment_plan.payment_plan_items = payment_plan_items_list
                db_session.commit()


                #CHECKING TO SEE IF BILL IS FULLY FUNDED
                #1. Loop through submitted payment plan items
                #2. Query each bill in the payment plan
                #3. sum all funded payment plan items for the bill
                #4. If the amounts match....set bill a "funded"
                for payment_plan_item in payment_plan.payment_plan_items:
                    paid_amount = 0
                    bill = Bill.query.filter_by(id = payment_plan_item.bill_id, user_id = user.id).first()
                    total_paid = db_session.query(func.sum(Payment_Plan_Item.amount).label('sum_amount')).filter(Payment_Plan_Item.bill_id == payment_plan_item.bill_id).filter(Payment_Plan_Item.accepted_flag == True).first()
                    if total_paid is not None:
                        if total_paid.sum_amount is not None:
                            paid_amount = float(total_paid.sum_amount)
                    app.logger.info("Bill Amount = $" + str(bill.total_due))
                    app.logger.info("total_paid = $" + str(round(paid_amount,2)))
                    if round(paid_amount,2) == float(bill.total_due):
                        app.logger.info("Bill '" +bill.name+ "' is fully paid!")
                        bill.funded_flag = True
                        db_session.commit()
                    else:
                        app.logger.info("Bill '" +bill.name+ "' is not fully paid")


            elif accepted_flag is False:
                payment_plan.accepted_flag = False

        payment_plan.last_updated = datetime.utcnow()
        app.logger.info('Saving Payment Plan')
        db_session.commit()
        return {"meta":buildMeta(), "data":payment_plan.serialize}


    @login_required
    def delete(self, payment_plan_id = None):

        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403

        #TODO: LOOK FOR CONTENT_TYPE
        if payment_plan_id is None:
            return {"meta":buildMeta(), "error":"Could not find payment plan"}, 202

        app.logger.info("Deleting Payment Plan #: " + payment_plan_id)
        bill = Payment_Plan.query.filter_by(id=payment_plan_id, user_id=user.id).first()
        if bill is not None:
            db_session.delete(bill)
            db_session.commit()
            return {"meta":buildMeta(), "data" : None}
        else:
            return {"meta":buildMeta(), "error":"Payment Plan #"+payment_plan_id+" Could not be found", "data" : None}

api.add_resource(ApiPaymentPlan, '/api/payment_plan', '/api/payment_plan/', '/api/payment_plan/<string:payment_plan_id>')
















#########################
# PAYMENT PLAN ITEM API #
#########################

class ApiPaymentPlanItem(Resource):
    @login_required
    def get(self, payment_plan_item_id=None):
        payment_plan_item_id = None
        payment_plan_id = None

        if 'username' in session:
            user=User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403

        if payment_plan_item_id is not None:
            paymentPlanId = payment_plan_item_id
        elif request.args.get('payment_plan_item_id') is not None:
            paymentPlanId = request.args.get('payment_plan_item_id')

        if request.args.get('payment_plan_id') is not None:
            payment_plan_id = request.args.get('payment_plan_id')

        if payment_plan_item_id is not None:
            app.logger.info("looking for Payment Plan Item:" + payment_plan_item_id)
            payment_plan_items = Payment_Plan_Item.query.filter_by(id=payment_plan_item_id, user_id=user.id).first()

            if payment_plan_items is None:
                return {"meta":buildMeta(), 'data':[]}
            else:
                return jsonify(meta=buildMeta(), data=[payment_plan_items.serialize])
        else:
            if payment_plan_id is not None:
                payment_plan_items = [i.serialize for i in Payment_Plan_Item.query.filter_by(user_id=user.id, payment_plan_id=payment_plan_id)]
            else:
                payment_plan_items = [i.serialize for i in Payment_Plan_Item.query.filter_by(user_id=user.id)]

            return {"meta":buildMeta(), "data":payment_plan_items, "error":None}, 200

    @login_required
    def post(self, payment_plan_item_id=None):
        app.logger.debug('Accessing PaymentPlanItem.post')
        #TODO: Build POST
        return {"meta":buildMeta(), "data":None, "error":None}, 202

    @login_required
    def put(self, payment_plan_item_id=None):
        app.logger.debug('Accessing PaymentPlanItem.put')

        #TODO: Handle update
        user_id = None
        user = None
        amount = None

        if 'username' in session:
            user=User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403

        if request_is_json():
            app.logger.info('Updating Payment Plan Item based upon JSON Request')
            app.logger.debug(json.dumps(request.get_json()))
            data = request.get_json()
            if data is not None:
                for key,value in data.iteritems():
                    #app.logger.debug(key+'-'+str(value))
                    if key == 'amount':
                        amount = value
                    elif key == 'payment_plan_item_id':
                        payment_plan_item_id = value
            else:
                return {"meta":buildMeta(), "error":"No JSON Data Sent"}
        elif request_is_form_urlencode():
            app.logger.info('Updating Payment Plan Item based upon form Request')
            requestData = json.loads(request.form['data'])
            if requestData is not None:
                payment_plan_item_id = requestData['payment_plan_item_id']
                amount = requestData['amount']
            else:
                return {"meta":buildMeta(), "error":"No form Data Sent"}
        elif request.content_type is None or not request.content_type:
            return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202

        if payment_plan_item_id is None:
            if request.args.get('payment_plan_item_id') is not None:
                payment_plan_item_id = request.args.get('payment_plan_item_id')
            else:
                return {"meta":buildMeta(), "error":"No Payment Plan ID Provided"}

        payment_plan_item = Payment_Plan_Item.query.filter_by(id=payment_plan_item_id, user_id=user.id).first()
        app.logger.info(payment_plan_item)

        if payment_plan_item is None:
            return {"meta":buildMeta(), 'error':'Could not find Payment Plan Item', 'data':[]}

        if amount is not None:
            payment_plan_item.amount = amount

        app.logger.info('Saving Payment Plan Item')
        db_session.commit()
        return {"meta":buildMeta(), "data":payment_plan_item.serialize}

    @login_required
    def delete(self, payment_plan_item_id=None):
        app.logger.debug('Accessing PaymentPlanItem.delete')
        bill_id = request.args.get('bill_id')

        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found", "data":None}, 401

        if payment_plan_item_id is None:
            if bill_id is not None:
                bill = Bill.query.filter_by(id=bill_id, user_id=user.id).first()
                if bill is not None:
                    app.logger.info("Deleting all Payment_plan_items from bill #" + str(bill_id))
                    bill.funded_flag = False;
                    bill.payment_processing_flag = False;
                    Payment_Plan_Item.query.filter_by(bill_id=bill_id).delete()
                    db_session.commit()
                    return {"meta":buildMeta(), "data" : None,  "error":None}, 200
                else:
                    return {"meta":buildMeta(), "error":"Bill #" + str(bill_id) + " Could not be found", "data" : None}, 202
            else:
                return {"meta":buildMeta(), "error":"Could not find payment plan item", "data": None}, 202
        else:
            payment_plan_item = Payment_Plan_Item.query.filter_by(id=payment_plan_item_id, user_id=user.id).first()
            if payment_plan_item is not None:
                app.logger.info("Deleting Payment_plan_item #" + str(payment_plan_item_id))
                db_session.delete(payment_plan_item)
                db_session.commit()
                return {"meta":buildMeta(), "data" : None, "error":None}, 200
            else:
                return {"meta":buildMeta(), "error":"Payment Plan Item #" + str(payment_plan_item_id) + " Could not be found", "data" : None}


api.add_resource(ApiPaymentPlanItem, '/api/payment_plan_item', '/api/payment_plan_item/', '/api/payment_plan_item/<string:payment_plan_item_id>')

















################
# FEEDBACK API #
################

class ApiFeedback(Resource):
    @login_required
    def get(self, feedback_id=None):
        feedbackId = None;

        if feedback_id is not None:
            feedbackId = feedback_id
        elif request.args.get('feedback_id') is not None:
            feedbackId = request.args.get('feedback_id')

        if feedbackId is not None:
            app.logger.info("looking for feedback:" + feedbackId)
            feedback = Feedback.query.filter_by(id=feedbackId).first()
            app.logger.debug(feedback)

            if feedback is None:
                return {"meta":buildMeta(), 'data':[], "error":None}, 200
            else:
                return {"meta":buildMeta(), 'data':[feedback.serialize], "error":None}, 200
        else:
            return {"meta":buildMeta(), "data":[i.serialize for i in Bill.query.all()], "error":None}, 202

    @login_required
    def post(self, feedback_id=None):
        app.logger.debug('Accessing Feedback.post')

        user = None
        user_id = None
        rating = None
        feedback = None


        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()

        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403
        else:
            user_id = user.id;

        if request_is_json():
            app.logger.info('Creating new feedback based upon JSON Request')
            app.logger.debug(json.dumps(request.get_json()))
            data = request.get_json()
            if data is not None:
                for key,value in data.iteritems():
                    #app.logger.debug(key+'-'+str(value))
                    if key == 'rating':
                        rating = value
                    if key == 'feedback':
                        feedback = value
        elif request_is_form_urlencode():
            app.logger.info('Creating new user based upon other Request')
            requestData = json.loads(request.form['data'])
            rating = requestData['rating']
            feedback = requestData['feedback']
        elif request.content_type is None or not request.content_type:
            return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202

        if rating is not None and feedback is not None:
            newFeedback = Feedback(user_id=user_id, rating=int(rating), feedback=feedback)

            db_session.add(newFeedback)
            db_session.commit()

            html_message = "<p>Rating: " + str(rating) + "</p><p>Feedback: "+ feedback + "</p>"
            text_message = "Rating: " + str(rating) + "\r\nFeedback: "+ feedback

            send_email('New Feedback', ['"Robert Donovan" <admin@mixfin.com>', '"David Larrimore" <david.larrimore@mixfin.com'], None, html_message)

            return {"meta":buildMeta(), 'data':newFeedback.serialize}, 201
        else:
            return {"meta":buildMeta(), 'error':'No feedback was provided'}, 201

    @login_required
    def put(self, payment_plan_item_id=None):
        app.logger.debug('Accessing Feedback.put')
        #TODO: Build PUT
        return {"meta":buildMeta(), "data":None, "error":None}, 202

    @login_required
    def delete(self, payment_plan_item_id=None):
        app.logger.debug('Accessing Feedback.delete')
        #TODO: Build PUT
        return {"meta":buildMeta(), "data":None, "error":None}, 202



api.add_resource(ApiFeedback, '/api/feedback', '/api/feedback/', '/api/feedback/<string:feedback_id>')









##########################
# EMAIL CONFIRMATION API #
##########################

class ApiConfirmEmail(Resource):

    @login_required
    def get(self):
        return {"meta":buildMeta(), "error":None, "data":None}, 202

    #The PUT method is used to actually confirm the login email
    @login_required
    def put(self, email_token=None):
        app.logger.debug('Accessing ConfirmEmail.put')

        user = None
        user_id = None

        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()

        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found", "data":None}, 401
        else:
            user_id = user.id;

        if request_is_json():
            app.logger.info('Creating new feedback based upon JSON Request')
            app.logger.debug(json.dumps(request.get_json()))
            data = request.get_json()
            if data is not None:

                for key,value in data.iteritems():
                    #app.logger.debug(key+'-'+str(value))
                    if key == 'email_token':
                        email_token = value
        elif request_is_form_urlencode():
            app.logger.info('Creating new user based upon other Request')
            requestData = json.loads(request.form['data'])
            email_token = requestData['email_token']
        elif request.content_type is None or not request.content_type:
            return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202

        if email_token is not None and email_token == user.confirm_token:
            app.logger.info('correct token provided, activating account')
            user.active = True
            user.confirm_token = None
            user.confirmed_at = datetime.utcnow()
            db_session.commit()

            return {"meta":buildMeta(), 'data':None, 'error':None}, 201
        else:
            return {"meta":buildMeta(), 'error':'Incorrect token was provided'}, 201

    #The POST method is used to send new confirmation emails
    #it creates a new token and sends it to the user
    @login_required
    def post(self, user_id=None):
        app.logger.debug('Accessing ConfirmEmail.post')

        user = None
        user_id = None

        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()

        if user is None:
            return {"meta":buildMeta(), "error":"No Session Found"}, 403
        else:
            user_id = user.id;

        if user.confirmed_at is None:
            confirm_token = generate_confirmation_token(user.email+str(datetime.utcnow()))
            app.logger.debug('created new confirmation token '+confirm_token+' for '+user.email);
            user.confirm_token = confirm_token;
            db_session.commit()

            send_email_confirmation_email(user.first_name, user.last_name, user.email, confirm_token)
            return {"meta":buildMeta(), 'data':[user.serialize], 'error':None}, 201
        else:
            return {"meta":buildMeta(), "error":"User has already confirmed email"}, 200

    @login_required
    def delete(self, user_id = None):
        return {"meta":buildMeta(), "data": "Tisk, tisk. You cannot just simply 'DELETE' a confirmaion email! there are protocols!", "error": None}, 200


api.add_resource(ApiConfirmEmail, '/api/confirm_email', '/api/confirm_email/', '/api/confirm_email/<string:token>')








#########################
# PASSWORD RECOVERY API #
#########################
#THIS API IS TO HANDLE WHEN USERS DON'T HAVE THEIR CURRENT PASSWORD

class ApiPasswordRecovery(Resource):

    def get(self):
        return {"meta":buildMeta(), "error":None, "data":None}, 200

    #The PUT method is used to actually change the password
    def put(self, email_address=None):
        app.logger.debug('Accessing ApiPasswordRecovery.put')

        password_recovery_token = None
        new_password = None
        confirm_new_password = None


        if request_is_json():
            app.logger.debug(json.dumps(request.get_json()))
            data = request.get_json()
            if data is not None:
                for key,value in data.iteritems():
                    #app.logger.debug(key+'-'+str(value))
                    if key == 'password_token':
                        password_recovery_token = value
                    elif key == 'confirm_new_password':
                        confirm_new_password = value
                    elif key == 'new_password':
                        new_password = value
                    elif key == 'email_address':
                        data_email_address = value
        elif request_is_form_urlencode():
            app.logger.info('Creating new user based upon other Request')
            requestData = json.loads(request.form['data'])
            password_recovery_token = requestData['password_token']
            new_password = requestData['new_password']
            confirm_new_password = requestData['confirm_new_password']
            data_email_address = requestData['email_address']
        elif request.content_type is None or not request.content_type:
            return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202



        if email_address is not None:
            user = User.query.filter_by(email=email_address).first()
        elif data_email_address is not None:
            user = User.query.filter_by(email=data_email_address).first()
        else:
            return {"meta":buildMeta(), "error":"Please provide an email address"}


        if user is None:
            return {"meta":buildMeta(), "error":"No account found with that email address"}


        #TODO: ADD LOGIC TO CHECK password_recovery_date
        if user.password_recovery_date is None:
            return {"meta":buildMeta(), "error":"Failed to update Password. Process not started."}, 201
        elif user.password_recovery_date < datetime.utcnow():
            return {"meta":buildMeta(), "error":"Failed to update Password. Recovery process has expired."}, 201


        if password_recovery_token is not None and password_recovery_token == user.confirm_token:
            if new_password and confirm_new_password:
                if new_password == confirm_new_password:
                    app.logger.info("Everything checks out, setting new password")
                    user.password = generate_password_hash(new_password)
                    user.confirm_token = None
                    user.password_recovery_date = None
                    db_session.commit()
                    return {"meta":buildMeta(), 'data':None}, 201
                    #TODO: SEND A CONFIRMATION EMAIL
                elif new_password != confirm_new_password:
                    return {"meta":buildMeta(), "error":"New passwords do not match"}, 201
                else:
                    return {"meta":buildMeta(), "error":"Failed to update Password"}
                #TODO: ADD LOGIC TO MEET PASSWORD COMPLEXITY REQUIREMENTS
            elif not new_password or not confirm_new_password:
                return {"meta":buildMeta(), "error":"When changing passwords, both password and confirmation are required."}, 201
            else:
                return {"meta":buildMeta(), "error":"Failed to update Password."}, 201
        else:
            return {"meta":buildMeta(), "error":"Failed to update Password. Invalid token."}, 201


    #The POST method is used to send the password recovery email
    #it creates a new token and sends it to the user
    def post(self, email_address=None):
        app.logger.debug('Accessing ApiPasswordRecovery.post')

        email_address = None

        if request_is_json():
            app.logger.debug(json.dumps(request.get_json()))
            data = request.get_json()
            if data is not None:
                for key,value in data.iteritems():
                    #app.logger.debug(key+'-'+str(value))
                    if key == 'email_address':
                        data_email_address = value
        elif request_is_form_urlencode():
            app.logger.info('Creating new user based upon other Request')
            requestData = json.loads(request.form['data'])
            data_email_address = requestData['email_address']
        elif request.content_type is None or not request.content_type:
            return {"meta":buildMeta(), "error":"Unable to process, no content type was provided", "data":None}, 202
        else:
            return {"meta":buildMeta(), "error":"Unable to process "+ str(request.content_type), "data":None}, 202



        if email_address is not None:
            user = User.query.filter_by(email=email_address).first()
        elif data_email_address is not None:
            user = User.query.filter_by(email=data_email_address).first()
        else:
            return {"meta":buildMeta(), "error":"Please provide an email address"}


        if user is None:
            return {"meta":buildMeta(), "error":"No account found with that email address"}

        confirm_token = generate_confirmation_token(user.email+str(datetime.utcnow()))
        app.logger.debug('created new confirmation token '+confirm_token+' for '+user.email);
        #app.logger.info(confirm_token);

        #SETTING EXPIRATION DATE
        user.password_recovery_date = datetime.utcnow() + timedelta(days=1)
        user.confirm_token = confirm_token;
        db_session.commit()

        send_password_recovery_email(user)
        return {"meta":buildMeta(), 'data':None}, 201

    @login_required
    def delete(self, user_id = None):
        return {"meta":buildMeta(), "data": "Tisk, tisk. You cannot just simply 'DELETE' a password confirmation! there are protocols!", "error": None}, 200


api.add_resource(ApiPasswordRecovery, '/api/recover_password', '/api/recover_password/', '/api/recover_password/<string:email_address>')















####################
# HELPER FUNCTIONS #
####################

def request_is_json():
    if 'application/json' in request.content_type:
        return True;
    else:
        return False







def request_is_form_urlencode():
    if 'application/x-www-form-urlencoded' in request.content_type:
        return True;
    else:
        return False




def buildMeta():
    return [{"authors":["David Larrimore", "Robert Donovan"], "copyright": "Copyright 2015 MixFin LLC.", "version": "0.1"}]







def send_email_confirmation_email(first_name, last_name, email, confirm_token):

    app.logger.info("Sending Welcome Email")
    html_message = '''
    <p>Hello '''+first_name+''',</p>
    <p>Thank you for registering with 2Weeks. In order to fully activate your account, you need to click the link below:</p>
    <p><a href="http://localhost:5000/#/?auth_check=true&action=confirm_email&token='''+confirm_token+'''" target="_blank">http://localhost:5000/home/#/?action=confirm_email&token='''+confirm_token+'''</a></p>
    <p>Thanks!</p>
    <p>the 2Weeks Admin Team<p>
    '''

    send_email('2Weeks Email Confirmation', ['"'+first_name+' '+last_name+'" <'+email+'>','"David Larrimore" <davidlarrimore@gmail.com>'], html_message, html_message)







def send_password_recovery_email(user):

    app.logger.info("Sending Password Recovery Email")
    html_message = '''
    <p>Hello '''+user.first_name+''',</p>
    <p>We have received a request to recover the password for your account. In order to complete this action, you need to click the link below:</p>
    <p><a href="http://localhost:5000/#/?email_address='''+user.email+'''&action=recover_password&token='''+user.confirm_token+'''" target="_blank">http://localhost:5000/#/?email_address='''+user.email+'''&action=recover_password&token='''+user.confirm_token+'''</a></p>
    <p>Thanks!</p>
    <p>the 2Weeks Admin Team<p>
    '''

    send_email('2Weeks Password Recovery', ['"'+user.first_name+' '+user.last_name+'" <'+user.email+'>','"David Larrimore" <davidlarrimore@gmail.com>'], html_message, html_message)
















########
# main #
########
if __name__ == "__main__":
    app.run(host='0.0.0.0')
