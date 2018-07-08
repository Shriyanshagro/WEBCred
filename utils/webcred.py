from datetime import datetime
from features import surface
from utils.essentials import MyThread
from utils.essentials import WebcredError
from utils.urls import normalizeCategory
from utils.urls import normalizedData
from utils.urls import Urlattributes

import logging

logger = logging.getLogger('WEBCred.webcred')
logging.basicConfig(level=logging.INFO)

# keywords used to check real_world_presence
hyperlinks_attributes = ['contact', 'email', 'help', 'sitemap']

# map feature to function name
# these keys() are also used to define db columns
apiList = {
    'lastmod': ['getDate', '', '', 'Integer'],
    'domain': ['getDomain', '', '', 'String(120)'],
    'inlinks': [
        'getInlinks',
        '',
        '',
        'Integer',
    ],
    'outlinks': [
        'getOutlinks',
        '',
        '',
        'Integer',
    ],
    'hyperlinks': [
        'getHyperlinks',
        hyperlinks_attributes,
        '',
        'JSON',
    ],
    'imgratio': ['getImgratio', '', '', 'FLOAT'],
    'brokenlinks': ['getBrokenlinks', '', '', 'Integer'],
    'cookie': ['getCookie', '', '', 'Boolean'],
    'langcount': ['getLangcount', '', '', 'Integer'],
    'misspelled': ['getMisspelled', '', '', 'Integer'],
    'wot': ['getWot', '', 'JSON'],
    'responsive': ['getResponsive', '', '', 'Boolean'],
    'ads': ['getAds', '', 'Integer'],
    'pageloadtime': ['getPageloadtime', '', '', 'Integer'],
    'site': [
        '',
        '',
        '',
        'String(120)',
    ],
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
        data = {}
        req = {}
        req['args'] = {}
        percentage = {}
        try:

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
            # TODO fetch other weightages
            data['genre'] = str(self.request.get('genre', ['other'])[0])

            if data['Url'] != site.geturl():
                data['redirected'] = site.geturl()

            data['lastmod'] = site.getlastmod()

            # site is not a WEBCred parameter
            del req['args']['site']

            # check database,
            # if url is already present?
            if self.db.session.query(
                    self.Features).filter(self.Features.Url == data['Url']
                                          ).count():
                # is lastmod changed?
                if self.db.session.query(
                        self.Features
                ).filter(self.Features.lastmod == data['lastmod']
                         ).count() or not data['lastmod']:
                    # get all existing data in dict format
                    dbData = self.db.session.query(
                        self.Features
                    ).filter(self.Features.Url == data['Url']
                             ).all()[0].__dict__
                    # check the ones from columns which have non None value
                    '''
                    None value indicates that feature has not
                    successfully extracted yet
                    '''
                    for k, v in dbData.items():
                        if v:
                            req['args'][k] = 'false'
                # update the database
                modified = 1
            # else create new entry, url
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
            logger.info(e)
        except Exception as e:
            logger.info(e)
            # HACK if it's not webcred error,
            #  then probably it's python error
            data['Error'] = 'Fatal Error'
            modified = 1
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
                self.db.session.rollback()
                logger.debug(e)

            logger.info('Time = {}'.format(now))

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
                logger.info('Not able to calculate webcred score')
        data["webcred_score"] = score / 100

        # TODO add Weightage score for new dimensions
        return data

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
        maxTime = 300
        for t in threads:
            try:
                t.join(maxTime)
                data[t.getName()] = t.getResult()
            except Exception as er:
                logger.debug(er)
                data[t.getName()] = None
            finally:
                logger.debug('{} = {}'.format(t.getName(), data[t.getName()]))

        return data
