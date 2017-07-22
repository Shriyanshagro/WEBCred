import re
import json
import os
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import wordnet
from ast import literal_eval
from datetime import datetime
from utils import WebcredError
from utils import Urlattributes
from utils import PatternMatching
import pdb

def getWot(url):

    result = ("http://api.mywot.com/0.4/public_link_json2?hosts=" +
    url.geturl() + "/&callback=&key=d60fa334759ae377ceb9cd679dfa22aec57ed998")
    try:
        # pdb.set_trace()
        uri = Urlattributes(result)
        raw = uri.gettext()
        result = literal_eval(raw[1:-2])
        return list(result.values())[0]['0']
    except WebcredError as e:
        raise WebcredError(e.message)
    except:
        return 'NA'

def getResponsive(url):
    result = ("http://tools.mercenie.com/responsive-check/api/?format=json&url="
    + url.geturl())
    try:
        # pdb.set_trace()
        uri = Urlattributes(result)
        result = literal_eval(uri.gettext())
        return result['responsive']
    except WebcredError as e:
        raise WebcredError(e.message)
    except:
        return 'Info not NA'

def getHyperlinks(url, attributes):

    try:
        soup = url.getsoup()
    except WebcredError as e:
        raise WebcredError(e.message)
    except:
        raise WebcredError('Error while parsing Page')

    data = {}
    for element in attributes:
        data[element] = 0
        if soup.find_all('a', string=re.compile(element, re.I), href=True):
            data[element] = 1
    return data

def getLangcount(url):
    '''
    idea is to find pattern 'lang' in tags and then iso_lang code in those tags
    there are 2 possible patterns, to match iso_lang -
        ="en"
        =en
    '''

    try:
        soup  = url.getsoup()
    except WebcredError as e:
        raise WebcredError(e.message)

    count = 0
    matched = []
    tags = soup.find_all(href=True)

    for tag in tags:

        tag = str(tag)
        match = re.search("lang", tag, re.I)

        if match:
            # FIXME check for reg =**
            pattern = url.patternMatching.getIsoPattern()
            try:
                match, pattern = url.patternMatching.regexMatch(pattern, tag)
            except WebcredError as e:
                raise WebcredError(e.message)
            if match:
                if pattern not in matched:
                    matched.append(pattern)
                    count +=1
                    # pdb.set_trace()

    # some uni-lang websites didn't mention lang tags
    if count==0:
        count = 1
    return count

def getImgratio(url):

    total_img_size = int(0)
    txt_size = int(0)

    try:
        header = url.getheader()
    except WebcredError as e:
        raise WebcredError(e.message)

    if header.get('Content-Length', None):
        txt_size = int(header.get('Content-Length'))
    else:
        raise WebcredError('Content-Length in headers is NA')

    try:
        soup = url.getsoup()
    except WebcredError as e:
        raise WebcredError(e.message)

    # total_img_size of images
    for link in soup.find_all('img', src=True):
        uri = link.get('src')
        if not uri.startswith('http://') and not uri.startswith('https://'):
            uri = url.geturl() + uri

        try:
            uri = Urlattributes(uri)
            header = uri.getheader()
        except:
            # WebcredError as e:
            # raise WebcredError(e.message)
            continue

        if header.get('Content-Length', None):
            size = int(header.get('Content-Length'))
        else:
            size = 0
        total_img_size += size
        # print total_img_size

    try:
    	ratio = txt_size/float(total_img_size+txt_size)
    except ValueError:
        raise WebcredError('Error in fetching images')

    return ratio

def getAds(url):
    try:
        soup  = url.getsoup()
    except webcredError as e:
        raise webcredError(e.message)

    count = 0

    for link in soup.find_all('a', href=True):
        href = str(link.get('href'))
        if  href.startswith('http://') or href.startswith('https://'):

            # pdb.set_trace()
            try:
                pattern = url.getPatternObj().getAdsPattern()
                match, pattern = url.getPatternObj().regexMatch(pattern, href)
            except webcredError as e:
                raise webcredError(e.message)
            if match:
                count += 1
                # print pattern, href

    return count

def getCookie(url):
    try:
    	header = url.getheader()
    except WebcredError as e:
        raise WebcredError(e.message)

    try:
        pattern = url.getPatternObj().regexCompile(['cookie'])
    except WebcredError as e:
        raise WebcredError(e.message)
    for key in header.keys():
        try:
            match, matched = url.getPatternObj().regexMatch(pattern=pattern, data=key)
        except WebcredError as e:
            # pdb.set_trace()
            raise WebcredError(e.message)

        if match:
            # print key
            return 'Yes'

    return 'No'

