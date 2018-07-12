from ast import literal_eval
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

import logging
import os
import sys
import threading
import traceback


load_dotenv(dotenv_path='.env')

logger = logging.getLogger('WEBCred.essentials')
logging.basicConfig(
    filename='log/logging.log',
    filemode='a',
    format='[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
'''
To create our database based off our model, run the following commands
$ python
>>> from app import db
>>> db.create_all()
>>> exit()'''

Base = declarative_base()


# A class to catch error and exceptions
class WebcredError(Exception):
    """An error happened during assessment of site.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class MyThread(threading.Thread):
    # def __init__(
    #         self, Module='api', Method=None, Name=None, Url=None, Args=None
    # ):
    #     pass

    def __init__(self, func, Name, Url, Args=None):

        threading.Thread.__init__(self)

        self.func = func
        self.name = Name
        self.url = Url
        self.args = Args
        self.result = None

        if Args and Args != '':
            self.args = Args

    def run(self):
        try:
            if self.args:
                self.result = self.func(self.url, self.args)
            else:
                self.result = self.func(self.url)
        except Exception:
            # Get current system exception
            ex_type, ex_value, ex_traceback = sys.exc_info()

            # Extract unformatter stack traces as tuples
            trace_back = traceback.extract_tb(ex_traceback)

            # Format stacktrace
            stack_trace = list()

            for trace in trace_back:
                stack_trace.append(
                    "File : %s , Line : %d, Func.Name : %s, Message : %s" %
                    (trace[0], trace[1], trace[2], trace[3])
                )

            # print("Exception type : %s " % ex_type.__name__)
            if not ex_value.message == 'Response 202':
                logger.info('{}:{}'.format(ex_type.__name__, ex_value))
                logger.info(stack_trace)

            self.result = None

    def getResult(self):
        return self.result

    # clear url if Urlattributes object
    def freemem(self):
        self.url.freemem()


class Database(object):
    def __init__(self, database):
        engine = db.engine
        # check existence of table in database
        if not engine.dialect.has_table(engine, database.__tablename__):
            # db.create_all()
            Base.metadata.create_all(engine, checkfirst=True)
            logger.info('Created table {}'.format(database.__tablename__))

        self.db = db
        self.database = database

    def filter(self, name, value):

        return self.db.session.query(
            self.database
        ).filter(getattr(self.database, name) == value)

    def exist(self, name, value):

        if self.filter(name, value).count():
            return True

        return False

    def getdb(self):
        return self.db

    def getsession(self):
        return self.db.session

    def add(self, data):
        reg = self.database(data)
        self.db.session.add(reg)
        self.commit()

    def update(self, name, value, data):
        if not self.filter(name, value).count():
            self.add(data)
        else:
            self.filter(name, value).update(data)
            self.commit()

    def commit(self):
        try:
            self.db.session.commit()
        except Exception:
            # Get current system exception
            ex_type, ex_value, ex_traceback = sys.exc_info()

            # Extract unformatter stack traces as tuples
            trace_back = traceback.extract_tb(ex_traceback)

            # Format stacktrace
            stack_trace = list()

            for trace in trace_back:
                stack_trace.append(
                    "File : %s , Line : %d, Func.Name : %s, Message : %s" %
                    (trace[0], trace[1], trace[2], trace[3])
                )

            # print("Exception type : %s " % ex_type.__name__)
            logger.debug(ex_value)
            logger.debug(stack_trace)

            logger.debug('Rolling back db commit')
            self.getsession().rollback()

    def getdata(self, name=None, value=None):

        return self.filter(name, value).all()[0].__dict__

    def getcolumns(self):

        return self.database.metadata.tables[self.database.__tablename__
                                             ].columns.keys()

    def gettablename(self):

        return self.database.__tablename__

    def getcolumndata(self, column):
        return self.getsession().query(getattr(self.database, column))


def getlistform(temp):
    data = []
    if isinstance(temp, list):
        for i in temp:
            data.append(literal_eval(i[0]))

    return data
