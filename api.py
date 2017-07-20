import sys
import extraction
import requests
import urllib2
from urllib import urlopen
from urlparse import urlparse
import socket
import utils
import re
import json
from bs4 import BeautifulSoup, SoupStrainer
import unicodedata
import re
import os
from nltk.tokenize import word_tokenize
import nltk
from nltk.tag import pos_tag
from nltk.corpus import wordnet
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from ast import literal_eval
from datetime import datetime
from classes import webcredError
from classes import urlattributes
import pdb

global i, urls, check_hyperlink, check_ratio, check_link_ads, broken_links
global cookie, language, spell_check, ads_list_flag, ads_list, iso_lang_flag
global iso_array

i = 0
ads_list = []
iso_lang_flag = 0
ads_list_flag = 0

def check_wot(url):
    result = ("http://api.mywot.com/0.4/public_link_json2?hosts=" + url +
    "/&callback=&key=d60fa334759ae377ceb9cd679dfa22aec57ed998")
    hdr = {'User-Agent': 'Mozilla/5.0'}
    try:
        raw = requests.get(result, headers=hdr)
        result = literal_eval(raw.text[1:-2])
    except:
        return 'NA'
    return list(result.values())[0]['0']

def check_responsive_check(url):
    result = "http://tools.mercenie.com/responsive-check/api/?format=json&url="
    +url
    hdr = {'User-Agent': 'Mozilla/5.0'}
    try:
        raw = requests.get(result, headers=hdr)
        result = literal_eval(raw.text)
    except:
        return 'NA'
    return result['responsive']

def check_hyperlinks(url, attributes):

    try:
        soup = url.soup()
    except webcredError as e:
        raise webcredError(e.message)
    except:
        raise webcredError('Error while parsing Page')

    data = {}
    for element in attributes:
        data[element] = 0
        if soup.find_all('a', string=re.compile(element, re.I), href=True):
            data[element] = 1
    return data

def check_language(url):
    # idea is to find patter 'lang' in tags and then iso_lang code in those tags
    # there are two possible patterns, to match iso_lang -
    #     ="en"
    #     =en
    global iso_lang_flag,iso_array
    if iso_lang_flag==0:
        # print "scanning array"
        iso = open("lang_iso.txt", "r")
        iso_array = iso.read().split()
        iso.close()
        iso_lang_flag=1

    count = {"Total supported Lang":"Page NA"}
    # need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
    try:
        raw  = requests.get(url,headers=hdr)
    except:
        # print "cannot extract raw of",url
        return count

    count = 0
    done = {}
    data = raw.text
    soup = BeautifulSoup(data,"html.parser")
    tags = soup.find_all(href=True)
    for tag in tags:
        tag = str(tag)
        match = re.search("lang",tag,re.I)
        # tag = tag.split("=")
        if match:
            # print tag
            # tag = word_tokenize(tag)
            for code in  iso_array:
            # return {"Total supported Lang":"Page NA"}
                    code = str(code)
                    # print code,
                # compile iso-code of languages
                    # break
                    reg = '='+code
                    pattern = re.compile(reg)
                    # # look for match in the string
                    match= pattern.search(tag)

                    if not match:

                        reg = '='+ '"' + code + '"'
                        pattern = re.compile(reg)
                        # # look for match in the string
                        match= pattern.search(tag)
                    # # print match
                    # # match = re.search("en",tag)
                    if match:
                        if not code in done.keys():
                            # print code
                            done[code]=1
                            count +=1
                            # print code

    # some uni-lang websites didn't mention lang tags
    if count==0:
        count = 1
    count = {"Total supported Lang":count}
    return count

def check_size_ratio(url):

    '''need to specify header for scrapping otherwise some websites doesn't
    allow bot to scrap'''
    hdr = {'User-Agent': 'Mozilla/5.0'}

    try:
        raw  = url.requests()
        soup = url.soup()
    except webcredError as e:
        raise webcredError(e.message)
    except:
        raise webcredError('Error while Requests Page')

    total_img_size = int(0)
    txt_size = int(0)

    if raw.headers.get('Content-Length', None):
        txt_size = int(raw.headers.get('Content-Length'))
    else:
        raise webcredError('Content-Length in headers is not available')

    # total_img_size of images
    for link in soup.find_all('img', src=True):
        links = link.get('src')
        if links!="":
            if not links.startswith('http://') and not links.startswith('https://'):
                # pdb.set_trace()
                links = url.geturl()+links

            try:
                '''You should use the HEAD Request for this, it asks the
                webserver for the headers without the body.'''
                r  = requests.head(links, headers=hdr)
                size = r.headers['Content-Length']
            except:
                # raise webcredError('Error while Requesting Page attributes')
            	size=0
            finally:
            	total_img_size += int(size)
                print total_img_size

    # pdb.set_trace()
    try:
    	ratio = txt_size/float(total_img_size+txt_size)
    except ValueError:
        raise webcredError('Error in fetching images')

    return ratio

