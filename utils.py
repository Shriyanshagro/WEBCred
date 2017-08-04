import urllib2
from urlparse import urlparse
from bs4 import BeautifulSoup, SoupStrainer
import pdb
import validators
import re
import threading
import json
import time
import statistics

global patternMatching
patternMatching = None

# A class to catch error and exceptions
class WebcredError(Exception):
    """An error happened during assessment of site.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

# A class for pattern matching using re lib
class PatternMatching(object):

    def __init__(self, lang_iso=None, ads_list=None):
        if lang_iso:
            try:
                iso = open(lang_iso, "r")
                self.isoList = iso.read().split()
                self.isoPattern = self.regexCompile(self.isoList)
                iso.close()
            except WebcredError as e:
                raise WebcredError(e.message)
            except:
                raise WebcredError('Unable to open {} file'.format(lang_iso))
        else:
            raise WebcredError('Provide Language iso file')

        if ads_list:
            try:
                ads = open(ads_list, "r")
                self.adsList = ads.read().split()
                self.adsPattern = self.regexCompile(self.adsList)
                ads.close()
                print 'successfull with ads compilation'
            except WebcredError as e:
                raise WebcredError(e.message)
            except:
                raise WebcredError('Unable to open {} file'.format(ads_list))
        else:
            raise WebcredError('Provide a good ads list')

    def getIsoList(self):
        return self.isoList

    def getAdsList(self):
        return self.adsList

    def getAdsPattern(self):
        return self.adsPattern

    def getIsoPattern(self):
        return self.isoPattern

    def regexCompile(self, data=None):
        if not data:
            raise WebcredError('Provide data to compile')

        pattern = []
        for element in data:
            temp = re.compile(re.escape(element), re.X)
            pattern.append(temp)
        # pdb.set_trace()
        return pattern

    def regexMatch(self, pattern=None, data=None):

        if not pattern:
            raise WebcredError('Provide regex pattern')

        if not data:
            raise WebcredError('Provide data to match with pattern')

        for element in pattern:
            match = element.search(data)
            if match:
                break

        if match:
            return True, element.pattern
        else:
            return False, None

# A class to use extract url attributes
class Urlattributes(object):
    try:
        # pdb.set_trace()
        # TODO fetch ads list dynamically from org
        if not patternMatching:
            patternMatching = PatternMatching(lang_iso='lang_iso.txt', ads_list='ads.txt' )
            print 'end patternMatching'
    except WebcredError as e:
        raise WebcredError(e.message)

    def __init__(self, url=None):
        # print 'here'
        # pdb.set_trace()
        if patternMatching:
            self.patternMatching = patternMatching

        self.hdr = {'User-Agent': 'Mozilla/5.0'}
        self.requests = self.urllibreq = self.soup = self.text = None
        self.netloc = self.header = self.size= self.domain = None
        self.lock = threading.Lock()
        if url:
            if not validators.url(url):
                raise WebcredError('Provide a valid url')
            self.url = str(url)
            # case of redirections
            resp =self.getrequests()
            self.url = str(resp.geturl())
            self.getsoup()
            # if url!= self.url:
            #     print 'redirected', url,' >> ', self.url
        else:
            raise WebcredError('Provide a url')

    def geturl(self):
        return self.url

    def gethdr(self):
        return self.hdr

    def getheader(self):
        if not self.header:
            self.header =  dict(self.geturllibreq().info())

        return self.header

    def getrequests(self):
        if not self.requests:
            try:
                self.requests =  self.geturllibreq()
            except WebcredError as e:
                raise WebcredError(e.message)
            # requestss.get(self.url, headers=self.hdr)

        return self.requests

    def geturllibreq(self):
        # pdb.set_trace()
        # with self.lock:
        if not self.urllibreq:
            try:
                # binding the request
                # print self.url
                req = urllib2.Request(self.url)
                key = self.gethdr().keys()[0]
                val = self.gethdr()[key]
                req.add_header(key, val)
                self.urllibreq = urllib2.urlopen(req)
            except:
                raise WebcredError('Error in binding req to urllib2')

        # print self.urllibreq.geturl()
        return self.urllibreq

    def gettext(self):
        if not self.text:
            try:
                # pdb.set_trace()
                self.text = self.getrequests().read()
            except WebcredError as e:
                raise WebcredError(e.message)

            # try:
            #     self.text = self.text.decode(url.getheader(
            #     ).get('content-type').split(';')[1].split('=')[1])
            # except:
            #     self.text = self.text.decode('UTF-8')
        return self.text

    def getsoup(self):
        # pdb.set_trace()
        if not self.soup:
            data = self.gettext()
            try:
                self.soup = BeautifulSoup(data, "html.parser")
            except:
                raise WebcredError('Error while parsing using bs4')

        return self.soup

    def getnetloc(self):
        if not self.netloc:
            try:
                parsed_uri = urlparse(self.geturl())
                self.netloc = '{uri.netloc}'.format(uri=parsed_uri)
            except:
                raise WebcredError('Error while fetching attributes from parsed_uri')

        return self.netloc

    def getdomain(self):
        if not self.domain:
            try:
                netloc = self.getnetloc()
                self.domain = netloc.split('.')[-1]
            except:
                raise WebcredError('provided {} not valid'.format(netloc))

        return self.domain

    def getPatternObj(self):
        try:
            return self.patternMatching
        except:
            raise WebcredError('Pattern Obj is NA')

        # self.isoList =

    def getsize(self):
        if not self.size:
            # pdb.set_  trace()
            t = self.gettext()
            try:
                self.size = len(t)
            except WebcredError as e:
                raise WebcredError(e.message)
            except:
                pdb.set_trace()
                raise WebcredError('error in retrieving length')
        return self.size

class MyThread(threading.Thread):

    def __init__(self, Module='api', Method=None, Name=None, Url=None, Args=None):

        threading.Thread.__init__(self)

        if Method and Module=='api':
            self.func = getattr(api, Method)
        elif Method and Module=='app':
            self.func = getattr(app, Method)
        else:
            raise WebcredError('Provide method')

        if Name:
            self.name = Name
        else:
            raise WebcredError('Provide name')

        if Url:
            self.url = Url
        else:
            raise WebcredError('Provide url')

        if Args and Args!= '':
            self.args = Args
        else:
            self.args = None

        # pdb.set_trace()

    def run(self):

        try:
            # print 'Fetching {}'.format(self.name)
            if self.args:
                self.result = self.func(self.url, self.args)
            else:
                # pdb.set_trace()
                self.result = self.func(self.url)
            # print 'Got {}'.format(self.name)
        except WebcredError as e:
            self.result = e.message
        except:
            self.result = '+++'

    def getResult(self):
        return self.result

class Captcha(object):

    def __init__(self, resp=None, ip=None):
        google_api = 'https://www.google.com/recaptcha/api/siteverify'
        self.url = google_api
        self.key = '6LcsiCoUAAAAAL9TssWVBE0DBwA7pXPNklXU42Rk'
        self.resp = resp
        self.ip = ip
        self.params = {'secret': self.key, 'response': self.resp,
        'remoteip': self.ip }

    def check(self):
        result = requests.post(url=self.url, params=self.params).text
        result = json.loads(result)
        return result.get('success', None)

class Webcred(object):

    def assess(self, request):
            if not isinstance(request, dict):
                # pdb.set_trace()
                request = dict(request.args)
            try:
                data = {}
                req = {}
                req['args'] = {}
                hyperlinks_attributes = ['contact', 'email', 'help',
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

                for keys in apiList.keys():
                    # because request.args is of ImmutableMultiDict form
                    if request.get(keys, None):
                        req['args'][keys] = request.get(keys)

                data['url'] =  req['args']['site']
                site = Urlattributes(url=req['args'].get('site', None))

                if data['url'] != site.geturl():
                    data['redirected'] = site.geturl()

                # site is not a WEBCred parameter
                del req['args']['site']
                threads = []

                for keys in req['args'].keys():
                    if str(req['args'].get(keys, None))=="true":
                            thread = MyThread(Method=apiList[keys][0], Name=keys, Url=site,
                            Args=apiList[keys][1])
                            thread.start()
                            threads.append(thread)

                for t in threads:
                    try:
                        t.join()
                        data[t.getName()] = t.getResult()
                    except WebcredError as e:
                        data[t.getName()] = e.message
                    except:
                        data[t.getName()] = 'Fatal Error'

            except WebcredError as e:
                data['Error'] =  e.message
            except:
                data['Error'] = 'Fatal error'
            return data

class Normalize(object):

    # data = json_List
    # name =parameter to score
    def __init__(self, data=None, name=None):
        if not data or not name:
            raise WebcredError('Need 3 args, 2 pass')

        self.data = data
        self.name = name

        self.dataList = self.mean = self.deviation = None

    def getdatalist(self):
        if not self.dataList:
            dataList = []
            for element in self.data:
                if not isinstance(element[self.name], str):
                    dataList.append(element[self.name])
            self.dataList = dataList

        return self.dataList

    def normalize(self):
        for index in range(len(self.data)):
            self.data[index][self.name] = self.getscore(self.data[index][self.name])

        return self.data

    def getdata(self):
        return self.data

    def getmean(self):
        if not self.mean:
            mean =statistics.mean(self.getdatalist())
        return mean

    def getdeviation(self):
        if not self.deviation:
            deviation =statistics.pstdev(self.getdatalist())
        return deviation

    def getscore(self, value):
        mean = self.getmean()
        deviation = self.getdeviation()

        if isinstance(value, str):
            return 0

        if value<(mean-deviation):
            return -1

        else :
            if value>(mean+deviation):
                return 1
            return 0



import api
import app
