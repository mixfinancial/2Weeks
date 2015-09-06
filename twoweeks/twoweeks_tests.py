__author__ = 'davidlarrimore'
import os
import twoweeks
from flask import Flask
from bson import json_util, ObjectId
import unittest
import tempfile



class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = twoweeks.app.test_client()


    def test_empty_db(self):
        #http://localhost:5000/api/user/55d28e50ade5cb5b660f572e
        rv = self.app.get('/api/user/55d28e50ade5cb5b660f572e')
        assert '{"username": "davidlarrimore", "first_name": "David", "last_name": "Larrimore", "password": null, "_id": {"$oid": "55d28e50ade5cb5b660f572e"}, "email_address": "davidlarrimore@gmail.com"}' in rv.data


if __name__ == '__main__':
    unittest.main()