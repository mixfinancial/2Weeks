__author__ = 'davidlarrimore'
import logging
from flask import Flask, render_template, request
from flask_restful import Resource, Api
from flask.ext.pymongo import PyMongo
from bson import json_util, ObjectId
import json

app = Flask(__name__)
api = Api(app)
app.config['MONGO_DBNAME'] = 'test'
mongo = PyMongo(app)


logging.basicConfig(filename='twoweeks.log',level=logging.DEBUG)


@app.route('/')
def index():
    return render_template('index.html')


# @app.route('/users')
# def users():
#     return json_util.dumps(mongo.db.users.find())



# USER
class Users(Resource):
    def get(self):
        #return {'hello': 'world'}
        return json.loads(json_util.dumps(mongo.db.users.find()))

api.add_resource(Users, '/api/users')

#USERS
class User(Resource):
    def get(self, user_id):
        user = mongo.db.users.find_one_or_404({'_id': ObjectId(user_id)})
        app.logger.info("looking for user:" + user_id)
        return json.loads(json_util.dumps(user))

    def put(self, user_id):
        data=json.loads(request.form['data'])
        app.logger.info("Creating User for: " + request.form['data'])
        user_id = mongo.db.users.insert(data)
        #user_id = mongo.db.users.insert({"email_address": "blarrimore5@gmail.com", "first_name": "Barbara", "last_name": "Larrimore", "password": "null", "username": "blarrimore5@gmail.com"}).inserted_id
        return {"status":"success", "New ID": json.loads(json_util.dumps(user_id))["$oid"]}

    def post(self):
        data=json.loads(request.form['data'])
        app.logger.info("Creating User for: " + request.form['data'])
        user_id = mongo.db.users.insert(data)
        #user_id = mongo.db.users.insert({"email_address": "blarrimore5@gmail.com", "first_name": "Barbara", "last_name": "Larrimore", "password": "null", "username": "blarrimore5@gmail.com"}).inserted_id
        return {"status":"success", "New ID": json.loads(json_util.dumps(user_id))["$oid"]}


api.add_resource(User, '/api/user/', '/api/user/<string:user_id>')






if __name__ == "__main__":
    app.run(debug=True)