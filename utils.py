import urllib2
from urlparse import urlparse
from bs4 import BeautifulSoup, SoupStrainer
import validators
import re
import threading
import json
import time
import statistics
import requests
import types
from datetime import datetime as dt
from pipeline import Pipeline

global patternMatching
patternMatching = None

# represents the normalized class of each dimension
# normalizedData[dimension_name].getscore(dimension_value) gives normalized_value
global normalizedData
normalizedData = None

global lastmodMaxMonths
lastmodMaxMonths = 93

# define rules to normalize data
global normalizeCategory
normalizeCategory = {
    '3':{
     'outlinks': 'reverse', 'inlinks': 'linear',
     'ads':'reverse',
     'brokenlinks': 'reverse', 'pageloadtime': 'reverse',
     'imgratio': 'linear'
     },
    '2':{'misspelled': {0:1, 'else':0},
     'responsive': {'true':1, 'false':0}, 'langcount':
     {1:0, 'else':1}, 'domain' :{'gov':1, 'org':0, 'edu':1,
        'com':0, 'net':0, 'else':-1},
        "lastmod" : {lastmodMaxMonths: 1, 'else': 0,},
     },
    'misc': {'hyperlinks':"linear"},
    'eval':['wot']
 }

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
                isoList = []
                for code in self.isoList:
                    # isoList.pop(iso)
                    isoList.append(str('='+code))
                    isoList.append(str('="'+code+'"'))
                self.isoList = isoList
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

# A class to get normalized score for given value based on collectData
class Normalize(object):

    # data = json_List
    # name =parameter to score
    def __init__(self, data=None, name=None):
        if not data or not name:
            raise WebcredError('Need 3 args, 2 pass')

        self.reverse = self.dataList = self.mean = self.deviation = None
        self.factorise = None

        self.data = data
        self.name = name[0]

        if isinstance(name[1], str):
            if  name[1] == 'reverse':
                self.reverse = True

        elif isinstance(name[1], dict):
            self.factorise = name[1]

    def getdatalist(self):
        if not self.dataList:
            dataList = []
            NumberTypes = (types.IntType, types.LongType, types.FloatType, types.ComplexType)
            for element in self.data:
                if element.get(self.name) and isinstance(element[self.name], NumberTypes):
                    # # done for decimal values like 0.23
                    # if isinstance(element[self.name], float):
                    #     element[self.name] = int(element[self.name]*1000000)
                    dataList.append(element[self.name])
            self.dataList = dataList

        # print self.dataList
        return self.dataList

    def normalize(self):
        NumberTypes = (types.IntType, types.LongType, types.FloatType, types.ComplexType)
        for index in range(len(self.data)):
            if isinstance(self.data[index].get(self.name), NumberTypes):
                self.data[index][self.name] = self.getscore(self.data[index][self.name])

        return self.data

    def getnormalizedScore(self, value):
        NumberTypes = (types.IntType, types.LongType, types.FloatType, types.ComplexType)
        if isinstance(value, NumberTypes):
            return self.getscore(value)

        # case when dimension value throws error
        # 0 because it  neither add nor reduces credibility
        return 0

    def getdata(self):
        return self.data

    def getmean(self):
        if not self.mean:
            self.mean =statistics.mean(self.getdatalist())
            print "mean=", self.mean, self.name
        return self.mean

    def getdeviation(self):
        if not self.deviation:
            self.deviation =statistics.pstdev(self.getdatalist())
            print "deviation=", self.deviation, self.name
        return self.deviation

    def getscore(self, value):
        mean = self.getmean()
        deviation = self.getdeviation()

        # somtimes mean<deviation and surpass good reults, as no value is less than 0
        netmd = mean-deviation
        if netmd<0:
            netmd = 0

        if value<=(netmd):
            if self.reverse:
                return 1
            return -1

        else :
            if value>=(mean+deviation):
                if self.reverse:
                    return -1
                return 1
            return 0

    def getfactoise(self, value):
        modified = 0
        global lastmodMaxMonths

        # condition for lastmod
        if self.name=="lastmod":
            value = self.getDateDifference(value)
            if value<lastmodMaxMonths:
                return self.factorise.get(lastmodMaxMonths)

        # condition for everthing else
        else:
            for k,v in self.factorise.items():
                if str(value) == str(k):
                    return v
        if 'else' in self.factorise.keys():
            return self.factorise.get('else')

    # return dayDiffernce form now and value
    def getDateDifference(self, value):
        try:
            # strptime  = string parse time
            # strftime = string format time
            lastmod = dt.strptime(value, '%Y-%m-%dT%H:%M:%S')
            dayDiffernce = (dt.now() - lastmod).days
            return dayDiffernce
        except:
            # in case of ValueError, lastmod will sum to WEBcred Score
            return 1000000

    def factoise(self):
        if not self.factorise:
            raise WebcredError('Provide attr to factorise')
        global lastmodMaxMonths

        for index in range(len(self.data)):
            if self.data[index].get(self.name):
                modified = 0

                # condition for lastmod
                if self.name=="lastmod":
                    value = self.data[index][self.name]
                    value = self.getDateDifference(value)
                    if value<lastmodMaxMonths:
                        self.data[index][self.name] = self.factorise.get(
                            lastmodMaxMonths)
                        modified = 1

                # condition for everthing else
                else:
                    for k,v in self.factorise.items():
                        value = self.data[index][self.name]
                        if str(value) == str(k):
                            self.data[index][self.name] = v
                            modified = 1
                if not modified:
                    if 'else' in self.factorise.keys():
                        self.data[index][self.name] = self.factorise.get('else')
        return self.data