# compiling all regular expressions of ads
def compile_ads():
	global ads_list_flag,ads_list
	if ads_list_flag==1:
		return
	print "compiling ads regex"
	easylist = open("easylist.txt", "r")
	ads_list_raw = easylist.read().split()
	'''
		[Adblock Plus 2.0]
		! Version: 201702151753
		! Title: EasyList
		! Last modified: 15 Feb 2017 17:53 UTC
		! Expires: 4 days (update frequency)
		! Homepage: https://easylist.to/
		! Licence: https://easylist.to/pages/licence.html
		!
		! Please report any unblocked adverts or problems
		! in the forums (https://forums.lanik.us/)
		! or via e-mail (easylist.subscription@gmail.com).
		! GitHub issues: https://github.com/easylist/easylist/issues
		! GitHub pull requests: https://github.com/easylist/easylist/pulls
		!
		! -----------------------General advert blocking filters-----------------------!
		! *** easylist:easylist/easylist_general_block.txt ***
	'''
	easylist.close()
	for ads in ads_list_raw:
		# use of re.escape so that if your text has special characters(#,?,/,\,.), they won't be interpreted as such.
		ads = re.compile(re.escape(ads),re.X)
		ads_list.append(ads)
	ads_list_flag=1
	return

def check_ads(url):
	# get compiled list of ads regex
	compile_ads()
	# print ads_list

	count = {"ad count":"Page NA"}
	hdr = {'User-Agent': 'Mozilla/5.0'}
	try:
		raw  = requests.get(url,headers=hdr)
	except:
		# print "cannot extract raw of",url
		return count

	data = raw.text
	soup = BeautifulSoup(data,'html.parser')
	count = 0

	for link in soup.find_all('a',href=True):
		# print link
		href = link.get('href')
		if  href.startswith('http://') or href.startswith('https://'):
			# print href
			try:
				href = str(href)
			except:
				return {"ad count":"Page NA"}


			for ads in ads_list:
				# ads = str(ads)
				# print ads
				match = ads.search(href)
				# print ads
				if match:
					# print href
					count += 1
					break


	# if count!=0:
	#	 print 'ad count=',count,url
	count = {"ad count":count}
	return count

def check_brokenlinks(url):
	array = {'total_links':"Page NA",'total_external_links':"Page NA",'broken_links':"Page NA"}
	# need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
	hdr = {'User-Agent': 'Mozilla/5.0'}
	# You should use the HEAD Request for this, it asks the webserver for the headers without the body.
	try:
		raw  = requests.get(url,headers=hdr)
	except:
		# print "cannot extract raw of",url
		return array

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
					# print "cannot extract raw of",url
					return {'total_links':"Page NA",'total_external_links':"Page NA",'broken_links':"Page NA"}
				raw  = ((str(raw).split(' ')[1]).split(']')[0])
				raw = int(raw.split('[')[1])
				# print  raw
				if raw>300:
					#  success response code are only b/w 200-300
					count +=1

	array = {'total_links':total_links,'total_external_links':total_external_links,'broken_links':broken_links}
	return  array

def check_cookie(url):

	hdr = {'User-Agent': 'Mozilla/5.0'}
	# You should use the HEAD Request for this, it asks the webserver for the headers without the body.
	try:
		raw  = requests.head(url,headers=hdr)
	except:
		# print "cannot extract raw of",url
		return {'cookies':"Page NA"}
	cookies = raw.cookies
	# print cookies
	if cookies:
		# print 'yes website installs cookie on client system'
		return {'cookies':1}
	else:
		return {'cookies':0}

