from flask import Flask, abort, flash, redirect, render_template, request
from flask import url_for, jsonify, make_response
import validators
import api
from classes import webcredError
from classes import urlattributes
import json

# debugging imports
import UserDict
import pdb

app = Flask(__name__)
@app.route("/start",methods=['GET'])
def start():

    responsive=wot=site=lastmod=domain=inlinks=outlinks=plt=hyperlinks= None
    imgratio=ads=brokencount=cookie=langcount=misspelled=None
    site = str(request.args.get('site'))
    # site = api.urlattributes(site)

    if str(request.args.get('lastmod'))=="true":
    	try:
    		lastmod=api.getDate(site)
    		lastmod.replace(",",":")
    	except:
    		lastmod='+++'

    if str(request.args.get('domain'))=="true":
    	domain = api.getDomain(site)
    if str(request.args.get('inlinksoutlinks'))=="true":
    	inlinks, outlinks = api.getLinks(site)
    print inlinks,outlinks
    if str(request.args.get('pageloadtime'))=="true":
    	try:
    		plt=pageloadtime(site)
    	except:
    		plt='+++'
    if str(request.args.get('hyperlinks'))=="true":
    	hyperlinks=check_hyperlinks(site)
    if str(request.args.get('imgratio'))=="true":
    	imgratio = check_size_ratio(site)
    if str(request.args.get('ads'))=="true":
    	ads = check_ads(site)
    if str(request.args.get('brokencount'))=="true":
    	brokencount  = check_brokenlinks(site)
    if str(request.args.get('cookie'))=="true":
    	cookie=check_cookie(site)
    if str(request.args.get('langcount'))=="true":
    	langcount=check_language(site)
    if str(request.args.get('misspelled'))=="true":
    	misspelled=spell_checker(site)
    if str(request.args.get('wot'))=="true":
    	wot=check_wot(site)
    if str(request.args.get('responsive'))=="true":
    	responsive=check_responsive_check(site)
    dic={'site':site,'lastmod':lastmod,'domain':domain,'inlinks':inlinks,'outlinks':outlinks,
    'pageloadtime':plt,'hyperlinks':hyperlinks,'imgratio':imgratio,'ads':ads,'brokencount':brokencount,
    'cookie':cookie,'langcount':langcount,'misspelled':misspelled,"wot":wot,"responsive":responsive}
    return jsonify(dic)

# @app.route("/start",methods=['GET'])
def debug_start(request):

    responsive=wot=site=lastmod=domain=inlinks=outlinks=plt=hyperlinks = None
    imgratio=ads=brokencount=cookie=langcount=misspelled = None

    site = str(request['args'].get('site', None))

    if not validators.url(site):
        return jsonify(webcredError('Provide a good site url').message)

    #  object
    site = urlattributes(site)

    if str(request['args'].get('lastmod', None))=="true":
    	try:
    		lastmod = api.getDate(site)
    	except webcredError as e:
    		lastmod = e.message
    	except:
    		lastmod = '+++'
    if str(request['args'].get('domain', None))=="true":
        try:
            domain = api.getDomain(site)
        except webcredError as e:
            domain = e.message
        except:
            domain = '+++'
    if str(request['args'].get('inlinksoutlinks', None))=="true":
        try:
        	outlinks = api.getOutLinks(site)
        except webcredError as e:
            outlinks = str(e.message)
        except:
            outlinks = '+++'

        try:
        	inlinks = api.getInLinks(site)
        except webcredError as e:
            inlinks = str(e.message)
        except:
            inlinks = '+++'
    if str(request['args'].get('hyperlinks', None))=="true":
        attributes = ['contact', 'email', 'help', 'recommend', 'sitemap']
    	try:
        	hyperlinks = api.check_hyperlinks(site, attributes)
        except webcredError as e:
            hyperlinks = e.message
    if str(request['args'].get('imgratio', None))=="true":
    	try:
        	imgratio = api.check_size_ratio(site)
        except webcredError as e:
            imgratio = e.message
    pdb.set_trace()

    if str(request['args'].get('pageloadtime', None))=="true":
        try:
            plt=pageloadtime(site)
        except:
            plt='+++'
    if str(request['args'].get('ads', None))=="true":
    	ads = check_ads(site)
    if str(request['args'].get('brokencount', None))=="true":
    	brokencount  = check_brokenlinks(site)
    if str(request['args'].get('cookie', None))=="true":
    	cookie=check_cookie(site)
    if str(request['args'].get('langcount', None))=="true":
    	langcount=check_language(site)
    if str(request['args'].get('misspelled', None))=="true":
    	misspelled=spell_checker(site)
    if str(request['args'].get('wot', None))=="true":
    	wot=check_wot(site)
    if str(request.args.get('responsive'))=="true":
    	responsive=check_responsive_check(site)

    dic={'site': site, 'lastmod': lastmod, 'domain': domain,
        'inlinks': inlinks, 'outlinks': outlinks, 'pageloadtime': plt,
        'hyperlinks': hyperlinks, 'imgratio': imgratio, 'ads': ads,
        'brokencount': brokencount, 'cookie': cookie, 'langcount': langcount,
        'misspelled': misspelled, "wot": wot, "responsive": responsive}

    print dic
    return jsonify(dic)

@app.route("/")
def index():

	return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
	# app.run(host='0.0.0.0',debug=True)

    data = {'lastmod': 'false', 'domain': 'false', 'inlinksoutlinks': 'false',
            'plt': 'false', 'hyperlinks': 'false',
            'imgratio': 'true', 'ads': 'false', 'brokencount': 'false',
            'responsive': 'false', 'wot': 'false', 'site': 'false',
            'cookie': 'false', 'langcount': 'false', 'misspelled': 'false',
            'site': 'https://blogs.rsa.com/'}
    request = UserDict.UserDict(args=data)

    result = debug_start(request)
    pdb.set_trace()
    print result
