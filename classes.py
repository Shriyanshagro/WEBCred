import requests
import urllib2
from urlparse import urlparse
from bs4 import BeautifulSoup, SoupStrainer
import pdb
# A class to catch error and exceptions
class webcredError(Exception):
    """An error happened during assessment of site.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


# A class to use extract url attributes
class urlattributes(object):

    def __init__(self, url):
        self.url = str(url)
        self.hdr = {'User-Agent': 'Mozilla/5.0'}
        self.flagrequests = 0
        self.flagurllib = 0
        self.flagsoup = 0
        self.flagtext = 0

    def getrequests(self):
        self.flagrequests = 1

    def gettext(self):
        self.flagtext = 1

    def getsoup(self):
        self.flagsoup = 1

    def geturllib(self):
        self.flagurllib = 1

    def requests(self):
        if self.flagrequests == 0:
            self.request =  requests.get(self.url, headers=self.hdr)

        self.getrequests()
        return self.request

    def urllibreq(self):
        if self.flagurllib == 0:
            # binding the request
            req = urllib2.Request(self.url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            self.urllibreq = urllib2.urlopen(req)

        self.geturllib()
        return self.urllibreq

    def geturl(self):
        return self.url

    def text(self):
        if self.flagtext == 0:
            self.text = self.requests().text
        self.gettext()
        return self.text

    def soup(self):
        # pdb.set_trace()
        if self.flagsoup == 0:
            data = self.text()
            self.soup = BeautifulSoup(data, "html.parser")
        self.getsoup()
        return self.soup
