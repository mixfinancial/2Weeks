__author__ = 'davidlarrimore'

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('mysql://twoweeks:twoweeks@mixfindb.c6uo5ewdeq5k.us-east-1.rds.amazonaws.com:3306/twoweeks', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=True,
                                         autoflush=True,
                                         bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()



def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import twoweeks.models
    Base.metadata.create_all(bind=engine)