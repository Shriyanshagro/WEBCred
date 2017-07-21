from flask import Flask, abort, flash, redirect, render_template, request
from flask import url_for, jsonify, make_response
import api
from utils import WebcredError
from utils import Urlattributes
import json
import pdb

# debugging imports
import UserDict

app = Flask(__name__)

@app.route("/start",methods=['GET'])
def start():

    data = {}
    site = str(request.args.get('site', None))
    #  object
    try:
        site = Urlattributes(url=site)
        data['site'] = site.geturl()

        # pdb.set_trace()
        if str(request.args.get('lastmod', None))=="true":
        	try:
        		data['lastmod'] = api.getDate(site)
        	except WebcredError as e:
        		data['lastmod'] = e.message
        	except:
        		data['lastmod'] = '+++'
        if str(request.args.get('domain', None))=="true":
            try:
                data['domain'] = api.getDomain(site)
            except WebcredError as e:
                data['domain'] = e.message
            except:
                data['domain'] = '+++'
        if str(request.args.get('inlinks', None))=="true":
            try:
            	data['inlinks'] = api.getInLinks(site)
            except WebcredError as e:
                data['inlinks'] = str(e.message)
            except:
                data['inlinks'] = '+++'
        if str(request.args.get('outlinks', None))=="true":
            try:
            	data['outlinks'] = api.getOutLinks(site)
            except WebcredError as e:
                data['outlinks'] = str(e.message)
            except:
                data['outlinks'] = '+++'
        if str(request.args.get('hyperlinks', None))=="true":
            attributes = ['contact', 'email', 'help', 'recommend', 'sitemap']
            try:
            	data['hyperlinks'] = api.check_hyperlinks(site, attributes)
            except WebcredError as e:
                data['hyperlinks'] = e.message
            except:
                data['hyperlinks'] = '+++'
        if str(request.args.get('imgratio', None))=="true":
            try:
                data['imgratio'] = api.check_size_ratio(site)
            except WebcredError as e:
                data['imgratio'] = e.message
            except:
                data['imgratio'] = '+++'
        if str(request.args.get('brokencount', None))=="true":
            try:
                data['brokencount'] = api.getBrokenLinks(site)
            except WebcredError as e:
                data['brokencount'] = e.message
            except:
                data['brokencount'] = '+++'
        if str(request.args.get('cookie', None))=="true":
            try:
                data['Store cookie?'] = api.check_cookie(site)
            except WebcredError as e:
                data['Store cookie?'] = e.message
            except:
                data['Store cookie?'] = '+++'
        if str(request.args.get('langcount', None))=="true":
            try:
                data['langcount'] = api.check_language(site)
            except WebcredError as e:
                data['langcount'] = e.message
            except:
                data['langcount'] = '+++'
        if str(request.args.get('misspelled', None))=="true":
            try:
                data['misspelled'], data['total_tags'] = api.spell_checker(site)
            except WebcredError as e:
                data['misspelled'] = e.message
            except:
                data['misspelled'] = '+++'
        if str(request.args.get('wot', None))=="true":
            try:
                data['wot'] = api.check_wot(site)
            except WebcredError as e:
                data['wot'] = e.message
            except:
                data['wot'] = '+++'
        if str(request.args.get('responsive'))=="true":
            try:
                data['responsive'] = api.check_responsive_check(site)
            except WebcredError as e:
                data['responsive'] = e.message
            except:
                data['responsive'] = '+++'
        if str(request.args.get('ads', None))=="true":
            try:
                data['ads'] = api.check_ads(site)
            except WebcredError as e:
                data['ads'] = e.message
            except:
                data['ads'] = '+++'
        if str(request.args.get('pageloadtime', None))=="true":
            try:
                data['pageloadtime'] = api.pageloadtime(site)
            except WebcredError as e:
                data['pageloadtime'] = e.message
            except:
                data['pageloadtime'] = '+++'

    except WebcredError as e:
        data =  WebcredError(e.message).message

    # pdb.set_trace()
    return jsonify(data)

