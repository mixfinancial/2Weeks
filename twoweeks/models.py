__author__ = 'davidlarrimore'

import os, json, decimal
from datetime import datetime
from twoweeks.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash



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




# ROLE MODEL
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




# USER MODEL
class User(Base):

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



# BILL MODEL
class Bill(Base):

    __tablename__ = 'bill'

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

