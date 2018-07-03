from datetime import datetime as dt
from utils.pipeline import Pipeline
from utils.utils import WebcredError

import bs4
import copy
import cPickle
import json
import numpy as np
import statistics
import sys
import types
import urllib


sys.path.insert(0, r'../../')

global genre_weightage
global normalizedData
normalizedData = None

global lastmodMaxMonths
lastmodMaxMonths = 93

# define rules to normalize data
global normalizeCategory
normalizeCategory = {
    '3': {
        'outlinks': 'reverse',
        'inlinks': 'linear',
        'ads': 'reverse',
        'brokenlinks': 'reverse',
        'pageloadtime': 'reverse',
        'imgratio': 'linear'
    },
    '2': {
        'misspelled': {
            0: 1,
            'else': 0
        },
        'responsive': {
            'true': 1,
            'false': 0
        },
        'langcount': {
            1: 0,
            'else': 1
        },
        'domain': {
            'gov': 1,
            'org': 0,
            'edu': 1,
            'com': 0,
            'net': 0,
            'else': -1
        },
        "lastmod": {
            lastmodMaxMonths: 1,
            'else': 0,
        },
    },
    'misc': {
        'hyperlinks': "linear"
    },
    'eval': ['wot']
}

genre_weightage = {
    'articles': [
        0.079, 0.053, 0.105, 0.105, 0.079, 0.079, 0.053, 0.053, 0.105, 0.105,
        0.105, 0.079
    ],
    'help': [
        0.059, 0.059, 0.059, 0.059, 0.059, 0.059, 0.059, 0.059, 0.059, 0.059,
        0.176, 0.235
    ],
    'shop': [
        0.069, 0.138, 0.103, 0.069, 0.069, 0.138, 0.103, 0.103, 0.069, 0.069,
        0.034, 0.034
    ],
    'Portrayl-org': [
        0.111, 0.083, 0.056, 0.083, 0.111, 0.056, 0.111, 0.111, 0.083, 0.083,
        0.056, 0.056
    ]

    # 'others' : []
}


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
            if name[1] == 'reverse':
                self.reverse = True

        elif isinstance(name[1], dict):
            self.factorise = name[1]

    def getdatalist(self):
        if not self.dataList:
            dataList = []
            NumberTypes = (
                types.IntType, types.LongType, types.FloatType,
                types.ComplexType
            )
            for element in self.data:
                if element.get(self.name) and isinstance(element[self.name],
                                                         NumberTypes):
                    # # done for decimal values like 0.23
                    # if isinstance(element[self.name], float):
                    #     element[self.name] = int(element[self.name]*1000000)
                    dataList.append(element[self.name])
            self.dataList = dataList

        # print self.dataList
        return self.dataList

    def normalize(self):
        NumberTypes = (
            types.IntType, types.LongType, types.FloatType, types.ComplexType
        )
        for index in range(len(self.data)):
            if isinstance(self.data[index].get(self.name), NumberTypes):
                self.data[index][self.name] = self.getscore(
                    self.data[index][self.name]
                )

        return self.data

    def getnormalizedScore(self, value):
        NumberTypes = (
            types.IntType, types.LongType, types.FloatType, types.ComplexType
        )
        if isinstance(value, NumberTypes):
            return self.getscore(value)

        # case when dimension value throws error
        # 0 because it  neither add nor reduces credibility
        return 0

    def getdata(self):
        return self.data

    def getmean(self):
        if not self.mean:
            self.mean = statistics.mean(self.getdatalist())
            print "mean=", self.mean, self.name
        return self.mean

    def getdeviation(self):
        if not self.deviation:
            self.deviation = statistics.pstdev(self.getdatalist())
            print "deviation=", self.deviation, self.name
        return self.deviation

    def getscore(self, value):
        mean = self.getmean()
        deviation = self.getdeviation()
        """
        somtimes mean<deviation and surpass good reults,
        as no value is less than 0
        """
        netmd = mean - deviation
        if netmd < 0:
            netmd = 0

        if value <= (netmd):
            if self.reverse:
                return 1
            return -1

        else:
            if value >= (mean + deviation):
                if self.reverse:
                    return -1
                return 1
            return 0

    def getfactoise(self, value):
        global lastmodMaxMonths

        # condition for lastmod
        if self.name == "lastmod":
            value = self.getDateDifference(value)
            if value < lastmodMaxMonths:
                return self.factorise.get(lastmodMaxMonths)

        # condition for everthing else
        else:
            for k, v in self.factorise.items():
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
                if self.name == "lastmod":
                    value = self.data[index][self.name]
                    value = self.getDateDifference(value)
                    if value < lastmodMaxMonths:
                        self.data[index][
                            self.name
                        ] = self.factorise.get(lastmodMaxMonths)
                        modified = 1

                # condition for everthing else
                else:
                    for k, v in self.factorise.items():
                        value = self.data[index][self.name]
                        if str(value) == str(k):
                            self.data[index][self.name] = v
                            modified = 1
                if not modified:
                    if 'else' in self.factorise.keys():
                        self.data[index][self.name
                                         ] = self.factorise.get('else')
        return self.data