def getMisspelled(url):
    # pdb.set_trace()
    try:
    	text  = url.gettext()
    except webcredError as e:
    	raise webcredError(e.message)

    excluded_tags = ['NNP', 'NNPS', 'SYM', 'CD', 'IN', 'TO', 'CC','LS','POS',
    '(',')',':','EX','FW','RP']

    text = word_tokenize(text)
    tags = []
    # print text
    for texts in text:
        i = pos_tag(texts.split())
        i =  i[0]
        if i[1] not in excluded_tags and i[0]!=i[1]:
            tags.append(i[0])

    # pdb.set_trace()
    total_tags = len(tags)
    # count of undefined words
    count = 0
    for tag in tags:
        syns = wordnet.synsets(tag)
        try:
            if syns:
                defi = syns[0].definition()
                # print defi
        except:
            count+= 1

    # pdb.set_trace()
    return count

def getDate(url):
    # pdb.set_trace()
    try:
        resp = url.geturllibreq()
    except WebcredError as e:
        raise WebcredError(e.message)
    # pdb.set_trace()
    if resp.code/100<4:
    	try:
            lastmod=str(resp.info().getdate('last-modified'))
            if lastmod == 'None' :
                # some page has key 'date' for same
        		lastmod=str(resp.info().getdate('date'))
            lastmod = datetime.strptime(str(lastmod), '(%Y, %m, %d, %H, %M, %S, %f, %W, %U)')
        except:
            raise WebcredError('Error with Requests')
    else:
    	try:
            # fetching data form archive
            uri = "http://archive.org/wayback/available?url=" + url.geturl()
            uri = Urlattributes(uri)
            resp = uri.geturllibreq()
            data = (json.load(resp)['archived_snapshots']['closest']
                    ['timestamp'])
            lastmod= ('wr'+ '('+ data[0:4]+ ', '+ data[4:6]+ ', '+ data[6:8]+
            ', '+ data[8:10]+ ', '+ data[10:12]+ ', '+ data[12:14]+')')
    	except WebcredError as e:
    		raise WebcredError(e.message)
    	except:
    		raise WebcredError('Error in fetching last-modified date from archive')
    return lastmod

def getDomain(url):
    # a fascinating use of .format() syntax
    try:
        domain = url.getdomain()
    except:
        raise WebcredError('urlparsing error')
    return domain

def getBrokenlinks(url):
    broken_links = 0

    try:
        soup = url.getsoup()
    except WebcredError as e:
        raise WebcredError(e.message)
    except:
        raise WebcredError('Url is broken')

    for link in soup.find_all('a', href=True):
        uri = link.get('href')

        # TODO should it inlude inner links as well?
        if uri.startswith('http://') or uri.startswith('https://'):
            # uri = url.geturl() + uri
            try:
                uri = Urlattributes(uri)
                resp = uri.geturllibreq()
                if not resp.code/100<4:
                    broken_links += 1
                    # print uri.geturl()
            except:
                # print uri.geturl()
                broken_links += 1

    return broken_links

def getOutlinks(url):
    outlinks = 0

    try:
        soup = url.getsoup()
    except WebcredError as e:
        raise WebcredError(e.message)
    except:
        raise WebcredError('Url is broken')

    for link in soup.find_all('a', href=True):
        uri = link.get('href')
        if uri.startswith('https://') or uri.startswith('http://'):
            try:
                uri = Urlattributes(uri)
                if url.getdomain() != uri.getdomain():
                	outlinks += 1
            except WebcredError as e:
                pass
                # raise WebcredError(e.message)

    return outlinks

# total web-pages which redirect/mention url
def getInlinks(url):

    API_KEY='AIzaSyB5L_ZZZKg9OeOVLQpmfOiqaHZMg8r9FCc'
    try:
        uri = ('https://www.googleapis.com/customsearch/v1?key='+
        API_KEY+ '&cx=017576662512468239146:omuauf_lfve&q=link:'+
        url.geturl())
        uri = Urlattributes(uri)
        txt = uri.gettext()
        # except WebcredError as e:
        # 	raise WebcredError(e.message)
    except:
    	raise WebcredError('GoogleApi limit is exceeded')

    # txt=unicodedata.normalize('NFKD', txt).encode('ascii','ignore')

    for line in txt.splitlines():
    	if "totalResults" in line:
    		break
    try:
    	inlinks=int(re.sub("[^0-9]", "", line))
    except:
    	raise WebcredError('Inlinks are hard to get for this URL')

    return inlinks

'''install phantomjs and have yslow.js in the path to execute'''
def getPageloadtime(url):
    # pdb.set_trace()
    try:
        response=os.popen('phantomjs yslow.js --info basic '+ url.geturl()).read()
        response=json.loads(response.split('\n')[1])
        return (int)(response['lt'])/((int)(response['r']))
    except ValueError:
        raise webcredError('FAIL to load')
    except:
        raise webcredError('Fatal error')
