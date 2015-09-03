__author__ = 'davidlarrimore'

import json
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api, reqparse


#################
# configuration #
#################

app = Flask(__name__)
app.config['TRAP_BAD_REQUEST_ERRORS'] = True


# Importing Models
from twoweeks.database import init_db
init_db()

from twoweeks.database import db_session
from twoweeks.models import Users




api = Api(app)


#logging.basicConfig(filename='twoweeks.log',level=logging.DEBUG)








##########
# routes #
##########


@app.route('/')
def index():
    return render_template('index.html')


# USER
class ApiUsers(Resource):
    def get(self):
        users = [i.serialize for i in Users.query.all()]
        return {"meta":buildMeta(), "error":"none", "data":[i.serialize for i in Users.query.all()]}

    def post(self):
        app.logger.info("Creating User for: " + request.form['data'])
        requestData = json.loads(request.form['data'])
        newUser = Users(requestData['username'], requestData['email'], requestData['first_name'], requestData['last_name'])
        db_session.add(newUser)
        db_session.commit()
        return {"meta":buildMeta(), "error":"none", "data": newUser.id}


api.add_resource(ApiUsers, '/api/users')



#USERS
class ApiUser(Resource):
    def get(self, user_id=None):

        if user_id is not None:
            app.logger.info("looking for user:" + user_id)
            user = Users.query.filter_by(id=user_id).first()
            if user is None:
                return {"meta":buildMeta(), "status":"success", "error": "No results returned for user id #"+ user_id, "data":""}
            else:
                return jsonify(meta=buildMeta(), data=[user.serialize])
        else:
            users = [i.serialize for i in Users.query.all()]
            return {"meta":buildMeta(), "error":"none", "data":[i.serialize for i in Users.query.all()]}

    def put(self, user_id):
        print json.loads(request.form['data'])
        app.logger.info("Updating User for: " + request.form['data'])
        requestData = json.loads(request.form['data'])

        user = Users.query.filter_by(id=user_id).first()
        if user is None:
            return {"meta":buildMeta(), "status":"success", "error": "No results returned for user id #"+ user_id, "data":""}
        else:
            user.username = requestData['username']
            user.email = requestData['email']
            user.first_name = requestData['first_name']
            user.last_name = requestData['last_name']
            user.last_updated = datetime.utcnow()
            db_session.commit()
            return {"meta":buildMeta(), "error":"none", "data": "Updated Record with ID " + user_id}


    def post(self, user_id=None):
        print json.loads(request.form['data'])
        app.logger.info("Creating User for: " + request.form['data'])
        requestData = json.loads(request.form['data'])
        newUser = Users(requestData['username'], requestData['email'], requestData['first_name'], requestData['last_name'])
        db_session.add(newUser)
        db_session.commit()
        return {"meta":buildMeta(), "error":"none", "data": newUser.id}

    def delete(self, user_id):
        app.logger.info("Deleting User #: " + user_id)
        user = Users.query.filter_by(id=user_id).first()
        db_session.delete(user)
        db_session.commit()

        return {"meta":buildMeta(), "error":"none", "data" : "Deleted Record with ID " + user_id}


api.add_resource(ApiUser, '/api/user/', '/api/user/<string:user_id>')


def buildMeta():
    return [{"authors":["David Larrimore", "Robert Donovan"], "copyright": "Copyright 2015 MixFin LLC.", "version": "0.1"}]



@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



if __name__ == "__main__":
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)