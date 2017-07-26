import requests
import urllib2
from urlparse import urlparse
from bs4 import BeautifulSoup, SoupStrainer
import pdb
from urlparse import urlparse
import validators
import re
import threading
import requests
import json

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

        if url:
            if not validators.url(url):
                raise WebcredError('Provide a valid url')
            self.url = str(url)
        else:
            raise WebcredError('Provide a url')

        if patternMatching:
            self.patternMatching = patternMatching

        self.hdr = {'User-Agent': 'Mozilla/5.0'}
        self.requests = self.urllibreq = self.soup = self.text = None
        self.domain = self.header = None

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
        if not self.urllibreq:
            try:
                # binding the request
                req = urllib2.Request(self.geturl())
                key = self.gethdr().keys()[0]
                val = self.gethdr()[key]
                req.add_header(key, val)
                self.urllibreq = urllib2.urlopen(req)
            except:
                raise WebcredError('Error in binding req to urllib2')

        return self.urllibreq

    def gettext(self):
        if not self.text:
            try:
                # pdb.set_trace()
                self.text = self.getrequests().read()
            except WebcredError as e:
                raise WebcredError(e.message)
            try:
                self.text = self.text.decode(url.getheader(
                ).get('content-type').split(';')[1].split('=')[1])
            except:
                self.text = self.text.decode('UTF-8')
        return self.text

    def getsoup(self):
        # pdb.set_trace()
        if not self.soup:
            try:
                data = self.gettext()
                # pdb.set_trace()
            except  WebcredError as e:
                raise WebcredError(e.message)
            try:
                self.soup = BeautifulSoup(data, "html.parser")
            except:
                raise WebcredError('Error while parsing using bs4')

        return self.soup

    def getdomain(self):
        if not self.domain:
            try:
                parsed_uri = urlparse(self.geturl())
                self.domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            except:
                raise WebcredError('Error while fetching attributes from parsed_uri')

        return self.domain

    def getPatternObj(self):
        try:
            return self.patternMatching
        except:
            raise WebcredError('Pattern Obj is NA')

        # self.isoList =


class MyThread(threading.Thread):

    def __init__(self, Method=None, Name=None, Url=None, Args=None):

        threading.Thread.__init__(self)

        if Method:
            self.func = getattr(api, Method)
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
            print 'Fetching {}'.format(self.name)
            if self.args:
                self.result = self.func(self.url, self.args)
            else:
                self.result = self.func(self.url)
            print 'Got {}'.format(self.name)
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
        pdb.set_trace()
        return result.get('success', None)

import api
# pdb.set_trace()
# url = 'https://blogs.rsa.com/'
#
# uri = Urlattributes(url='')
# header = uri.getheader()
