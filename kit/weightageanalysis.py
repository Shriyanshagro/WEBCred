# sum of all weightage== 1, misc. genre == 0.1

# some mac os stuff
import matplotlib  # isort:skip
matplotlib.use('TkAgg')  # isort:skip
import matplotlib.pyplot as pl  # isort:skip

from app import db
from datetime import datetime as dt
from features.surface import getAlexarank
from features.surface import getWot
from fnmatch import fnmatch
from sklearn.model_selection import KFold
from utils.pipeline import Pipeline

import cPickle
import json
import logging
import numpy as np
import pandas as pd
import random
import seaborn as sns
import subprocess
import sys
import traceback

logger = logging.getLogger('WEBCred.surface')
logging.basicConfig(
    filename='log/logging.log',
    filemode='a',
    format='[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)

global totalSample
global jsonData
global Featureset
global alexaScoreSet
global FeaturesName
global repetetion

repetetion = 0


# filter data
# data = json dict
def filter(data):
    errorString = ['*Error*', '*+++*', '*NA*', '*limit*']
    for i in errorString:
        if fnmatch(json.dumps(data), i):
            return False
    return True


def getFeatureValue(sampleSet, FeaturesName):

    # get feature Values out of dict
    featurevalue = []
    alexaScore = []
    wotScore = []
    for i in range(len(sampleSet)):

        temp = []
        for j in FeaturesName:
            temp.append(sampleSet[i].get(j))

        # row - feature values of individial sampels
        featurevalue.append(temp)
        # appending alexa score of each sample
        # 1000 is acting as a proportinality constant
        alexaScore.append(
            "{:.15f}".format(1000 / float(sampleSet[i].get('alexaRank')))
        )
        wotScore.append(sampleSet[i].get('wot'))

    return featurevalue, alexaScore, wotScore


def getFeatures(sampleSet, FeaturesName):

    # get feature Values out of dict
    featurevalue = []
    alexaScore = []
    wotScore = []
    for i in range(len(sampleSet)):
        temp = []
        for j in FeaturesName:
            if j == 'hyperlinks':
                sum_hyperlinks_attributes = 0
                tempData = sampleSet[i].get(j)
                try:
                    for k, v in tempData.items():
                        sum_hyperlinks_attributes += v
                except:
                    # TimeOut error clause
                    pass
                finally:
                    temp.append(sum_hyperlinks_attributes)
                    # data[index][it[0]] = sum_hyperlinks_attributes
            elif j == 'responsive':
                tempData = sampleSet[i].get(j)
                try:
                    if tempData == 'false':
                        tempData = 0
                    elif tempData == 'true':
                        tempData = 1
                except:
                    # TimeOut error clause
                    pass
                finally:
                    temp.append(tempData)
            elif j == 'lastmod':
                lastmod = dt.strptime(sampleSet[i].get(j), '%Y-%m-%dT%H:%M:%S')
                dayDiffernce = (dt.now() - lastmod).days
                temp.append(dayDiffernce)
            elif j == 'domain':
                domain = {
                    'gov': 1,
                    'org': 0,
                    'edu': 1,
                    'com': 0,
                    'net': 0,
                    'else': -1
                }
                if sampleSet[i].get(j) in domain.keys():
                    temp.append(domain.get(sampleSet[i].get(j)))
                else:
                    temp.append(-1)

            else:
                temp.append(sampleSet[i].get(j))

        # row - feature values of individial sampels
        featurevalue.append(temp)
        # appending alexa score of each sample
        # 1000 is acting as a proportinality constant
        alexaScore.append(
            "{:.15f}".format(1000 / float(sampleSet[i].get('alexaRank')))
        )
        wotScore.append(sampleSet[i].get('wot'))

    return featurevalue, alexaScore, wotScore


def getNoise(length):
    temp = []
    for i in range(0, length):
        # temp.append("{:.15f}".format(random.uniform(0, 0.00005)))
        temp.append(random.uniform(-1, 1))
    return temp


def getWeightage(Featureset, alexaScoreSet):
    global FeaturesName
    global repetetion

    while True:
        try:
            features = np.array(Featureset)
            alexa = np.array(alexaScoreSet, dtype='float')
            # print Featureset, alexaScoreSet
            weightage = np.linalg.lstsq(features, alexa, rcond=None)[0]
            weightage = np.transpose(weightage).tolist()[0]
            # weightage = np.linalg.solve(features, alexa)
            break
        except:
            repetetion += 1
            print repetetion
            Featureset.append(getNoise(len(Featureset[0])))
            alexaScoreSet.append([
                "{:.15f}".format(random.uniform(0, 10) / 1000)
            ])
            # print Featureset

            # sample = getjsonData()
            # featurevalue, alexaScore = getFeatureValue([sample],
            #                                            FeaturesName)
            # if checksimiliarData(featurevalue[0]):
            #     Featureset.append(featurevalue[0])
            #     alexaScoreSet.append(alexaScore)

    # print weightage
    return weightage


def checksimiliarData(featurevalue):
    global Featureset

    if featurevalue in Featureset:
        return False
    return True


def getjsonData():
    global totalSample
    global jsonData
    while True:
        var = random.randint(0, totalSample)
        if filter(jsonData[var]):
            # get alexa rank
            if jsonData[var].get('redirected'):
                jsonData[var]['alexaRank'] = getAlexarank(
                    jsonData[var].get('redirected')
                )
            else:
                jsonData[var]['alexaRank'] = getAlexarank(
                    jsonData[var].get('url')
                )
            return jsonData[var]


def calculateWeightage():
    global totalSample
    global jsonData
    global Featureset

    csv_filename = "WebcredNormalized.csv"

    f = open(csv_filename, 'r')
    data = f.readlines()
    pipe = Pipeline()
    # get json data
    jsonData = pipe.converttojson(data)
    totalSets = 10
    # sets of possible weightages
    weightage = []
    totalSample = int(
        subprocess.check_output(['wc', '-l', csv_filename]).split(' ')[0]
    ) - 1
    filterKeys = ['url', 'wot', 'cookie', 'redirected']
    FeaturesName = list((set(jsonData[0].keys()) - set(filterKeys)))

    Featureset = []
    alexaScoreSet = []

    for i in range(totalSets):
        count = 0
        # select sample sets
        while True:
            sample = getjsonData()
            featurevalue, alexaScore, wotScore = getFeatureValue([sample],
                                                                 FeaturesName)
            if checksimiliarData(featurevalue[0]):
                Featureset.append(featurevalue[0])
                alexaScoreSet.append(alexaScore)
                count += 1
                if count == len(FeaturesName) - 1:
                    # sum of all weightage== 1, misc. genre == 0.1
                    temp = []
                    for j in range(len(FeaturesName)):
                        temp.append(1)
                    Featureset.append(temp)
                    alexaScoreSet.append([0.9])
                    break

        # get weightage of individual feature
        weightage.append(getWeightage(Featureset, alexaScoreSet))
        print 'getting', i, 'set of weightages'

    finalWeightage = np.mean(weightage, axis=0).tolist()

    total = 0
    for i in finalWeightage:
        total += i

    print total
    print finalWeightage

    # 0.0009
    # [
    #     2.2236760132294826, -7.914215741530812, 13.670499590165207,
    #     0.6997838591507087, -18.92453210550777, -2.1201375082255307,
    #     3.47573168112091, -3.3656969095840408, 1.6417591589969007,
    #     -18.924532105507726, 29.79957873535698, -0.2610146676643253
    # ]

    # 0.9
    # [
    #     0.5618453533609132, 2.3648011206042603, 2.83712132712444,
    #     -3.7989143226214894, -3.284626108222308, 7.181750443471694,
    #     -1.0507277890932947, -4.82427142749968, 8.153725324824535,
    #     -3.284626108222303, 3.2085626854529594, -7.1646404991797255
    # ]


table_name = 'ranks'


class Ranks(db.Model):
    __tablename__ = table_name

    id = db.Column(db.Integer, primary_key=True)
    Url = db.Column(db.String(), unique=True)
    redirected = db.Column(db.String())
    Error = db.Column(db.String())
    alexa = db.Column(db.Integer())
    wot_confidence = db.Column(db.Integer())
    wot_reputation = db.Column(db.Integer())
    alexa = db.Column(db.Integer())
    wot = db.Column(db.FLOAT())

    def __init__(self, data):
        for key in data.keys():
            setattr(self, key, data[key])

    def __repr__(self):
        return '<URL %r>' % self.Url


class Database(object):
    def __init__(self):
        engine = db.engine
        # check existence of table in database
        if not engine.dialect.has_table(engine, table_name):
            db.create_all()
            logger.info('Created table {}'.format(table_name))

        self.db = db
        self.ranks = Ranks

    def exist(self, url):

        if self.db.session.query(
                self.ranks).filter(self.ranks.Url == url).count():
            return True

        return False

    def getdb(self):
        return self.db

    def add(self, data):
        reg = self.ranks(data)
        self.db.session.add(reg)
        self.db.session.commit()

    def update(self, data):
        self.db.session.query(
            self.ranks
        ).filter(self.ranks.Url == data['Url']).update(data)
        self.db.session.commit()


if __name__ == "__main__":

    while True:
        print(
            '''
                w == calculateWeightage, wotSimilarity and alexaSimilarity
                bn = build Normalized_features matrix(Pickles under
                normlized directory)
                c = check corelation between features(Pickles under
                Webcred_normalized directory)
                b = build features matrix(Pickles under Webcred directory)
                for features
                    corelation heatmap
                s = check correlation between alexa and wot
            '''
        )
        action = raw_input("what action would you like to perform: ")

        if action == 's':

            # all urls
            link = open('data/essentials/urls.txt', 'r')
            links = link.readlines()
            link.close()
            wot = []
            alexa = []
            database = Database()
            for url in links:
                print(links.index(url))
                data = {}
                data['Url'] = url[:-2]
                try:
                    if not database.exist(url[:-2]):
                        web_of_trust = getWot(url[:-2])
                        data['alexa'] = getAlexarank(url[:-2])

                        data['wot_confidence'] = web_of_trust['confidence']
                        data['wot_reputation'] = web_of_trust['reputation']
                        data['wot'] = (
                            data['wot_reputation'] * data['wot_confidence'] /
                            10000.0
                        )

                except Exception:
                    # Get current system exception
                    ex_type, ex_value, ex_traceback = sys.exc_info()

                    # Extract unformatter stack traces as tuples
                    trace_back = traceback.extract_tb(ex_traceback)

                    # Format stacktrace
                    stack_trace = list()

                    for trace in trace_back:
                        stack_trace.append(
                            "File : %s , Line : %d, Func.Name : %s,"
                            " Message : %s" %
                            (trace[0], trace[1], trace[2], trace[3])
                        )

                    # print("Exception type : %s " % ex_type.__name__)
                    if ex_value.message != 'Response 202':
                        logger.debug(ex_value)
                        logger.debug(stack_trace)

                    data['Error'] = ex_value.message

                try:
                    database.add(data)
                except Exception:
                    database.getdb().session.rollback()

            # similarity = np.corrcoef(wot, alexa)[0][1]
            # print('similarity between alexa and wot = {}'.format(similarity))

        if action == 'w':
            # calculateWeightage()
            FeaturesName = [
                'domain', 'ads', 'imgratio', 'inlinks', 'misspelled',
                'pageloadtime', 'brokenlinks', 'hyperlinks', 'responsive',
                'lastmod', 'langcount', 'outlinks'
            ]
            # TODO genre classification is not done, so weightage can be biased
            genre = {
                'Article': FeaturesName,
            }

            weightage = {}
            alexaSimilarityScore = {}
            wotSimilarity = {}

            with open(r"data/analysis/normalized/Featureset.pickle",
                      "rb") as input_file:
                Featureset = cPickle.load(input_file)

            with open(r"data/analysis/normalized/alexaScoreSet.pickle",
                      "rb") as input_file:
                alexaScoreSet = cPickle.load(input_file)

            with open(r"data/analysis/normalized/wotScoreSet.pickle",
                      "rb") as input_file:
                wotScoreSet = cPickle.load(input_file)

            for k, v in genre.items():

                # numpy to pick particular columns based on
                # featuresname(v) required
                tempfeatureName = []

                # pick column id
                for web_of_trust in range(len(FeaturesName)):
                    if FeaturesName[web_of_trust] in v:
                        tempfeatureName.append(web_of_trust)

                # prepare required feature set
                tempFeatureSet = np.asarray(
                    Featureset, dtype='float'
                )[:, tempfeatureName]

                # adding one extra columns at last for k(misc. value to score)
                new_col = np.ones((len(tempFeatureSet), 1))
                idx = tempFeatureSet.shape[1]
                tempFeatureSet = np.insert(
                    tempFeatureSet, idx, np.transpose(new_col), axis=1
                )

                # adding one extra columns at last for alexaScore
                alexa = np.asarray(alexaScoreSet)
                idx = tempFeatureSet.shape[1]
                tempFeatureSet = np.insert(
                    tempFeatureSet, idx, np.transpose(alexa), axis=1
                )
                # pp = tempFeatureSet.tolist()
                # tt = pp
                # tt = random.shuffle(pp)
                # In loop of j, j can be 10
                #  n = total samples
                loop = 10
                n = tempFeatureSet.shape[0]
                kf = KFold(n_splits=loop)
                web_of_trust = 0
                Weigh = []
                alexaSimilarity = []
                wotSimilarity = []
                for train, test in kf.split(tempFeatureSet):
                    train_data = np.array(tempFeatureSet)[train]
                    test_data = np.array(tempFeatureSet)[test]
                    F = train_data[:, tempfeatureName + [-2]]
                    A = train_data[:, [-1]]

                    W = np.linalg.lstsq(F, A, rcond=None)[0]
                    W = np.transpose(W).tolist()[0]

                    score = np.matmul(test_data[:, tempfeatureName + [-2]],
                                      W).reshape(test_data.shape[0], 1)

                    AcorrScore = np.corrcoef(
                        np.transpose(alexaScoreSet), np.transpose(wotScoreSet)
                    ).tolist()[0][1]
                    # 49%
                    print AcorrScore

                    # TODO normalize wot value to wotScore
                    # TODO correlation between WOT and score

                    Weigh.append(W)
                    alexaSimilarity.append(AcorrScore)
                    # wotSimilarity.append()

                # get Weigh_avg(W), alexaSimilarity_avg, wotSimilarity_avg
                Weigh_avg = np.mean(Weigh, axis=0).tolist()
                alexaSimilarity_avg = np.mean(alexaSimilarity, axis=0).tolist()

                weightage[k] = Weigh_avg
                alexaSimilarityScore[k] = alexaSimilarity_avg
                # TODO wotSimilarity[k] = wotSimilarity_avg

            print weightage, alexaSimilarityScore

        elif action == 'bn':
            global totalSample
            global jsonData
            global Featureset
            Featureset = []
            alexaScoreSet = []
            wotScoreSet = []
            csv_filename = "WebcredNormalized.csv"

            f = open(csv_filename, 'r')
            data = f.readlines()
            pipe = Pipeline()
            # get json data
            jsonData = pipe.converttojson(data)
            totalSample = int(
                subprocess.check_output(['wc', '-l', csv_filename]
                                        ).split(' ')[0]
            ) - 1
            filterKeys = ['url', 'wot', 'cookie', 'redirected']
            FeaturesName = list((set(jsonData[0].keys()) - set(filterKeys)))
            count = 0
            tried = 0
            # building matrix wiht 1000 samples
            while True:
                tried += 1
                try:
                    sample = getjsonData()
                    featurevalue, alexaScore, wotScore = getFeatureValue([
                        sample
                    ], FeaturesName)
                    if checksimiliarData(featurevalue[0]):
                        # TODO do we need checksimiliarData here?
                        Featureset.append(featurevalue[0])
                        alexaScoreSet.append(alexaScore)
                        wotScoreSet.append(wotScore[0])
                        count += 1
                        print count
                except:
                    with open(r"data/analysis/normalized/Featureset.pickle",
                              "wb") as output_file:
                        cPickle.dump(Featureset, output_file)

                    with open(r"data/analysis/normalized/alexaScoreSet.pickle",
                              "wb") as output_score:
                        cPickle.dump(alexaScoreSet, output_score)

                    with open(r"data/analysis/normalized/wotScoreSet.pickle",
                              "wb") as output_score:
                        cPickle.dump(wotScoreSet, output_score)

                if tried == totalSample:

                    with open(r"data/analysis/normalized/Featureset.pickle",
                              "w") as output_file:
                        cPickle.dump(Featureset, output_file)

                    with open(r"data/analysis/normalized/alexaScoreSet.pickle",
                              "w") as output_score:
                        cPickle.dump(alexaScoreSet, output_score)

                    with open(r"data/analysis/normalized/wotScoreSet.pickle",
                              "w") as output_score:
                        cPickle.dump(wotScoreSet, output_score)

                    with open(r"data/analysis/normalized/Featureset.pickle",
                              "rb") as input_file:
                        e = cPickle.load(input_file)
                        print e
                        print len(e)

                    break

            # weightage = [
            #     0.5618453533609132, 2.3648011206042603, 2.83712132712444,
            #     -3.7989143226214894, -3.284626108222308, 7.181750443471694,
            #     -1.0507277890932947, -4.82427142749968, 8.153725324824535,
            #     -3.284626108222303, 3.2085626854529594, -7.1646404991797255
            # ]

            # features = np.array(Featureset)
            # # alexa = np.array(alexaScoreSet, dtype='float')
            # # wot = np.array(wotScoreSet, dtype='float')
            # weightage = np.transpose(np.array(weightage))
            # WebcredScore = np.matmul(features, weightage)
            #
            # with open(r"normlized/WebcredScore.pickle", "w") as output_file:
            #     cPickle.dump(WebcredScore, output_file)

        elif action == 'b':
            global totalSample
            global jsonData
            global Featureset
            Featureset = []
            alexaScoreSet = []
            wotScoreSet = []

            csv_filename = "../csvDataNew.csv"

            f = open(csv_filename, 'r')

            data = f.readlines()
            pipe = Pipeline()
            # get json data
            jsonData = pipe.converttojson(data)
            totalSample = int(
                subprocess.check_output(['wc', '-l', csv_filename]
                                        ).split(' ')[0]
            ) - 1
            filterKeys = ['url', 'wot', 'cookie', 'redirected']
            FeaturesName = list((set(jsonData[0].keys()) - set(filterKeys)))
            count = 0
            tried = 0

            # building matrix wiht 1000 samples
            while True:
                tried += 1
                try:
                    sample = getjsonData()
                    featurevalue, alexaScore, wotScore = getFeatures([
                        sample
                    ], FeaturesName)
                    # if checksimiliarData(featurevalue[0]):
                    # TODO do we need checksimiliarData here?
                    Featureset.append(featurevalue[0])
                    alexaScoreSet.append(alexaScore)
                    wotScoreSet.append(wotScore[0])
                    count += 1
                    print count
                except:
                    with open(r"Webcred_normalized/Featureset.pickle",
                              "wb") as output_file:
                        cPickle.dump(Featureset, output_file)

                    with open(r"Webcred_normalized/alexaScoreSet.pickle",
                              "wb") as output_score:
                        cPickle.dump(alexaScoreSet, output_score)

                    with open(r"Webcred_normalized/wotScoreSet.pickle",
                              "wb") as output_score:
                        cPickle.dump(wotScoreSet, output_score)

                if tried == totalSample:

                    with open(r"Webcred_normalized/Featureset.pickle",
                              "w") as output_file:
                        cPickle.dump(Featureset, output_file)

                    with open(r"Webcred_normalized/alexaScoreSet.pickle",
                              "w") as output_score:
                        cPickle.dump(alexaScoreSet, output_score)

                    with open(r"Webcred_normalized/wotScoreSet.pickle",
                              "w") as output_score:
                        cPickle.dump(wotScoreSet, output_score)

                    with open(r"Webcred_normalized/Featureset.pickle",
                              "rb") as input_file:
                        e = cPickle.load(input_file)
                        # print e
                        print len(e)

                    break

        elif action == "c":
            # with open(r"Webcred_normalized/Featureset.pickle", "rb")
            # as input_file:
            #     e = cPickle.load(input_file)
            #     # print e
            #     print len(e)

            FeaturesName = [
                'domain', 'ads', 'imgratio', 'inlinks', 'misspelled',
                'pageloadtime', 'brokenlinks', 'hyperlinks', 'responsive',
                'lastmod', 'langcount', 'outlinks'
            ]

            with open(r"Webcred_normalized/Featureset.pickle",
                      "rb") as input_file:
                e = cPickle.load(input_file)

            dataframe = pd.DataFrame(
                data=np.asarray(e)[0:, 0:],
                index=np.asarray(e)[0:, 0],
                columns=FeaturesName
            )
            corr = dataframe.corr()

            with open(r"Webcred_normalized/correlation.pickle",
                      "w") as output_score:
                cPickle.dump(corr, output_score)

            sns.heatmap(
                corr,
                xticklabels=FeaturesName,
                yticklabels=FeaturesName,
                cmap=sns.diverging_palette(220, 10, as_cmap=True)
            )
            pl.show()
