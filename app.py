from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from utils.utils import Captcha
from utils.utils import Webcred
from utils.utils import WebcredError

import os
import subprocess
import time


app = Flask(__name__)


@app.route("/start", methods=['GET'])
def start():

    addr = request.environ.get('REMOTE_ADDR')
    g_recaptcha_response = request.args.get('g-recaptcha-response', None)

    if g_recaptcha_response:
        response_captcha = Captcha(ip=addr, resp=g_recaptcha_response)

    if not g_recaptcha_response or not response_captcha.check():
        pass
        # result = "Robot not allowed"
        # return result

    try:
        data = Webcred()
        data = data.assess(request)
    except WebcredError as e:
        data = e.message

    data = jsonify(data)
    return data


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def collectData(request):

    try:
        dt = Webcred()
        dt = dt.assess(request)
        # print dt

    except WebcredError as e:
        dt['Error'] = {e.message}

    print dt
    return dt


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
    app.run(threaded=True, host='0.0.0.0', debug=False)
