import logging
import threading


logger = logging.getLogger('WEBCred.essentials')
logging.basicConfig(
    filename='log/logging.log',
    filemode='a',
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)


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

        self.func = func
        self.name = Name
        self.url = Url
        self.args = Args
        self.result = None

        if Args and Args != '':
            self.args = Args

    def run(self):
        try:
            if self.args:
                self.result = self.func(self.url, self.args)
            else:
                self.result = self.func(self.url)
        except Exception as e:
            logger.debug(e)
            self.result = None

    def getResult(self):
        return self.result

    # clear url if Urlattributes object
    def freemem(self):
        self.url.freemem()
