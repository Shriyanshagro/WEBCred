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

if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', debug=True)

    # from pipeline import Pipeline
    # from werkzeug.datastructures import ImmutableMultiDict
    # work = 'None'
    # data = []
    #
    # if work:
    #     link = open('APIs/urls.txt', 'r')
    #     links = link.readlines()
    #     link.close()
    #     # i = raw_input('Give me the url')
    #     # links = []
    #     # links.append(i)
    #     count = 100
    #     counter = 0
    #     request = {}
    #     request = {
    #      'lastmod': 'true', 'domain': 'true', 'inlinks': 'true',
    #      'outlinks': 'true', 'hyperlinks': 'true', 'imgratio': 'true',
    #      'brokenlinks': 'true', 'cookie': 'true', 'langcount': 'true',
    #      'misspelled': 'true', 'wot': 'true', 'responsive': 'true',
    #      'pageloadtime': 'true','ads': 'true',
    #      }
    #     # request = ImmutableMultiDict(request)
    #     # pdb.set_trace()
    #     data = []
    #     threads = []
    #     now = datetime.now().time().isoformat()
    #     new_id = 'data.{}.{:04d}'.format(
    #             now,
    #             randint(0, 9999))
    #     new_id = 'DATA/' + str(new_id)+'.json'
    #     data_file = open(new_id,'w')
    #     data_file.close()
    #
    #     for url in links[:count]:
    #                 request['site'] = url[:-1]
    #                 dt = collectData(request['site'], request)
    #                 data_file = open(new_id,'a')
    #                 data.append(dt)
    #                 # print dt
    #                 content = '"' + str(counter)+ '"' + ": " + json.dumps(dt) + '\n'
    #                 # pdb.set_trace()
    #                 data_file.write(content)
    #                 data_file.close()
    #                 counter += 1
    #
    # else:
    #     if not data:
    #         file_ = 'DATA/data.00:56:36.889197.7922.json'
    #         file_ = open(file_, 'r').read()
    #         file_ = file_.split('\n')
    #         import json
    #         for element in file_[:-1]:
    #             # print str(element[4:])
    #             # pdb.set_trace()
    #             data.append(json.loads(str(element[4:])))
    #     # pdb.set_trace()
    #     norm = utils.Normalize(data, 'outlinks')
    #     dt = norm.normalize()
    #     print dt
    #
    #     # data = open('jsondata.json','r')
    #     # data = data.readlines()
    #     # dict_list = []
    #     # for index in range(len(data)):
    #     #     # pdb.set_trace()
    #     #     temp = data[index]
    #     #     temp = temp[:-1]
    #     #     temp = '{' + temp + '}'
    #     #     temp = json.loads(temp)
    #     #     dict_list.append(temp)
    #     #     # dict_[temp.keys()[0]] = temp.values()[0]
    #     # pipe = Pipeline()
    #     # csv = pipe.convertjson(dict_list)
    #     # pdb.set_trace()
    #     # f = open('csvData.csv','w')
    #     # f.write(csv)