def debug_start(request):

    data = {}
    site = str(request['args'].get('site', None))

    #  object
    try:
        site = Urlattributes(url=site)
    except WebcredError as e:
        print WebcredError(e.message).message

    data['url'] = site.geturl()

    # pdb.set_trace()
    if str(request['args'].get('lastmod', None))=="true":
    	try:
    		data['lastmod'] = api.getDate(site)
    	except WebcredError as e:
    		data['lastmod'] = e.message
    	except:
    		data['lastmod'] = '+++'
    if str(request['args'].get('domain', None))=="true":
        try:
            data['domain'] = api.getDomain(site)
        except WebcredError as e:
            data['domain'] = e.message
        except:
            data['domain'] = '+++'
    if str(request['args'].get('inlinks', None))=="true":
        try:
        	data['inlinks'] = api.getInLinks(site)
        except WebcredError as e:
            data['inlinks'] = str(e.message)
        except:
            data['inlinks'] = '+++'
    if str(request['args'].get('outlinks', None))=="true":
        try:
        	data['outlinks'] = api.getOutLinks(site)
        except WebcredError as e:
            data['outlinks'] = str(e.message)
        except:
            data['outlinks'] = '+++'
    if str(request['args'].get('hyperlinks', None))=="true":
        attributes = ['contact', 'email', 'help', 'recommend', 'sitemap']
    	try:
        	data['hyperlinks'] = api.check_hyperlinks(site, attributes)
        except WebcredError as e:
            data['hyperlinks'] = e.message
        except:
            data['hyperlinks'] = '+++'
    if str(request['args'].get('imgratio', None))=="true":
    	try:
        	data['imgratio'] = api.check_size_ratio(site)
        except WebcredError as e:
            data['imgratio'] = e.message
        except:
            data['imgratio'] = '+++'
    if str(request['args'].get('brokencount', None))=="true":
        try:
            data['brokencount'] = api.getBrokenLinks(site)
        except WebcredError as e:
            data['brokencount'] = e.message
        except:
            data['brokencount'] = '+++'
    if str(request['args'].get('cookie', None))=="true":
        try:
            data['cookie'] = api.check_cookie(site)
        except WebcredError as e:
            data['cookie'] = e.message
        except:
            data['cookie'] = '+++'
    if str(request['args'].get('langcount', None))=="true":
        try:
            data['langcount'] = api.check_language(site)
        except WebcredError as e:
            data['langcount'] = e.message
        except:
            data['langcount'] = '+++'
    if str(request['args'].get('misspelled', None))=="true":
        try:
            data['misspelled'], data['total_tags'] = api.spell_checker(site)
        except WebcredError as e:
            data['misspelled'] = e.message
        except:
            data['misspelled'] = '+++'
    if str(request['args'].get('wot', None))=="true":
        try:
            data['wot'] = api.check_wot(site)
        except WebcredError as e:
            data['wot'] = e.message
        except:
            data['wot'] = '+++'
    if str(request['args'].get('responsive'))=="true":
        try:
            data['responsive'] = api.check_responsive_check(site)
        except WebcredError as e:
            data['responsive'] = e.message
        except:
            data['responsive'] = '+++'
    if str(request['args'].get('ads', None))=="true":
        try:
            data['ads'] = api.check_ads(site)
        except WebcredError as e:
            data['ads'] = e.message
        except:
            data['ads'] = '+++'
    if str(request['args'].get('pageloadtime', None))=="true":
        try:
            data['pageloadtime'] = api.pageloadtime(site)
        except WebcredError as e:
            data['pageloadtime'] = e.message
        except:
            data['pageloadtime'] = '+++'

    print data
    return data

@app.route("/")
def index():
    print 'index'
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

    # data = {'lastmod': 'true', 'domain': 'true', 'inlinks': 'true',
    #  'outlinks': 'true', 'hyperlinks': 'true', 'imgratio': 'true',
    #  'brokencount': 'true', 'cookie': 'true', 'langcount': 'true',
    #  'misspelled': 'true', 'responsive': 'true', 'wot': 'true',
    #  'pageloadtime': 'true','ads': 'true',
    #  'site': 'https://threatpost.com/'}
    #
    # request = UserDict.UserDict(args=data)
    #
    # debug_start(request)
    # pdb.set_trace()
    # print result
