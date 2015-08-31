__author__ = 'davidlarrimore'
import logging
from flask import Flask, render_template, request
from flask_restful import Resource, Api
from flask.ext.sqlalchemy import SQLAlchemy
from bson import json_util, ObjectId
from datetime import datetime
import json

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://twoweeks:twoweeks@mixfindb.c6uo5ewdeq5k.us-east-1.rds.amazonaws.com:3306/twoweeks'
db = SQLAlchemy(app)


logging.basicConfig(filename='twoweeks.log',level=logging.DEBUG)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test')
def test():
    return render_template('test.html')


# USER MODEL
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(120), unique=True)
    last_name = db.Column(db.String(120), unique=True)
    date_created = db.Column(db.DateTime(120), unique=True)
    last_updated = db.Column(db.DateTime(120), unique=True)

    def __init__(self, username, email, first_name=None, last_name=None):
        self.username = username

        self.email = email

        if first_name is None:
            first_date = "None"
        self.first_name = first_name

        if last_name is None:
            last_name = "None"
        self.last_name = last_name

        self.last_updated = datetime.utcnow()

        self.last_updated = datetime.utcnow()

    def __repr__(self):
        return "<User(id='%s', username='%s', email='%s', password='%s', first_name='%s', last_name='%s', date_created='%s', last_updated='%s')>" % (
                                self.id, self.username, self.email, self.password, self.first_name, self.date_created, self.last_updated)




# USER
class APIUsers(Resource):
    def get(self):
        users = Users.query.filter_by(username='deleteme').first()
        return {'hello': users.username}
        #return json.loads(json_util.dumps(mongo.db.users.find()))

api.add_resource(APIUsers, '/api/users')













#USERS
#class User(Resource):
#    def get(self, user_id):
#        user = mongo.db.users.find_one_or_404({'_id': ObjectId(user_id)})
#        app.logger.info("looking for user:" + user_id)
#        return json.loads(json_util.dumps(user))

#    def put(self, user_id):
#        data=json.loads(request.form['data'])
#        app.logger.info("Creating User for: " + request.form['data'])
#        user_id = mongo.db.users.insert(data)
#        #user_id = mongo.db.users.insert({"email_address": "blarrimore5@gmail.com", "first_name": "Barbara", "last_name": "Larrimore", "password": "null", "username": "blarrimore5@gmail.com"}).inserted_id
#        return {"status":"success", "New ID": json.loads(json_util.dumps(user_id))["$oid"]}

#    def post(self):
#        data=json.loads(request.form['data'])
#        app.logger.info("Creating User for: " + request.form['data'])
#        user_id = mongo.db.users.insert(data)
#        #user_id = mongo.db.users.insert({"email_address": "blarrimore5@gmail.com", "first_name": "Barbara", "last_name": "Larrimore", "password": "null", "username": "blarrimore5@gmail.com"}).inserted_id
#        return {"status":"success", "New ID": json.loads(json_util.dumps(user_id))["$oid"]}


#api.add_resource(User, '/api/user/', '/api/user/<string:user_id>')






if __name__ == "__main__":
    app.run(debug=True)