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
        return json.loads(json_util.dumps(user))

    def put(self, user_id):
        user = mongo.db.users.find_one_or_404({'_id': ObjectId(user_id)})
        return json.loads(json_util.dumps(user))

api.add_resource(User, '/api/user/<string:user_id>')



if __name__ == "__main__":
    app.run(debug=True)