__author__ = 'davidlarrimore'

import os
from datetime import datetime
from twoweeks.database import Base
from sqlalchemy import Column, Integer, String, DateTime


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    #return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]
    return value.strftime("%Y-%m-%d") + " " + value.strftime("%H:%M:%S")



# USER MODEL
class Users(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    password = Column(String(45))
    email = Column(String(120), unique=True)
    first_name = Column(String(120), unique=True)
    last_name = Column(String(120), unique=True)
    date_created = Column(DateTime(120), unique=True)
    last_updated = Column(DateTime(120), unique=True)

    def __init__(self, username, email, first_name=None, last_name=None):
        self.username = username

        self.email = email

        if first_name is None:
            first_date = "None"
        self.first_name = first_name

        if last_name is None:
            last_name = "None"
        self.last_name = last_name

        self.date_created = datetime.utcnow()

        self.last_updated = datetime.utcnow()

    def __repr__(self):
        return "<User(id='%s', username='%s', email='%s', password='%s', first_name='%s', last_name='%s', date_created='%s', last_updated='%s')>" % (
                                self.id, self.username, self.email, self.password, self.first_name, self.date_created, self.last_updated)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'          : self.id,
           'username'    : self.username,
           'email'       : self.email,
           'password'    : self.password,
           'first_name'  : self.first_name,
           'last_name'   : self.last_name,
           'date_created': dump_datetime(self.date_created),
           'last_updated': dump_datetime(self.last_updated)
       }

    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializeable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]