def spell_checker(url):
	array ={"Misspelled words":"Page NA","total words":"Page NA"}
	hdr = {'User-Agent': 'Mozilla/5.0'}
	# You should use the HEAD Request for this, it asks the webserver for the headers without the body.
	try:
		raw  = requests.get(url,headers=hdr)
	except:
		# print "cannot extract raw of",url
		return array

	# give text with html tags
	text = raw.text
	# gives only  text of HTML, i.e removes all HTML tags
	text = BeautifulSoup(text,"html.parser")
	text = text.get_text()
	# print raw,text
	excluded_tags = ['NNP', 'NNPS', 'SYM', 'CD', 'IN', 'TO', 'CC','LS','POS','(',')',':','EX','FW','RP']
	# text  = re.split(' {?}| ?:[ -]|\,|\.* |\\n|!|\?|\)|-|\(|!|;|\[|\]|\"|',text)
	text = word_tokenize(text)
	tags = []
	# print text
	for texts in text:
		i = pos_tag(texts.split())
		i =  i[0]
		if i[1] not in excluded_tags and i[0]!=i[1]:
			tags.append(i[0])
			# print i
	# tags = [i[0] for i in pos_tag(text.split()) if i[1] not in excluded_tags]

	total_tags = len(tags)
	# count of undefined words
	count = 0
	for tag in tags:
		flag =1
		# print tag
		syns = wordnet.synsets(tag)
		try:
			defi = syns[0].definition()
			# print tag,"=",defi
		except:
			# print tag,"naa ho paayega"
			flag = 0

		if flag ==0:
			count+= 1
			# print tag

	# print count
	array ={"Misspelled words":count,"total words":total_tags}
	# print array,len(text)
	return array

def getDate(url):

    resp = url.urllibreq()
    if resp.code/100<4:
    	try:
            lastmod=str(resp.info().getdate('last-modified'))
            if lastmod == 'None' :
                # some page has key 'date' for same
        		lastmod=str(resp.info().getdate('date'))
            lastmod = datetime.strptime(str(lastmod), '(%Y, %m, %d, %H, %M, %S, %f, %W, %U)')
        except:
            raise webcredError('Error with Requests')
    else:
    	try:
            # fetching data form archive
            req = urllib2.Request("http://archive.org/wayback/available?url="+url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            response=urllib2.urlopen(req)
            data = (json.load(response)['archived_snapshots']['closest']
                    ['timestamp'])
            lastmod= ('wr'+ '('+ data[0:4]+ ', '+ data[4:6]+ ', '+ data[6:8]+
            ', '+ data[8:10]+ ', '+ data[10:12]+ ', '+ data[12:14]+')')
    	except:
    		raise webcredError('Error in fetching last-modified date from archive')
    return lastmod

def getDomain(url):
    # a fascinating use of .format() syntax
    try:
        parsed_uri = urlparse(url.geturl())
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    except:
        raise webcredError('urlparsing error')
    return domain

def getOutLinks(url):
    outlinks=[]

    try:
        soup = url.soup()
    except webcredError as e:
        raise webcredError(e.message)
    except:
        raise webcredError('Url is broken')


    for link in soup.find_all('a', href=True):
    	outlinks.append(link['href'])

    outlinks = len(outlinks)
    return outlinks

def getInLinks(url):

    hdr = {'User-Agent': 'Mozilla/5.0'}
    '''You should use the HEAD Request for this, it asks the webserver for the
    headers without the body.'''

    API_KEY='AIzaSyB5L_ZZZKg9OeOVLQpmfOiqaHZMg8r9FCc'
    try:
    	r = requests.get('https://www.googleapis.com/customsearch/v1?key='+
        API_KEY+ '&cx=017576662512468239146:omuauf_lfve&q=link:'+
        url, headers=hdr)
    except:
    	raise webcredError('GoogleApi limit is exceeded')

    txt=r.text
    txt=unicodedata.normalize('NFKD', txt).encode('ascii','ignore')

    for line in txt.splitlines():
    	if "totalResults" in line:
    		break
    try:
    	inlinks=int(re.sub("[^0-9]", "", line))
    except:
    	raise webcredError('Inlinks are hard to get for this URL')

    return inlinks

'''install phantomjs and have yslow.js in the path to execute'''
def pageloadtime(url):
	response=os.popen('phantomjs yslow.js --info basic '+url).read()
	response=json.loads(response.split('\n')[1])
	return (int)(response['lt'])/((int)(response['r']))
