from dotenv import load_dotenv
from flask import render_template
from flask import request
from utils.essentials import app
from utils.essentials import Base
from utils.essentials import Database
from utils.essentials import db
from utils.essentials import WebcredError
from utils.webcred import apiList
from utils.webcred import Webcred

import json
import logging
import os
import requests
import subprocess
import time


load_dotenv(dotenv_path='.env')
logger = logging.getLogger('WEBCred.app')
logging.basicConfig(
    filename='log/logging.log',
    filemode='a',
    format='[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)


# Our database model
class Features(Base):
    __tablename__ = 'features'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(), unique=True)
    redirected = db.Column(db.String())
    genre = db.Column(db.String(120))
    webcred_score = db.Column(db.FLOAT)
    error = db.Column(db.String(120))
    html = db.Column(db.String())
    text = db.Column(db.String())
    assess_time = db.Column(db.Float)

    # create columns of features
    for key in apiList.keys():
        dataType = apiList[key][-1]
        exec (key + " = db.Column(db." + dataType + ")")
        norm = key + 'norm'
        exec (norm + " = db.Column(db.Integer)")

    def __init__(self, data):
        for key in data.keys():
            setattr(self, key, data[key])

    def __repr__(self):
        return self.url


class Captcha(object):
    def __init__(self, resp=None, ip=None):
        google_api = 'https://www.google.com/recaptcha/api/siteverify'
        self.url = google_api
        self.key = '6LcsiCoUAAAAAL9TssWVBE0DBwA7pXPNklXU42Rk'
        self.resp = resp
        self.ip = ip
        self.params = {
            'secret': self.key,
            'response': self.resp,
            'remoteip': self.ip
        }

    def check(self):
        result = requests.post(url=self.url, params=self.params).text
        result = json.loads(result)
        return result.get('success', None)


@app.route("/start", methods=['GET'])
def start():

    addr = request.environ.get('REMOTE_ADDR')
    g_recaptcha_response = request.args.get('g-recaptcha-response', None)
    response_captcha = Captcha(ip=addr, resp=g_recaptcha_response)

    if not response_captcha.check():
        pass
        # result = "Robot not allowed"
        # return result

    data = collectData(request)

    return data


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def collectData(request):

    try:

        database = Database(Features)
        dt = Webcred(database, request)
        data = dt.assess()

    except WebcredError as e:
        data['Error'] = {e.message}

    # logger.info(data)
    return data


def appinfo(url=None):
    pid = os.getpid()
    # print pid
    cmd = ['ps', '-p', str(pid), '-o', "%cpu,%mem,cmd"]
    # print
    while True:
        info = subprocess.check_output(cmd)
        print info
        time.sleep(3)

    print 'exiting appinfo'
    return None


if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', debug=False, port=5050)
