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
    return value.strftime("%Y-%m-%d") + "T" + value.strftime("%H:%M:%S")

def dump_date(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None

    #return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]
    return value.strftime("%Y-%m-%d")



class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)




############
# FEEDBACK #
############
class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey("user.id"))
    rating = Column(Integer())
    feedback = Column(String(1000))
    date_created = Column(DateTime(120), default=datetime.utcnow)
    last_updated = Column(DateTime(120), default=datetime.utcnow)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'type'          : 'feedback',
           'id'            : self.id,
           'user_id'       : self.user_id,
           'rating'        : self.rating,
           'feedback'      : self.feedback,
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
    account_balance_amount = Column(Float(2), default=0);

    bill = relationship("Bill")
    next_pay_date = Column(DateTime(120), default=datetime.utcnow)

    #TODO: This needs to be changed to an Indicator...
    #W: Weekly
    #B: Bi-Weekly
    #T: Twice Monthly (1st/15th)
    #M Monthly
    pay_recurrance_flag = Column(String(1), default="B");

    average_paycheck_amount = Column(Float(2), default="0");




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
            elif key=="average_paycheck_amount":
                self.average_paycheck_amount = value
            elif key=="pay_recurrance_flag":
                self.pay_recurrance_flag = value
            elif key=="next_pay_date":
                self.next_pay_date = value


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
           'type'                    : 'users',
           'id'                      : self.id,
           'username'                : self.username,
           'email'                   : self.email,
           #'password'               : self.password,
           'first_name'              : self.first_name,
           'last_name'               : self.last_name,
           'active'                  : self.active,
           'role_id'                 : self.role_id,
           'confirmed_at'            : self.confirmed_at,
           'next_pay_date'           : dump_datetime(self.next_pay_date),
           'pay_recurrance_flag'     : self.pay_recurrance_flag,
           'account_balance_amount'  : self.account_balance_amount,
           'average_paycheck_amount' : self.average_paycheck_amount,
           'date_created'            : dump_datetime(self.date_created),
           'last_updated'            : dump_datetime(self.last_updated)
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
    paid_flag = Column(Boolean(), default=False)
    payment_processing_flag = Column(Boolean(), default=False)
    funded_flag = Column(Boolean(), default=False)
    paid_date = Column(DateTime())
    check_number = Column(Integer)
    payment_plan_items = relationship("Payment_Plan_Item", backref="bill",cascade="all, save-update, merge, delete")



    #CC: Credit Card
    #CH: Cash
    #CK: Check
    #DD: Direct Deposit
    payment_method_ind = Column(String(2), default="CC")

    #A: Automatic
    #M: Manual
    payment_type_ind = Column(String(1), default="M")

    date_created = Column(DateTime(120), default=datetime.utcnow)
    last_updated = Column(DateTime(120), default=datetime.utcnow)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'type'                    : 'bills',
           'id'                      : self.id,
           'user_id'                 : self.user_id,
           'payee_id'                : self.payee_id,
           'name'                    : self.name,
           'description'             : self.description,
           'due_date'                : dump_date(self.due_date),
           'billing_period'          : dump_date(self.billing_period),
           'total_due'               : self.total_due,
           'paid_flag'               : self.paid_flag,
           'payment_processing_flag' : self.payment_processing_flag,
           'funded_flag'             : self.funded_flag,
           'paid_date'               : dump_datetime(self.paid_date),
           'check_number'            : self.check_number,
           'payment_method_ind'      : self.payment_method_ind,
           'payment_type_ind'        : self.payment_type_ind,
           'payment_plan_items'      : [ item.serialize for item in self.payment_plan_items],
           'date_created'            : dump_datetime(self.date_created),
           'last_updated'            : dump_datetime(self.last_updated)
       }

    @property
    def serialize_many2many(self):
       """
       Return object's relations in easily serializeable format.
       NB! Calls many2many's serialize property.
       """
       return [ item.serialize for item in self.many2many]







#################
# PAYMENT PLAN  #
#################
class Payment_Plan(Base):

    __tablename__ = 'payment_plan'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    amount = Column(Float(2), default=0)
    base_flag = Column(Boolean, default=False)
    transfer_date = Column(DateTime(120), default=datetime.utcnow)
    date_created = Column(DateTime(120), default=datetime.utcnow)
    last_updated = Column(DateTime(120), default=datetime.utcnow)
    accepted_flag = Column(Boolean, default=False)
    payment_plan_items = relationship("Payment_Plan_Item", backref="payment_plan",cascade="all, save-update, merge, delete")


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'type'               : 'payment_plan',
           'id'                 : self.id,
           'user_id'            : self.user_id,
           'base_flag'          : self.base_flag,
           'accepted_flag'      : self.accepted_flag,
           'amount'             : self.amount,
           'payment_plan_items' : [ item.serialize for item in self.payment_plan_items],
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
# PAYMENT PLAN ITEM #
#####################

class Payment_Plan_Item(Base):

    __tablename__ = 'payment_plan_item'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    bill_id = Column(Integer, ForeignKey("bill.id"), nullable=False)
    payment_plan_id = Column(Integer, ForeignKey("payment_plan.id"), nullable=False)
    amount = Column(Float(2))
    accepted_flag = Column(Boolean, default=False)
    date_created = Column(DateTime(120), default=datetime.utcnow)
    last_updated = Column(DateTime(120), default=datetime.utcnow)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'type'               : 'payment_plan_item',
           'user_id'            : self.user_id,
           'id'                 : self.id,
           'bill_id'            : self.bill_id,
           'payment_plan_id'    : self.payment_plan_id,
           'amount'             : self.amount,
           'accepted_flag'      : self.accepted_flag,
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





