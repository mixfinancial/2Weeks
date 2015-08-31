__author__ = 'davidlarrimore'

import logging
import json

from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
import os
from datetime import datetime
from database import db_session


#################
# configuration #
#################

app = Flask(__name__)

# Importing Models
from database import init_db
init_db()

from database import db_session
from models import Users




api = Api(app)


#logging.basicConfig(filename='twoweeks.log',level=logging.DEBUG)








##########
# routes #
##########


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test')
def test():
    return render_template('test.html')



# USER
class ApiUsers(Resource):
    def get(self):
        users = Users.query.all()
        return jsonify(results=[i.serialize for i in users])

    def post(self):
        app.logger.info("Creating User for: " + request.form['data'])
        requestData = json.loads(request.form['data'])
        newUser = Users(requestData['username'], requestData['email'], requestData['first_name'], requestData['last_name'])
        db_session.add(newUser)
        db_session.commit()

        return {"status":"success", "New ID": newUser.id}


api.add_resource(ApiUsers, '/api/users')



#USERS
class ApiUser(Resource):
    def get(self, user_id):
        app.logger.info("looking for user:" + user_id)
        user = Users.query.filter_by(id=user_id).first()

        if user is None:
            return {"status":"success", "message": "No results returned for user id #"+ user_id, "results":""}
        else:
            return jsonify(results=[user.serialize])

    def put(self, user_id):
        app.logger.info("Updating User for: " + request.form['data'])
        requestData = json.loads(request.form['data'])
        user = Users.query.filter_by(id=user_id).first()

        user.username = requestData['username']
        user.email = requestData['email']
        user.first_name = requestData['first_name']
        user.last_name = requestData['first_name']
        user.last_updated = datetime.utcnow()
        db_session.commit()

        return {"status":"success", "Updated ID": user.id}


    def delete(self, user_id):
        app.logger.info("Deleting User #: " + user_id)
        user = Users.query.filter_by(id=user_id).first()
        db_session.delete(user)
        db_session.commit()

        return {"status":"success", "Deleted #": user_id}



api.add_resource(ApiUser, '/api/user/', '/api/user/<string:user_id>')








if __name__ == "__main__":
    app.run(debug=True)