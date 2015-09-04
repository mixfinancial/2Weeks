__author__ = 'davidlarrimore'

import os, json, decimal
from datetime import datetime
from twoweeks.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    #return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]
    return value.strftime("%Y-%m-%d") + " " + value.strftime("%H:%M:%S")


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)





# USER MODEL
class Users(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(45))
    email = Column(String(120), unique=True, nullable=False)
    first_name = Column(String(120), unique=True)
    last_name = Column(String(120), unique=True)
    date_created = Column(DateTime(120), nullable=False)
    last_updated = Column(DateTime(120), nullable=False)

    def __init__(self, username, email, first_name=None, last_name=None):
        self.username = username

        self.email = email

        if first_name is None:
            first_name = "None"
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





# BILL MODEL
class Bills(Base):

    __tablename__ = 'bills'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(45), nullable=False)
    description = Column(String(255))
    recurring_flag = Column(Integer)
    amount = Column(Float(2))
    average_amount = Column(Float(2))
    recurrance = Column(String(45))
    next_due_date = Column(DateTime)
    payment_type_ind = Column(String(2))
    payment_method = Column(String(45))
    date_created = Column(DateTime(120), nullable=False)
    last_updated = Column(DateTime(120), nullable=False)

    def __init__(self, user_id, name, description=None, recurring_flag=None, amount=None, average_amount=None, recurrance=None, next_due_date=None, payment_type_ind=None, payment_method=None):
        self.user_id = user_id

        self.name = name

        if description is not None:
            self.description = description

        if recurring_flag is not None:
            self.recurring_flag = recurring_flag
        else:
            self.recurring_flag = 0

        if amount is not None:
            self.amount = amount

        if average_amount is not None:
            self.average_amount = average_amount

        if recurrance is not None:
            self.recurrance = recurrance

        if next_due_date is not None:
            self.next_due_date = recurrance

        if payment_type_ind is not None:
            self.payment_type = payment_type_ind

        if payment_method is not None:
            self.payment_method = payment_method


        self.date_created = datetime.utcnow()

        self.last_updated = datetime.utcnow()

    def __repr__(self):
        return "<User(id='%s', user_id='%s', name='%s', description='%s', recurring_flag='%s', amount='%s', average_amount='%s', recurrance='%s', next_due_date='%s', payment_type='%s', payment_method='%s', date_created='%s', last_updated='%s')>" % (
                                self.id, self.user_id, self.name, self.description, self.recurring_flag, self.amount, self.average_amount, self.recurrance, self.next_due_date, self.payment_type, self.payment_method, self.date_created, self.last_updated)


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'                 : self.id,
           'user_id'            : self.user_id,
           'name'               : self.name,
           'description'        : self.description,
           'recurring_flag'     : self.recurring_flag,
           'amount'             : str(self.amount),
           'average_amount'     : str(self.average_amount),
           'recurrance'         : self.recurrance,
           'next_due_date'      : dump_datetime(self.next_due_date),
           'payment_type_ind'   : self.payment_type_ind,
           'payment_method'     : self.payment_method,
           'date_created'       : dump_datetime(self.date_created),
           'last_updated'       : dump_datetime(self.last_updated)
       }

    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializeable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]




