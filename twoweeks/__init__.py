__author__ = 'davidlarrimore'

import json
from datetime import datetime

from flask import Flask, render_template, request, jsonify, abort, g , flash, url_for, redirect
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
from twoweeks.models import User, Bill, Role

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
        app.logger.info('User:' + request.form['username'] + ' attempting to login')
        # validate username and password
        if (request.form['username'] is not None and request.form['password'] is not None):
            user = User.query.filter_by(username = request.form['username']).first()

            if (user is not None and user.verify_password(request.form['password'])):
                app.logger.info('Login Successful')
                login_user(user)
                return {"meta":buildMeta()}
            else:
                app.logger.info('Username or password incorrect')
                return {"meta":buildMeta(), "error":"Username or password incorrect"}
        else:
            app.logger.info('Please provide a username and password')
            return {"meta":buildMeta(), "error":"Please provide a username and password"}


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
# base Routes #
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





##############
# API Routes #
##############

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
                return {"meta":buildMeta(),"error": "No results returned for user id #"+ userID, "data":""}
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
            if request_wants_json():
                app.logger.info('Creating new user based upon JSON Request')
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
            else:
                app.logger.info('Updating user '+username)
                requestData = json.loads(request.form['data'])
                user.username = requestData['email']
                user.email = requestData['email']
                user.last_name = requestData['last_name']
                user.first_name = requestData['first_name']
                confirm_password = requestData['confirm_password']
                password = requestData['password']
        else:
            return {"meta":buildMeta(), "error":"Could not find user id #"+id}

        #TODO: PASSWORD and CONFIRM_PASSWORD comparison

        db_session.commit()
        return {"meta":buildMeta(), "data": "Updated Record with ID " + user_id}


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

        if request_wants_json():
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
        else:
            app.logger.info('Creating new user based upon other Request')
            requestData = json.loads(request.form['data'])
            username = requestData['email']
            email = requestData['email']
            last_name = requestData['last_name']
            first_name = requestData['first_name']
            confirm_password = requestData['confirm_password']

        #TODO: PASSWORD and CONFIRM_PASSWORD comparison
        if email is None or password is None:
            return {"meta":buildMeta(), "error":"Email and Password is required"}

        if User.query.filter_by(username = username).first() is not None:
            return {"meta":buildMeta(), "error":"Username already exists"}

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

        return {"meta":buildMeta(), "data" : "Deleted Record with ID " + user_id}

api.add_resource(ApiUser, '/api/user', '/api/user/', '/api/user/<string:user_id>', '/api/users/', '/api/users/<string:user_id>')





####################
# HELPER FUNCTIONS #
####################

def request_wants_json():
    if 'application/json' in request.accept_mimetypes:
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
