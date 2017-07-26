from flask import Flask, abort, flash, redirect, render_template, request
from flask import url_for, jsonify, make_response
from utils import WebcredError
from utils import Urlattributes
from utils import MyThread
from utils import Captcha
import json
import UserDict
import pdb

app = Flask(__name__)

@app.route("/start",methods=['GET'])
def start():
    # pdb.set_trace()
    addr = request.environ.get('REMOTE_ADDR')
    g_recaptcha_response = request.args.get('g-recaptcha-response')
    response_captcha = Captcha(ip=addr, resp=g_recaptcha_response)
    if not response_captcha.check():
        result = "Robot not allowed"
        return result
    try:
        data = {}
        req = {}
        req['args'] = {}
        hyperlinks_attributes = ['contact', 'email', 'help', 'recommend',
        'sitemap']
        apiList = {
            'lastmod': ['getDate', '', ''],
            'domain': ['getDomain', '', ''],
            'inlinks': ['getInlinks', '', ''],
            'outlinks': ['getOutlinks', '', ''],
            'hyperlinks': ['getHyperlinks', hyperlinks_attributes, ''],
            'imgratio': ['getImgratio', '', ''],
            'brokenlinks': ['getBrokenlinks', '', ''],
            'cookie': ['getCookie', '', ''],
            'langcount': ['getLangcount', '', ''],
            'misspelled': ['getMisspelled', '', ''],
            'wot': ['getWot', '', ''],
            'responsive': ['getResponsive', '', ''],
            'ads': ['getAds', '', ''],
            'pageloadtime': ['getPageloadtime', '', ''],
            'site': ['']
        }

        # for production start method
        # req['args']['site'] = request.args.get('site', None)
        for keys in apiList.keys():
            # because request.args is of ImmutableMultiDict form
            if request.args.get(keys, None):
                req['args'][keys] = request.args.get(keys)

        # pdb.set_trace()
        # for debug method
        # req['args'] = request['args']
        # site = str(req['args'].get('site', None))

        try:
            site = Urlattributes(url=req['args'].get('site', None))
        except WebcredError as e:
            raise WebcredError(e.message)

        del req['args']['site']
        data['url'] = site.geturl()

        threads = []

        for keys in req['args'].keys():
            if str(req['args'].get(keys, None))=="true":
                try:
                    thread = MyThread(Method=apiList[keys][0], Name=keys, Url=site,
                    Args=apiList[keys][1])
                    thread.start()
                    threads.append(thread)
                except WebcredError as e:
                    # print keys, e.message
                    continue

        for t in threads:
            t.join()
            data[t.getName()] = t.getResult()

    except WebcredError as e:
        data =  WebcredError(e.message).message

    #  for production mode
    data = jsonify(data)
    # print data
    return data

@app.route("/")
def index():
    # print 'index'
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', debug=False)

    # data = {'lastmod': 'true', 'domain': 'true', 'inlinks': 'true',
    #  'outlinks': 'true', 'hyperlinks': 'true', 'imgratio': 'true',
    #  'brokenlinks': 'false', 'cookie': 'true', 'langcount': 'true',
    #  'misspelled': 'true', 'responsive': 'true', 'wot': 'true',
    #  'pageloadtime': 'true','ads': 'true',
    #  'site': 'https://threatpost.com/'}
    #
    # request = UserDict.UserDict(args=data)
    #
    # debug_start(request)
    # pdb.set_trace()
    # print result
