__author__ = 'davidlarrimore'

import os, json, decimal
from datetime import datetime
from twoweeks.database import Base
import twoweeks.config as config
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)



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




########
# ROLE #
########
class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer(), primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    date_created = Column(DateTime(120), default=datetime.utcnow)
    last_updated = Column(DateTime(120), default=datetime.utcnow)
    user = relationship("User")

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'type'          : 'role',
           'id'            : self.id,
           'name'          : self.name,
           'description'   : self.description,
           'date_created'  : dump_datetime(self.date_created),
           'last_updated'  : dump_datetime(self.last_updated)
       }

    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializeable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]




########
# USER #
########
class User(Base, UserMixin):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255))
    email = Column(String(120), unique=True, nullable=False)
    first_name = Column(String(120))
    last_name = Column(String(120))
    date_created = Column(DateTime(120), default=datetime.utcnow)
    last_updated = Column(DateTime(120), default=datetime.utcnow)

    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    role_id = Column(Integer, ForeignKey('role.id'))
    bill = relationship("Bill")

    def __init__(self, **kwargs):
        # Setting Defaults
        active = True
        role_id = 1;

        for key, value in kwargs.iteritems():
            if key=="first_name":
                self.first_name = value
            elif key=="last_name":
                self.last_name = value
            elif key=="username":
                self.email = value
                self.username = value
            elif key=="password":
                self.password = self.hash_password(value)
            elif key=="role_id":
                role_id = value
            elif key=="active":
                active = value

        self.role_id = role_id
        self.date_created = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        self.active = active;

    def hash_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def generate_auth_token(self, expiration = 600):
        s = Serializer(config.SECRET_KEY, expires_in = expiration)
        return s.dumps({ 'id': self.id })

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(config.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'type'        : 'users',
           'id'          : self.id,
           'username'    : self.username,
           'email'       : self.email,
           'password'    : self.password,
           'first_name'  : self.first_name,
           'last_name'   : self.last_name,
           'active'      : self.active,
           'role_id'     : self.role_id,
           'confirmed_at': self.confirmed_at,
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








# PAYEE MODEL
class Payee(Base):

    __tablename__ = 'payee'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String(45), nullable=False)
    description = Column(String(255))
    recurring_flag = Column(Integer)
    amount = Column(Float(2))
    average_amount = Column(Float(2))
    recurrance = Column(String(45))
    next_due_date = Column(DateTime)
    payment_type_ind = Column(String(2))
    payment_method = Column(String(45))
    date_created = Column(DateTime(120), default=datetime.utcnow)
    last_updated = Column(DateTime(120), default=datetime.utcnow)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'type'               : 'payee',
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




########
# BILL #
########
class Bill(Base):

    __tablename__ = 'bill'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    payee_id = Column(Integer, ForeignKey("payee.id"), nullable=True)
    name = Column(String(45), nullable=False)
    description = Column(String(255))
    due_date = Column(DateTime(120))
    billing_period = Column(DateTime(120))
    total_due = Column(Float(2))
    paid_flag = Column(Boolean())
    paid_date = Column(DateTime())
    check_number = Column(Integer)
    payment_type = Column(String(45))
    date_created = Column(DateTime(120), default=datetime.utcnow)
    last_updated = Column(DateTime(120), default=datetime.utcnow)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'type'               : 'bills',
           'user_id'            : self.user_id,
           'payee_id'           : self.payee_id,
           'name'               : self.name,
           'description'        : self.description,
           'due_date'           : dump_datetime(self.due_date),
           'billing_period'     : dump_datetime(self.billing_period),
           'total_due'          : str(self.total_due),
           'paid_flag'          : self.paid_flag,
           'paid_date'          : dump_datetime(self.paid_date),
           'check_number'       : self.check_number,
           'payment_type'       : self.payment_type,
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




##################
# FUNDS TRANSFER #
##################
class Funds_Transfer(Base):

    __tablename__ = 'funds_transfer'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    amount = Column(Float(2))
    transfer_date = Column(DateTime(120), default=datetime.utcnow)
    date_created = Column(DateTime(120), default=datetime.utcnow)
    last_updated = Column(DateTime(120), default=datetime.utcnow)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'type'               : 'funds_Transfer',
           'user_id'            : self.user_id,
           'amount'             : str(self.amount),
           'transfer_date'      : dump_datetime(self.transfer_date),
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




#####################
# BILL FUNDING ITEM #
#####################

class Bill_Funding_Item(Base):

    __tablename__ = 'bill_funding_item'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    bill_id = Column(Integer, ForeignKey("bill.id"), nullable=False)
    funds_transfer_id = Column(Integer, ForeignKey("funds_transfer.id"), nullable=True)
    amount = Column(Float(2))

    date_created = Column(DateTime(120), default=datetime.utcnow)
    last_updated = Column(DateTime(120), default=datetime.utcnow)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'type'               : 'bill_funding_item',
           'user_id'            : self.user_id,
           'bill_id'            : self.bill_id,
           'funds_transfer_id'  : self.funds_transfer_id,
           'amount'             : str(self.amount),
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