# if rank not available, 999999999 wil be returned
def getAlexarank(url):
    try:
        rank = bs4.BeautifulSoup(
            urllib.
            urlopen("http://data.alexa.com/data?cli=10&dat=s&url=" +
                    url).read(), "xml"
        ).find("REACH")['RANK']
    except:
        rank = '999999999'
    return rank


def webcredscore(featurevalue, percentage):
    # matrix multiply
    pass


def normalize():
    global normalizedData
    global normalizeCategory
    if not normalizedData:
        normalizedData = {}
        # read existing data
        old_data = '../data2.json'
        old_data = open(old_data, 'r').read()
        old_data = old_data.split('\n')
        new_data = '../new_data.json'
        new_data = open(new_data, 'r').read()
        new_data = new_data.split('\n')
        re_data = '../re_data.json'
        re_data = open(re_data, 'r').read()
        re_data = re_data.split('\n')

        # list with string/buffer as values
        file_ = list(set(new_data + old_data + re_data))
        # final json_List of data
        data = []
        for element in file_[:-1]:
            try:
                # ranflag = 1
                # error_catch = ['*TimeOut*', "*limit*", '*+++*']
                # for i in error_catch:
                #     if fnmatch.fnmatch(str(element),i):
                #         ranflag = '0'
                #         break
                # if ranflag == '0':
                #     continue
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
                    for k, v in tempData.items():
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


def getNormalize(data):

    global normalizedData
    global normalizeCategory

    for k, v in data.items():

        try:
            if k in normalizeCategory['3'].keys():
                name = k
                data[name] = normalizedData[k].getnormalizedScore(v)
                # score += data[name]*float(percentage[k])

            if k in normalizeCategory['2'].keys():
                name = k
                data[name] = normalizedData[k].getfactoise(v)
                # score += data[name]*float(percentage[k])

            if k in normalizeCategory['misc'].keys():
                sum_hyperlinks_attributes = 0
                try:
                    for key, value in v.items():
                        sum_hyperlinks_attributes += value
                    name = k
                    data[name] = normalizedData[k].getnormalizedScore(
                        sum_hyperlinks_attributes
                    )
                    # score += data[name]*float(percentage[k])
                except:
                    # TimeOut error clause
                    pass
        except:
            pass

    return data


