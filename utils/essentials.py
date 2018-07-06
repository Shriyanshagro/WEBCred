import logging
import threading


logger = logging.getLogger('WEBCred.utils')
logging.basicConfig(level=logging.INFO)


# A class to catch error and exceptions
class WebcredError(Exception):
    """An error happened during assessment of site.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class MyThread(threading.Thread):
    # def __init__(
    #         self, Module='api', Method=None, Name=None, Url=None, Args=None
    # ):
    #     pass

    def __init__(self, func, Name, Url, Args=None):

        threading.Thread.__init__(self)

        # if Method and Module == 'api':
        #     self.func = getattr(surface, Method)
        # elif Method and Module == 'app':
        #     logger.info("app is called")
        #     import pdb
        #     pdb.set_trace()
        #     # self.func = getattr(app, Method)
        self.func = func
        self.name = Name
        self.url = Url
        self.args = Args

        if Args and Args != '':
            self.args = Args

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
