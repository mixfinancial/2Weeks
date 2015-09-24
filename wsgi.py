__author__ = 'Robert Donovan'

##import newrelic.agent
##newrelic.agent.initialize('newrelic.ini')

from flask import Flask
application = Flask(__name__)

def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ["Hello!"]

