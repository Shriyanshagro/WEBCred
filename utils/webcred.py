from datetime import datetime
from features import surface
from utils.essentials import MyThread
from utils.essentials import WebcredError
from utils.urls import Urlattributes

import logging

logger = logging.getLogger('WEBCred.utils')
logging.basicConfig(level=logging.INFO)


class Webcred(object):
    def __init__(self, db, Features, request):
        self.db = db
        self.Features = Features
        self.request = request

    def assess(self, ):

        now = datetime.now()

        if not isinstance(self.request, dict):
            self.request = dict(self.request.args)

        try:
            data = {}
            req = {}
            req['args'] = {}
            percentage = {}
            hyperlinks_attributes = ['contact', 'email', 'help', 'sitemap']

            # map feature to function name
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

            # get percentage of each feature
            for keys in apiList.keys():
                if self.request.get(keys, None):
                    # because self.request.args is of ImmutableMultiDict form
                    if isinstance(self.request.get(keys, None), list):
                        req['args'][keys] = str(self.request.get(keys)[0])
                        perc = keys + "Perc"
                        if self.request.get(perc):
                            percentage[keys] = self.request.get(perc)[0]
                    else:
                        req['args'][keys] = self.request.get(keys)
                        perc = keys + "Perc"
                        if self.request.get(perc):
                            percentage[keys] = self.request.get(perc)

            # to show wot ranking
            req['args']['wot'] = "true"
            data['Url'] = req['args']['site']

            if self.request.session.query(
                    self.Features).filter(self.Features.url == data['Url']
                                          ).count():
                now = str((datetime.now() - now).total_seconds())
                logger.info(data['Url'])
                logger.info(now)
                return self.request.session.query(
                    self.Features
                ).filter(self.Features.url == data['Url'])

            # get genre
            data['Genre'] = str(self.request.get('genre', ['other'])[0])

            site = Urlattributes(url=req['args'].get('site', None))

            if data['Url'] != site.geturl():
                data['redirected'] = site.geturl()

            # site is not a WEBCred parameter
            del req['args']['site']
            threads = []
            for keys in req['args'].keys():
                if str(req['args'].get(keys, None)) == "true":
                    Method = apiList[keys][0]
                    Name = keys
                    Url = site
                    Args = apiList[keys][1]
                    func = getattr(surface, Method)
                    thread = MyThread(func, Name, Url, Args)
                    thread.start()
                    threads.append(thread)

            # HACK 13 is calculated number, refer to index.html, where new
            # dimensions are dynamically added
            number = 13
            while True:
                dim = "dimension" + str(number)
                API = "api" + str(number)
                if dim in self.request.keys():
                    try:
                        data[self.request.get(dim)[0]] = surface.dimapi(
                            site.geturl(),
                            self.request.get(API)[0]
                        )
                        perc = API + "Perc"
                        percentage[dim] = self.request.get(perc)[0]
                    except WebcredError as e:
                        data[self.request.get(dim)[0]] = e.message
                    except:
                        data[self.request.get(dim)[0]] = "Fatal ERROR"
                else:
                    break
                number += 1

            maxTime = 180
            for t in threads:
                try:
                    t.join(maxTime)
                    data[t.getName()] = t.getResult()
                except WebcredError as e:
                    data[t.getName()] = e.message
                except:
                    data[t.getName()
                         ] = 'TimeOut Error, Max {} sec'.format(maxTime)
                finally:
                    logger.debug(t.getName(), " = ", data[t.getName()])

        except WebcredError as e:
            data['Error'] = e.message
        except:
            data['Error'] = 'Fatal error'
        finally:
            try:
                site.freemem()
            finally:
                data = self.webcredScore(data, percentage)
                now = str((datetime.now() - now).total_seconds())
                logger.info(data['Url'])
                logger.info(now)
                return data

    def webcredScore(self, data, percentage):
        global normalizedData
        global normalizeCategory
        # score varies from -1 to 1
        score = 0
        for k, v in data.items():

            try:
                if k in normalizeCategory['3'].keys():
                    name = k + "Norm"
                    data[name] = normalizedData[k].getnormalizedScore(v)
                    score += data[name] * float(percentage[k])

                if k in normalizeCategory['2'].keys():
                    name = k + "Norm"
                    data[name] = normalizedData[k].getfactoise(v)
                    score += data[name] * float(percentage[k])

                if k in normalizeCategory['misc'].keys():
                    sum_hyperlinks_attributes = 0
                    try:
                        for key, value in v.items():
                            sum_hyperlinks_attributes += value
                        name = k + "Norm"
                        data[name] = normalizedData[k].getnormalizedScore(
                            sum_hyperlinks_attributes
                        )
                        score += data[name] * float(percentage[k])
                    except:
                        # TimeOut error clause
                        pass
            except:
                pass
        data["WEBCred Score"] = score / 100

        # REVIEW add Weightage score for new dimensions
        return data
