__author__ = 'davidlarrimore'
import logging
from flask import Flask, render_template, request
from flask.ext.pymongo import PyMongo
from bson import json_util, ObjectId
import json

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'test'
mongo = PyMongo(app)


logging.basicConfig(filename='twoweeks.log',level=logging.DEBUG)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users')
def users():
    return json_util.dumps(mongo.db.users.find())


@app.route('/api/user/<user_id>')
def get_user(user_id):
    app.logger.debug('Looking for User: ' + user_id)
    user = mongo.db.users.find_one_or_404({'_id': ObjectId(user_id)})
    return json_util.dumps(user)


@app.route('/api/user/', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201


if __name__ == "__main__":
    app.run(debug=True)