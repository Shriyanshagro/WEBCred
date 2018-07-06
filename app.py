from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from utils.essentials import WebcredError
from utils.webcred import Webcred

import json
import os
import requests
import subprocess
import time


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/webcred'
db = SQLAlchemy(app)


# Create our database model
class Features(db.Model):
    __tablename__ = "features"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120), unique=True)

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return '<URL %r>' % self.url


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
        result = "Robot not allowed"
        return result

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
        dt = Webcred(db, Features, request)
        data = dt.assess()
        data = jsonify(data)

    except WebcredError as e:
        data['Error'] = {e.message}

    print data
    return data


def appinfo(url=None):
    pid = os.getpid()
    # print pid
    cmd = ['ps', '-p', str(pid), '-o', "%cpu,%mem,cmd"]
    # print
    # pdb.set_trace()
    while True:
        info = subprocess.check_output(cmd)
        print info
        time.sleep(3)

    print 'exiting appinfo'
    return None


if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', debug=True)