# A class to use extract url attributes
class Urlattributes(object):
    try:
        # TODO fetch ads list dynamically from org
        if not patternMatching:
            patternMatching = PatternMatching(lang_iso='lang_iso.txt', ads_list='ads.txt' )
            print 'end patternMatching'

        global normalizedData
        global normalizeCategory
        if not normalizedData:
            normalizedData = {}
            # read existing data
            old_data = 'DATA/data2.json'
            old_data = open(old_data, 'r').read()
            old_data = old_data.split('\n')
            new_data = 'DATA/new_data.json'
            new_data = open(new_data, 'r').read()
            new_data = new_data.split('\n')
            re_data = 'DATA/re_data.json'
            re_data = open(re_data, 'r').read()
            re_data = re_data.split('\n')

            # list with string/buffer as values
            file_= list(set(new_data + old_data + re_data))

            # final json_List of data
            data = []
            for element in file_[:-1]:
                try:
                    metadata = json.loads(str(element))
                    # if metadata.get('redirected'):
                    #     url = metadata['redirected']
                    # else:
                    #     url = metadata['Url']
                    # obj = utils.Domain(url)
                    # url = obj.getnetloc()
                    # metadata['domain_similarity'] = scorefile_data.get(url)
                except:
                    continue
                if metadata.get('Error'):
                    continue
                data.append(metadata)

            it = normalizeCategory['3'].items()
            for k in it:
                normalizedData[k[0]] = Normalize(data, k)
                data = normalizedData[k[0]].normalize()

            it = normalizeCategory['misc'].items()[0]
            # summation of hyperlinks_attribute values
            for index in range(len(data)):
                if data[index].get(it[0]):
                    sum_hyperlinks_attributes = 0
                    tempData = data[index].get(it[0])
                    try:
                        for k,v in tempData.items():
                            sum_hyperlinks_attributes += v
                    except:
                        # TimeOut error clause
                        pass
                    finally:
                        data[index][it[0]] = sum_hyperlinks_attributes

            normalizedData[it[0]] = Normalize(data, it)
            data = normalizedData[it[0]].normalize()

            for k in normalizeCategory['2'].items():
                print "normalizing", k
                normalizedData[k[0]] = Normalize(data, k)
                data = normalizedData[k[0]].factoise()

            # csv_filename = 'analysis/WebcredNormalized.csv'
            #
            # pipe = Pipeline()
            # csv = pipe.convertjson(data)
            # f = open(csv_filename,'w')
            # f.write(csv)
            # f.close()

    except WebcredError as e:
        raise WebcredError(e.message)

    def __init__(self, url=None):
        # print 'here'
        if patternMatching:
            self.patternMatching = patternMatching

        self.hdr = {'User-Agent': 'Mozilla/5.0'}
        self.requests = self.urllibreq = self.soup = self.text = None
        self.netloc = self.header = self.size= self.domain = None
        self.lock = threading.Lock()
        if url:
            if not validators.url(url):
                raise WebcredError('Provide a valid url')
            self.originalUrl = self.url = str(url)
            # case of redirections
            resp =self.getrequests()
            self.url = str(resp.geturl())
            self.getsoup()
            # if url!= self.url:
            #     print 'redirected', url,' >> ', self.url
        else:
            raise WebcredError('Provide a url')

    def getoriginalurl(self):
        return self.originalUrl

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
        # with self.lock:
        # if not self.soup:
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
            t = self.gettext()
            try:
                self.size = len(t)
            except:
                raise WebcredError('error in retrieving length')
        return self.size

    def freemem(self):
        del self

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


    def run(self):
        try:
            # print 'Fetching {}'.format(self.name)
            if self.args:
                self.result = self.func(self.url, self.args)
            else:
                self.result = self.func(self.url)
            # print 'Got {}'.format(self.name)
        except WebcredError as e:
            self.result = e.message
        except:
            # if self.args:
            #     self.result = self.func(self.url, self.args)
            # else:
            #     self.result = self.func(self.url)
            self.result = '+++'

    def getResult(self):
        return self.result

    # clear url if Urlattributes object
    def freemem(self):
        self.url.freemem()

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
                request = dict(request.args)
            try:
                data = {}
                req = {}
                req['args'] = {}
                percentage = {}
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
                    if request.get(keys, None):
                        # because request.args is of ImmutableMultiDict form
                        if isinstance(request.get(keys, None), list):
                            req['args'][keys] = str(request.get(keys)[0])
                            perc = keys + "Perc"
                            if request.get(perc):
                                percentage[keys] = request.get(perc)[0]
                        else:
                            req['args'][keys] = request.get(keys)
                            perc = keys + "Perc"
                            if request.get(perc):
                                percentage[keys] = request.get(perc)

                # to show wot ranking
                req['args']['wot'] = "true"
                data['Url'] =  req['args']['site']

                if str(request.get('genre')[0])=='other':
                    data['Genre'] =  str(request.get('other-genre')[0])
                else:
                    data['Genre'] =  str(request.get('genre')[0])

                site = Urlattributes(url=req['args'].get('site', None))

                if data['Url'] != site.geturl():
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


                # HACK 13 is calculated number, refer to index.html, where new
                # dimensions are dynamically added
                number = 13
                while True:
                    dim = "dimension"+str(number)
                    API = "api"+str(number)
                    if dim in request.keys():
                        try:
                            data[request.get(dim)[0]] = api.dimapi(site.geturl(), request.get(API)[0])
                            perc = API + "Perc"
                            percentage[dim] = request.get(perc)[0]
                        except WebcredError as e:
                            data[request.get(dim)[0]] = e.message
                        except:
                            data[request.get(dim)[0]] = "Fatal ERROR"
                    else:
                        break
                    number += 1

                maxTime = 130
                for t in threads:
                    try:
                        t.join(maxTime)
                        data[t.getName()] = t.getResult()
                    except WebcredError as e:
                        data[t.getName()] = e.message
                    except:
                        data[t.getName()] = 'TimeOut Error, Max {} sec'.format(maxTime)
                    finally:
                        print t.getName()," = ", data[t.getName()]

            except WebcredError as e:
                data['Error'] =  e.message
            except:
                data['Error'] = 'Fatal error'
            finally:
                try:
                    site.freemem()
                finally:
                    data = self.webcredScore(data, percentage)
                    return data

    def webcredScore(self, data, percentage):
        global normalizedData
        global normalizeCategory
        # score varies from -1 to 1
        score = 0
        for k,v in data.items():

            try:
                if k in normalizeCategory['3'].keys():
                    name = k + "Norm"
                    data[name] = normalizedData[k].getnormalizedScore(v)
                    score += data[name]*float(percentage[k])

                if k in normalizeCategory['2'].keys():
                    name = k + "Norm"
                    data[name] = normalizedData[k].getfactoise(v)
                    score += data[name]*float(percentage[k])

                if k in normalizeCategory['misc'].keys():
                    sum_hyperlinks_attributes = 0
                    try:
                        for key,value in v.items():
                            sum_hyperlinks_attributes += value
                        name = k + "Norm"
                        data[name] = normalizedData[k].getnormalizedScore(sum_hyperlinks_attributes)
                        score += data[name]*float(percentage[k])
                    except:
                        # TimeOut error clause
                        pass
            except:
                pass
        data["WEBCred Score"] = score/100

        # REVIEW add Weightage score for new dimensions
        return data



import api
import app