if __name__ == '__main__':

    print '''
    c = check_similarity of WebcredScore with alexaScore and wotScore
    s = simulate csv and form pickles for genre-labelled samples
    '''
    work = raw_input('what do you want?')

    if work == 's':
        normalize()
        global genre_weightage
        # read data
        genre_labelled = "/home/shriyanshagro/Academics/Research/WEBCred" \
                         "/DATA/Similarity_check/Genre-labelled Data.csv"
        score_file = "/home/shriyanshagro/Academics/Research/WEBCred/" \
                     "DATA/Similarity_check/validation.csv"

        f = open(genre_labelled, 'r')
        data = f.readlines()
        pipe = Pipeline()
        jsonData = pipe.converttojson(data)
        WEBCredScoreSet = []
        alexaScoreSet = []
        wotScoreSet = []

        Links = [
            'inlinks',
            # 'outlinks', 'brokenlinks'
        ]
        content = ['misspelled', 'lastmod', 'ads', 'imgratio']
        presence = ['hyperlinks', 'domain']
        others = ['langcount', 'responsive', 'pageloadtime']
        # FeaturesName in order with data
        FeaturesName = []
        FeaturesName += Links
        FeaturesName += content
        FeaturesName += presence
        FeaturesName += others
        # print FeaturesName
        # import pdb; pdb.set_trace()
        # FeaturesName += 'inlinks'

        FeaturesNaming = [
            'domain', 'ads', 'imgratio', 'inlinks', 'misspelled',
            'pageloadtime', 'brokenlinks', 'hyperlinks', 'responsive',
            'lastmod', 'langcount', 'outlinks'
        ]

        genre_flag = ['articles', 'help', 'shop', 'Portrayl-org']
        datas = copy.deepcopy(jsonData)

        for m in genre_flag:

            jsonData = copy.deepcopy(datas)
            for i in range(len(jsonData)):

                genre = jsonData[i].get('genre')

                jsonData[i]['alexaScore'] = "{0:.7f}".format(
                    (1.00) / (json.loads(getAlexarank(jsonData[i]['url'])))
                )

                if isinstance(jsonData[i].get('wot'), list):
                    jsonData[i]['wotScore'] = "{0:.7f}".format(
                        (jsonData[i]['wot'][0] * jsonData[i]['wot'][1]) /
                        (10000.00)
                    )
                else:
                    jsonData[i]['wotScore'] = 0.00
                del jsonData[i]['wot']

                if not genre == m:
                    # TODO mayfill with geric weightages
                    jsonData[i]['WEBCredScore'] = 'Generic Genre'
                    continue

                weightage = genre_weightage[genre]
                weights = []
                temp = copy.deepcopy(jsonData[i])
                # normalize
                normalized_value = getNormalize(temp)

                featurevalue = []
                for j in FeaturesName:
                    featurevalue.append(normalized_value.get(j))
                    weights.append(weightage[FeaturesNaming.index(j)])

                WEBCredScore = 0
                for l in range(len(featurevalue)):
                    if featurevalue[l] and featurevalue[l] != '+++':
                        WEBCredScore += featurevalue[l] * weights[l]

                jsonData[i]['WEBCredScore'] = WEBCredScore

                WEBCredScoreSet.append(jsonData[i]['WEBCredScore'])
                alexaScoreSet.append(jsonData[i]['alexaScore'])
                wotScoreSet.append(jsonData[i]['wotScore'])

                # print WEBCredScoreSet, alexaScoreSet, wotScoreSet

            # with open(r"WEBCredScoreSet.pickle", "w") as output_file:
            #     cPickle.dump(WEBCredScoreSet, output_file)
            #
            # with open(r"alexaScoreSet.pickle", "w") as output_file:
            #     cPickle.dump(alexaScoreSet, output_file)
            #
            # with open(r"wotScoreSet.pickle", "w") as output_file:
            #     cPickle.dump(wotScoreSet, output_file)
            #

            alexaSimilarity = np.corrcoef(
                np.asarray(alexaScoreSet).astype(np.float),
                np.asarray(WEBCredScoreSet).astype(np.float)
            ).tolist()[0][1]
            wotSimilarity = np.corrcoef(
                np.asarray(wotScoreSet).astype(np.float),
                np.asarray(WEBCredScoreSet).astype(np.float)
            ).tolist()[0][1]

            print m, FeaturesName
            print 'alexaSimilarity == ', alexaSimilarity
            print 'wotSimilarity == ', wotSimilarity

        # pipe = Pipeline()
        # csv = pipe.convertjson(jsonData)
        # f = open(score_file,'w')
        # f.write(csv)
        # f.close()

    elif work == 'c':

        with open(r"WEBCredScoreSet.pickle", "rb") as input_file:
            WEBCredScoreSet = cPickle.load(input_file)

        with open(r"alexaScoreSet.pickle", "rb") as input_file:
            alexaScoreSet = cPickle.load(input_file)

        with open(r"wotScoreSet.pickle", "rb") as input_file:
            wotScoreSet = cPickle.load(input_file)

        alexaSimilarity = np.corrcoef(
            np.asarray(alexaScoreSet).astype(np.float),
            np.asarray(WEBCredScoreSet).astype(np.float)
        ).tolist()[0][1]
        wotSimilarity = np.corrcoef(
            np.asarray(wotScoreSet).astype(np.float),
            np.asarray(WEBCredScoreSet).astype(np.float)
        ).tolist()[0][1]

        print 'alexaSimilarity == ', alexaSimilarity
        print 'wotSimilarity == ', wotSimilarity
