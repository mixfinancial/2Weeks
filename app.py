from flask import Flask, render_template
from flask.ext.pymongo import PyMongo
from bson import json_util, ObjectId
import json



app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'test'
mongo = PyMongo(app)

@app.route('/')
def index():
    users = mongo.db.users.find()
    app.logger.info('Info')
    for user in mongo.db.users.find():
        print(user)
    return render_template('index.html',
        users=users)



@app.route('/users')
def users():
    return json_util.dumps(mongo.db.users.find())






if __name__ == "__main__":
    app.run()