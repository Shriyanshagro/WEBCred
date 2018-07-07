from datetime import datetime
from features import surface
from utils.essentials import MyThread
from utils.essentials import WebcredError
from utils.urls import normalizeCategory
from utils.urls import normalizedData
from utils.urls import Urlattributes

import logging

logger = logging.getLogger('WEBCred.utils')
logging.basicConfig(level=logging.INFO)

# keywords used to check real_world_presence
hyperlinks_attributes = ['contact', 'email', 'help', 'sitemap']

# map feature to function name
# these keys() are also used to define db columns
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
    'site': [''],
}


class Webcred(object):
    def __init__(self, db, Features, request):
        self.db = db
        self.Features = Features
        self.request = request

    def assess(self):

        now = datetime.now()

        if not isinstance(self.request, dict):
            self.request = dict(self.request.args)

        modified = 0
        try:
            data = {}
            req = {}
            req['args'] = {}
            percentage = {}

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

            site = Urlattributes(url=req['args'].get('site', None))

            # get genre
            data['genre'] = str(self.request.get('genre', ['other'])[0])

            if data['Url'] != site.geturl():
                data['redirected'] = site.geturl()

            data['lastmod'] = site.getlastmod()

            # site is not a WEBCred parameter
            del req['args']['site']

            # check database,
            # if url is already present?
            # TODO check data types issue
            if self.db.session.query(
                    self.Features).filter(self.Features.Url == data['Url']
                                          ).count():
                # if lastmod is not changed?
                # HACK self.Features.lastmod doesn't show None value
                if self.db.session.query(
                        self.Features
                ).filter(self.Features.lastmod == str(data['lastmod'])
                         ).count() or not data['lastmod']:
                    # get all existing data in dict format
                    dbData = self.db.session.query(
                        self.Features
                    ).filter(self.Features.Url == data['Url']
                             ).all()[0].__dict__
                    # HACK for few cases, this should not be done?
                    # check the ones from apilist which have non None value
                    # put them as False
                    '''
                    None value indicates that feature has not been
                    evaluated yet
                    '''
                    for k, v in dbData.items():
                        if v:
                            req['args'][k] = 'false'
                    # for values
                    # update the database
                    data = self.extractValue(req, apiList, data, site)
                    modified = 1
                # assess all data again
                else:
                    data = self.extractValue(req, apiList, data, site)

            # else create new entry, url
            else:
                data = self.extractValue(req, apiList, data, site)

            # HACK 13 is calculated number, refer to index.html, where new
            # dimensions are dynamically added
            # create percentage dictionary
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

            data = self.webcredScore(data, percentage)

        except WebcredError as e:
            data['Error'] = e.message
            logger.debug('Webcred Issue with webcred.assess')
        except Exception as e:
            data['Error'] = 'Fatal error'
            logger.info(e)
        finally:

            now = str((datetime.now() - now).total_seconds())
            # store it in data
            try:
                if modified:
                    logger.info('updating entry')
                    logger.info(data['Url'])
                    self.db.session.query(
                        self.Features
                    ).filter(self.Features.Url == data['Url']).update(data)

                else:
                    logger.info('creating new entry')
                    logger.info(data['Url'])
                    data['assess_time'] = now
                    reg = self.Features(data)
                    self.db.session.add(reg)

                self.db.session.commit()

                data = self.db.session.query(
                    self.Features
                ).filter(self.Features.Url == data['Url']).all()[0].__dict__

            except Exception as e:
                logger.info(e)

            logger.info(now)

            return data

    def webcredScore(self, data, percentage):
        # score varies from -1 to 1
        score = 0
        # take all keys of data into account
        for k, v in data.items():

            try:
                if k in normalizeCategory['3'
                                          ].keys() and k in percentage.keys():
                    name = k + "Norm"
                    data[name] = normalizedData[k].getnormalizedScore(v)
                    score += data[name] * float(percentage[k])

                if k in normalizeCategory['2'
                                          ].keys() and k in percentage.keys():
                    name = k + "Norm"
                    data[name] = normalizedData[k].getfactoise(v)
                    score += data[name] * float(percentage[k])

                if k in normalizeCategory['misc'
                                          ].keys() and k in percentage.keys():
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
                        logger.info('Issue with misc normalizing categories')
                        # TimeOut error clause
            except:
                import pdb
                pdb.set_trace()
                logger.info('Not able to calculate webcred score')
        data["webcred_score"] = score / 100

        # REVIEW add Weightage score for new dimensions
        return data

    # TODO put assessed but NONE value with some string
    # to differentiate it with DB null value
    def extractValue(self, req, apiList, data, site):
        # assess requested features
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

        # wait to join all threads in order to get all results
        maxTime = 180
        for t in threads:
            try:
                t.join(maxTime)
                data[t.getName()] = t.getResult()
            except WebcredError as e:
                data[t.getName()] = e.message
            except:
                data[t.getName()] = 'TimeOut Error, Max {} sec'.format(maxTime)
            finally:
                logger.debug(t.getName(), " = ", data[t.getName()])

        return data
