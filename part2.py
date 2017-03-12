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

def check_hyperlinks(url):
	# need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
	hdr = {'User-Agent': 'Mozilla/5.0'}
	# You should use the HEAD Request for this, it asks the webserver for the headers without the body.
	try:
		raw  = requests.get(url,headers=hdr)
	except:
		print "cannot extract raw of",url
		return

	data = raw.text
	soup = BeautifulSoup(data,"html.parser")

	data = {'contact':0,'email':0,'help':0,'recommend':0,'sitemap':0}
	for link in soup.find_all('a', string=re.compile("contact",re.I),href=True):
		links = link.get('href')
		if links:
			# print 'contact',
			data['contact']=1
			break

	for link in soup.find_all('a', string=re.compile("email",re.I),href=True):
		links = link.get('href')
		if links:
			# print 'email',
			data['email']=1
			break

	for link in soup.find_all('a', string=re.compile("help",re.I),href=True):
		links = link.get('href')
		if links:
			# print 'help',
			data['help']=1
			break

	for link in soup.find_all('a', string=re.compile("recommend",re.I),href=True):
		links = link.get('href')
		if links:
			# print 'recommend',
			data['recommend']=1
			break

	for link in soup.find_all('a', string=re.compile("sitemap",re.I),href=True):
		links = link.get('href')
		if links:
			# print 'sitemap',
			data['sitemap']=1
			break

	# print data,url
	return data

def check_size_ratio(url):
	# need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
	hdr = {'User-Agent': 'Mozilla/5.0'}
	# You should use the HEAD Request for this, it asks the webserver for the headers without the body.
	try:
		raw  = requests.get(url,headers=hdr)
	except:
		print "cannot extract raw of",url
		return

	ratio  = 'Not defined'
	total_img_size = int(0)
	txt_size = int(0)

	try:
		data = raw.text
		txt_size = int(raw.headers['Content-Length'])
	except:
		txt_size ='NA'
		print 'text size not available, page is dynamically created',
		return "NA"

	soup = BeautifulSoup(data,"html.parser")

	# total_img_size of images
	for link in soup.find_all('img',src=True):
		links = link.get('src')
		if links!="":
			if not links.startswith('http://') or links.startswith('https://'):
				links = url+links
				# print links

			hdr = {'User-Agent': 'Mozilla/5.0'}
			r  = requests.get(links,headers=hdr)
			try:
				size = r.headers['Content-Length']
			except:
				size=0
			finally:
				total_img_size += int(size)
			# print size,link

			try:
				ratio = total_img_size/txt_size
			except ValueError:
				ratio = 'Not defined'
	# print total_img_size,url,txt_size
	# print ratio
	return ratio
#
# def check_ads(url):
#	 # print ads for ads in ads_list
#	 # return
#	 hdr = {'User-Agent': 'Mozilla/5.0'}
#	 # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
#	 try:
#		 raw  = requests.head(url,headers=hdr)
#	 except:
#		 print "cannot extract raw of",url
#		 return
#	 data = raw.text
#	 soup = BeautifulSoup(data,'html.parser')
#	 count = 0
#
#	 for link in soup.find_all('a'):
#		 href = link.get('href')
#		 if  href.startswith('http://') or href.startswith('https://'):
#			 print href
#			 # for ads in ads_list:
#			 #	 print str(ads)
#			 x = re.findall(r"(?=("+'|'.join(ads_list)+r"))",href)
#			 if x:
#				 print x,len(x)
#				 # if re.match(ads,href):
#				 #	 print link
#				 #	 count += 1
#
#
#	 print 'ad count=',count,
#	 return count
#
def check_brokenlinks(url):
	# need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
	hdr = {'User-Agent': 'Mozilla/5.0'}
	# You should use the HEAD Request for this, it asks the webserver for the headers without the body.
	try:
		raw  = requests.get(url,headers=hdr)
	except:
		print "cannot extract raw of",url
		return

	data = raw.text
	soup = BeautifulSoup(data,'html.parser')
	count = 0
	total_links  = 0
	total_external_links=0

	for link in soup.find_all('a',href=True):
			href = link.get('href')
			total_links+=1
			if  href.startswith('http://') or href.startswith('https://'):
				total_external_links +=1
				# now only allowed for external links
				# header is mentioned because some robots don't allow bot to crawl their pages
				hdr = {'User-Agent': 'Mozilla/5.0'}
				# You should use the HEAD Request for this, it asks the webserver for the headers without the body.
				try:
					raw  = requests.head(url,headers=hdr)
				except:
					print "cannot extract raw of",url
					return
				raw  = ((str(raw).split(' ')[1]).split(']')[0])
				raw = int(raw.split('[')[1])
				# print  raw
				if raw>300:
					#  success response code are only b/w 200-300
					count +=1
	print  'total_links =',total_links,'total_external_links =',total_external_links,'broken_links =',count,
	return  count

def check_cookie(url):
	hdr = {'User-Agent': 'Mozilla/5.0'}
	# You should use the HEAD Request for this, it asks the webserver for the headers without the body.
	try:
		raw  = requests.head(url,headers=hdr)
	except:
		print "cannot extract raw of",url
		return
	cookies = raw.cookies
	print cookies
	if cookies:
		print 'yes website installs cookie on client system'
		return 1
	else:
		return 0

def getDate(url):
	print urllib2.urlopen(url).info().getdate('last-modified')
	if urllib2.urlopen(url).code/100<4:
		lastmod=str(urllib2.urlopen(url).info().getdate('last-modified'))
		if lastmod=='None':
			lastmod='cr'+str(urllib2.urlopen(url).info().getdate('date'))
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
	print inlinks,outlinks
	plt=pageloadtime(site)
	hyprlinks=check_hyperlinks(site)
	imgratio = check_size_ratio(site)
	ads = None #check_ads(site)
	brokencount  = check_brokenlinks(site)
	cookie=check_cookie(site)
	dic={'site':site,'lastmod':lastmod,'domain':domain,'inlinks':inlinks,'outlinks':outlinks,
	'pageloadtime':plt,'hyprlinks':hyprlinks,'imgratio':imgratio,'ads':ads,'brokencount':brokencount,
	'cookie':cookie}
	return jsonify(dic)

if __name__ == "__main__":
	app.run(debug=True)
