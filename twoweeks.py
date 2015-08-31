__author__ = 'davidlarrimore'
import logging
from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
from flask.ext.sqlalchemy import SQLAlchemy
from json import dumps
import models
from models import Users


import json

app = Flask(__name__)
api = Api(app)
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://twoweeks:twoweeks@mixfindb.c6uo5ewdeq5k.us-east-1.rds.amazonaws.com:3306/twoweeks'
db = SQLAlchemy(app)


#logging.basicConfig(filename='twoweeks.log',level=logging.DEBUG)


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
        db.session.add(newUser)
        db.session.commit()

        return {"status":"success", "New ID": newUser.id}


api.add_resource(ApiUsers, '/api/users')






#USERS
class ApiUser(Resource):
    def get(self, user_id):
        app.logger.info("looking for user:" + user_id)
        users = Users.query.filter_by(id=user_id).first()
        return jsonify(results=[users.serialize])
        return json.loads(json_util.dumps(user))

#    def put(self, user_id):
#        data=json.loads(request.form['data'])
#        app.logger.info("Creating User for: " + request.form['data'])
#        user_id = mongo.db.users.insert(data)
#        #user_id = mongo.db.users.insert({"email_address": "blarrimore5@gmail.com", "first_name": "Barbara", "last_name": "Larrimore", "password": "null", "username": "blarrimore5@gmail.com"}).inserted_id
#        return {"status":"success", "New ID": json.loads(json_util.dumps(user_id))["$oid"]}

api.add_resource(ApiUser, '/api/user/', '/api/user/<string:user_id>')






if __name__ == "__main__":
    app.run(debug=True)