from flask import Flask, abort, flash, redirect, render_template, request
from flask import url_for, jsonify, make_response
from utils import WebcredError
from utils import Urlattributes
from utils import MyThread
from utils import Captcha
from utils import Webcred
import utils
import UserDict
import pdb
import json
import threading
import time
from random import randint
from datetime import datetime
import subprocess
import os
import gc

app = Flask(__name__)

@app.route("/start",methods=['GET'])
def start():

    addr = request.environ.get('REMOTE_ADDR')
    g_recaptcha_response = request.args.get('g-recaptcha-response', None)

    if g_recaptcha_response:
        response_captcha = Captcha(ip=addr, resp=g_recaptcha_response)

    if not g_recaptcha_response or not response_captcha.check():
        result = "Robot not allowed"
        return result

    try:
        data = Webcred()
        data = data.assess(request)
    except WebcredError as e:
        data =  e.message

    data = jsonify(data)
    return data

@app.route("/")
def index():
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def collectData(url, request):

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
    # app.run(threaded=True, host='0.0.0.0', debug=False)

    '''
    BELOW ARE THE WORKER FUNCTIONS TO COLLECTDATA
    '''
    from pipeline import Pipeline
    from werkzeug.datastructures import ImmutableMultiDict
    # collectData, normalize, csv, json
    work = 'normalize'
    csv_filename = 'analysis/normalize.csv'
    data = []
    # pdb.set_trace()
    t = MyThread(Module='app', Method='appinfo', Name='appinfo', Url='url')
    t.start()
    # time.sleep(500)
    if work == 'collectData':
        link = open('APIs/urls.txt', 'r')
        links = link.readlines()
        link.close()
        # i = raw_input('Give me the url')
        # links = []
        # links.append(i)
        request = {}
        request = {
         'lastmod': 'true', 'domain': 'true', 'inlinks': 'true',
         'outlinks': 'true', 'hyperlinks': 'true', 'imgratio': 'true',
         'brokenlinks': 'true', 'cookie': 'true', 'langcount': 'true',
         'misspelled': 'true', 'wot': 'true', 'responsive': 'true',
         'pageloadtime': 'true','ads': 'true',
         }
        # request = ImmutableMultiDict(request)
        # pdb.set_trace()
        data = []
        threads = []
        now = datetime.now().time().isoformat()
        new_id = 'data.{}.{:04d}'.format(
                now,
                randint(0, 9999))
        new_id = 'DATA/' + str('data2')+'.json'

        data_file = open(new_id,'r')
        tempData = data_file.readlines()
        data_file.close()

        count = len(links)
        tempcounter = counter = len(tempData)

        for url in links[tempcounter:count]:
                    request['site'] = url[:-1]
                    dt = collectData(request['site'], request)
                    data_file = open(new_id,'a')
                    data.append(dt)
                    content = json.dumps(dt) + '\n'
                    data_file.write(content)
                    data_file.close()
                    counter += 1

    if not data:
        file_ = 'DATA/data2.json'
        file_ = open(file_, 'r').read()
        file_ = file_.split('\n')

        import json
        truncate_char = 0
        # pdb.set_trace()
        for element in file_[:-1]:
            # print str(element[4:])
            try:
                data.append(json.loads(str(element[truncate_char:])))
            except ValueError:
                # it happens when len(data) changes to 100 from 99
                truncate_char += 1
                data.append(json.loads(str(element[truncate_char:])))
                # pdb.set_trace()

    if work == 'normalize':
        # imgratio value are converted to int from float by multiple by 10^6
        normalizeCategory = {
        '3':{'outlinks': 'reverse', 'inlinks': 'linear', 'ads':'reverse',
         'brokenlinks': 'reverse', 'pageloadtime': 'reverse',
         'imgratio':'linear'},
        '2':{'misspelled': {0:1, 'else':0}, 'cookie': {'Yes':0, 'No':1},
         'responsive': {'true':1, 'false':0},},
        'not_sure': ['domain', 'langcount', 'lastmod'],
        'misc': ['hyperlinks'],
        'eval':['wot']
         }

        for k in normalizeCategory['3'].items():
            norm = utils.Normalize(data, k)
            data = norm.normalize()
        # pdb.set_trace()

        for k in normalizeCategory['2'].items():
            # pdb.set_trace()
            norm = utils.Normalize(data, k)
            data = norm.factoise()

        for index in range(len(data)):
            if data[index].get(normalizeCategory['misc'][0]):
                tempData = data[index].get(normalizeCategory['misc'][0])
                del data[index][normalizeCategory['misc'][0]]
                for k,v in tempData.items():
                    data[index][k] = v


        # print dt
        # pdb.set_trace()
        work = 'csv'
        csv_filename = 'normalized.csv'

    if work == 'csv':
        pipe = Pipeline()
        csv = pipe.convertjson(data)
        # pdb.set_trace()
        f = open(csv_filename,'w')
        f.write(csv)
        f.close()

    if work=='json':
        f = open(csv_filename, 'r')
        data = f.readlines()
        pipe = Pipeline()
        jsonData = pipe.converttojson(data)
        file_ = 'DATA/data.json'
        file_ = open(file_, 'a')
        for element in jsonData:
            element = json.dumps(element) + '\n'
            file_.write(element)
        file_.close()
