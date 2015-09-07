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
    user = User.query.filter_by(username = request.form['username']).first()
    app.logger.info(user.id);
    if (user is not None and user.verify_password(request.form['password'])):
        app.logger.info('Login Successful')
        login_user(user)
    else:
        app.logger.info('Username or password incorrect')
        flash('Username or password incorrect')

    return redirect(url_for('home'))



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('/'))


@app.route('/adminLogout')
def adminLogout():
    logout_user()
    return redirect(url_for('/admin/'))




#USERS
class ApiLogin(Resource):
    def post(self):
        app.logger.info('User:' + request.form['username'] + ' attempting to login')
        # validate username and password
        user = User.query.filter_by(username = request.form['username']).first()
        app.logger.info(user.id);

        if (user is not None and user.verify_password(request.form['password'])):
            app.logger.info('Login Successful')
            login_user(user)
            return {"meta":buildMeta(), "error":"none", "data": ""}
        else:
            app.logger.info('Username or password incorrect')
            return {"meta":buildMeta(), "error":"Username or password incorrect", "data": ""}

        return {"meta":buildMeta(), "error":"none", "data": ""}
api.add_resource(ApiLogin, '/api/login/')


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
        if user_id is not None:
            app.logger.info("looking for user:" + user_id)
            user = User.query.filter_by(id=user_id).first()
            if user is None:
                return {"meta":buildMeta(), "status":"success", "error": "No results returned for user id #"+ user_id, "data":""}
            else:
                return jsonify(meta=buildMeta(), data=[user.serialize])
        else:
            users = [i.serialize for i in User.query.all()]
            return {"meta":buildMeta(), "data":users}

    @login_required
    def put(self, user_id):
        print json.loads(request.form['data'])
        app.logger.info("Updating User for: " + request.form['data'])
        requestData = json.loads(request.form['data'])

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return {"meta":buildMeta(), "status":"success", "error": "No results returned for user id #"+ user_id, "data":""}
        else:
            user.username = requestData['username']
            user.email = requestData['email']
            user.first_name = requestData['first_name']
            user.last_name = requestData['last_name']
            user.last_updated = datetime.utcnow()
            db_session.commit()
            return {"meta":buildMeta(), "data": "Updated Record with ID " + user_id}

    @login_required
    def post(self, user_id=None):
        print json.loads(request.form['data'])
        app.logger.info("Creating User for: " + request.form['data'])

        requestData = json.loads(request.form['data'])

        if requestData['username'] is None or requestData['password'] is None:
            abort(400) # missing arguments

        if User.query.filter_by(username = requestData['username']).first() is not None:
            abort(400) # existing user

        newUser = User(username=requestData['username'], password=requestData['password'], email=requestData['email'], first_name=requestData['first_name'], last_name=requestData['last_name'])

        db_session.add(newUser)
        db_session.commit()

        return {"meta":buildMeta(), "error":"none", "data": newUser.id}

    @login_required
    def delete(self, user_id):
        app.logger.info("Deleting User #: " + user_id)
        user = User.query.filter_by(id=user_id).first()
        db_session.delete(user)
        db_session.commit()

        return {"meta":buildMeta(), "data" : "Deleted Record with ID " + user_id}

api.add_resource(ApiUser, '/api/user/', '/api/user/<string:user_id>', '/api/users/', '/api/users/<string:user_id>')









def buildMeta():
    return [{"authors":["David Larrimore", "Robert Donovan"], "copyright": "Copyright 2015 MixFin LLC.", "version": "0.1"}]






########
# main #
########
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
