__author__ = 'davidlarrimore'

import json
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
import twoweeks.config as config




#################
# configuration #
#################

app = Flask(__name__)
app.config['TRAP_BAD_REQUEST_ERRORS'] = config.TRAP_BAD_REQUEST_ERRORS
app.debug = config.DEBUG

# Importing Models
from twoweeks.database import init_db
init_db()

from twoweeks.database import db_session
from twoweeks.models import User, Bill


api = Api(app)


#logging.basicConfig(filename='twoweeks.log',level=logging.DEBUG)



#login_manager = LoginManager()


###############
# base Routes #
###############

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home/')
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

    def post(self, user_id=None):
        print json.loads(request.form['data'])
        app.logger.info("Creating User for: " + request.form['data'])
        requestData = json.loads(request.form['data'])
        newUser = User(requestData['username'], requestData['email'], requestData['first_name'], requestData['last_name'])
        db_session.add(newUser)
        db_session.commit()
        return {"meta":buildMeta(), "error":"none", "data": newUser.id}

    def delete(self, user_id):
        app.logger.info("Deleting User #: " + user_id)
        user = User.query.filter_by(id=user_id).first()
        db_session.delete(user)
        db_session.commit()

        return {"meta":buildMeta(), "data" : "Deleted Record with ID " + user_id}

api.add_resource(ApiUser, '/api/user/', '/api/user/<string:user_id>', '/api/users/', '/api/users/<string:user_id>')




#BILLS
class ApiBill(Resource):
    def get(self, bill_id=None):

        if bill_id is not None:
            app.logger.info("looking for user:" + bill_id)
            bill = Bill.query.filter_by(id=bill_id).first()
            if bill is None:
                return {"meta":buildMeta(), "status":"success", "error": "No results returned for user id #"+ bill_id, "data":""}
            else:
                return jsonify(meta=buildMeta(), data=[bill.serialize])
        else:
            bills = [i.serialize for i in Bill.query.all()]
            data = {"meta":buildMeta(), "data":[bills]}
            json.dumps(data)
            return data

    def put(self, bill_id):
        print json.loads(request.form['data'])
        app.logger.info("Updating User for: " + request.form['data'])
        requestData = json.loads(request.form['data'])

        bill = Bill.query.filter_by(id=bill_id).first()
        if bill is None:
            return {"meta":buildMeta(), "status":"success", "error": "No results returned for user id #"+ bill_id, "data":""}
        else:
            bill.username = requestData['username']
            bill.email = requestData['email']
            bill.first_name = requestData['first_name']
            bill.last_name = requestData['last_name']
            bill.last_updated = datetime.utcnow()
            db_session.commit()
            return {"meta":buildMeta(), "data": "Updated Record with ID " + bill_id}

    def post(self, bill_id=None):
        print json.loads(request.form['data'])
        app.logger.info("Creating User for: " + request.form['data'])
        requestData = json.loads(request.form['data'])
        newBill = Bill(requestData['user_id'], requestData['name'])
        db_session.add(newBill)
        db_session.commit()
        return {"meta":buildMeta(), "data": newBill.id}

    def delete(self, bill_id):
        app.logger.info("Deleting User #: " + bill_id)
        bill = Bill.query.filter_by(id=bill_id).first()
        db_session.delete(bill)
        db_session.commit()

        return {"meta":buildMeta(), "data" : "Deleted Record with ID " + bill_id}

api.add_resource(ApiBill, '/api/bill/', '/api/bill/<string:user_id>', '/api/bills/', '/api/bills/<string:user_id>')


def buildMeta():
    return [{"authors":["David Larrimore", "Robert Donovan"], "copyright": "Copyright 2015 MixFin LLC.", "version": "0.1"}]









@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()









########
# main #
########
if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host= '0.0.0.0', debug=True)