__author__ = 'davidlarrimore'

import json
from datetime import datetime

from flask import Flask, render_template, request, jsonify, abort, g
import twoweeks.config as config





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

from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True




###############
# base Routes #
###############

@app.route('/')
def index():
    #send_email('Test', ['david.larrimore@mixfin.com'], 'Test Flask Email', 'Test Flask Email')
    return render_template('index.html')

@app.route('/home/')
@auth.login_required
def home():
    return render_template('home.html')

@app.route('/admin/')
def adminIndex():
    return render_template('adminIndex.html')

@app.route('/admin/home/')
def adminHome():
    return render_template('adminHome.html')








##############
# API Routes #
##############

#USERS
class ApiUser(Resource):
    @auth.login_required
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

    @auth.login_required
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

    @auth.login_required
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

    @auth.login_required
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
