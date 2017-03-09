import sys
import extraction
import requests
from urllib import urlopen
import socket
from urlparse import urlparse
# from http import utils
import re
import urllib2
import json
from bs4 import BeautifulSoup, SoupStrainer
import unicodedata
import os
from flask import Flask, jsonify, make_response, request
app = Flask(__name__)



def getDate(url):
	print urlopen(url).code
	if urlopen(url).code/100<4:
		lastmod=str(urlopen(url).info().getdate('last-modified'))
		if lastmod=='None':
			lastmod='cr'+str(urlopen(url).info().getdate('date'))
	else:
		try:
			response=urllib2.urlopen("http://archive.org/wayback/available?url="+url)
			data = json.load(response)['archived_snapshots']['closest']['timestamp']
			lastmod='wr'+'('+data[0:4]+', '+data[4:6]+', '+data[6:8]+', '+data[8:10]+', '+data[10:12]+', '+data[12:14]+')'
		except:
			lastmod='NA'
	return lastmod

def getDomain(url):
	parsed_uri = urlparse(url)
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
	return domain

def getLinks(url):
	outlinks=[]
	html = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'}).text
	soup=BeautifulSoup(html)
	for link in soup.find_all('a', href=True):
		outlinks.append(link['href'])
	API_KEY='AIzaSyB5L_ZZZKg9OeOVLQpmfOiqaHZMg8r9FCc'
	r = requests.get('https://www.googleapis.com/customsearch/v1?key='+API_KEY+'&cx=017576662512468239146:omuauf_lfve&q=link:'+url,
                 headers={'User-Agent': 'Mozilla/5.0'}
                )
	txt=r.text
	txt=unicodedata.normalize('NFKD', txt).encode('ascii','ignore')
	for line in txt.splitlines():
		if "totalResults" in line:
			break

	inlinks=int(re.sub("[^0-9]", "", line))
	outlinks = len(outlinks)
	return inlinks,outlinks

'''install phantomjs and have yslow.js in the path to execute'''
def pageloadtime(url):
	response=os.popen('phantomjs yslow.js --info basic '+url).read()
	response=json.loads(response.split('\n')[1])
	return (int)(response['lt'])/((int)(response['r']))


@app.route("/start",methods=['GET'])
def start():
	site=str(request.args.get('site'))
	lastmod=getDate(site)
	domain=getDomain(site)
	inlinks, outlinks=getLinks(site)
	plt=pageloadtime(site)
	dic={'site':site,'lastmod':lastmod,'domain':domain,'inlinks':inlinks,'outlinks':outlinks,'pageloadtime':plt}
	return jsonify(dic)

if __name__ == "__main__":
	app.run(debug=True)
