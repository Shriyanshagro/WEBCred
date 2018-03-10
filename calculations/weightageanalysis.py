# sum of all weightage== 1, misc. genre == 0.1

import sys
sys.path.insert(0,r'../')
from pipeline import Pipeline
from fnmatch import fnmatch
import json
import random
import subprocess
import cPickle

global totalSample
global jsonData
global Featureset
global alexaScoreSet
global FeaturesName
global repetetion
import pandas as pd
import matplotlib.pyplot as pl
import seaborn as sns
repetetion = 0
# filter data
# data = json dict
def filter(data):
    errorString= ['*Error*', '*+++*', '*NA*', '*limit*']
    for i in errorString:
        if fnmatch(json.dumps(data),i):
            return False
    return True

import urllib, sys, bs4
# if rank not available, 999999999 wil be returned
def getAlexarank(url):
    try:
        rank =  bs4.BeautifulSoup(urllib.urlopen("http://data.alexa.com/data?cli=10&dat=s&url="+ url).read(), "xml").find("REACH")['RANK']
    except:
        rank = 999999999
    return rank

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
        alexaScore.append("{:.15f}".format(1000/float(sampleSet[i].get('alexaRank'))))
        wotScore.append(sampleSet[i].get('wot'))
    return featurevalue, alexaScore, wotScore

from datetime import datetime as dt
def getFeatures(sampleSet, FeaturesName):

    # get feature Values out of dict
    featurevalue = []
    alexaScore = []
    wotScore = []
    for i in range(len(sampleSet)):
        temp = []
        for j in FeaturesName:
            if j=='hyperlinks':
                sum_hyperlinks_attributes = 0
                tempData = sampleSet[i].get(j)
                try:
                    for k,v in tempData.items():
                        sum_hyperlinks_attributes += v
                except:
                    # TimeOut error clause
                    pass
                finally:
                    temp.append(sum_hyperlinks_attributes)
                    # data[index][it[0]] = sum_hyperlinks_attributes
            elif j=='responsive':
                tempData = sampleSet[i].get(j)
                try:
                    if tempData=='false':
                        tempData = 0
                    elif tempData=='true':
                        tempData = 1
                except:
                    # TimeOut error clause
                    pass
                finally:
                    temp.append(tempData)
            elif j=='lastmod':
                lastmod = dt.strptime(sampleSet[i].get(j), '%Y-%m-%dT%H:%M:%S')
                dayDiffernce = (dt.now() - lastmod).days
                temp.append(dayDiffernce)
            elif j=='domain':
                domain = {'gov':1, 'org':0, 'edu':1,
                   'com':0, 'net':0, 'else':-1}
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
        alexaScore.append("{:.15f}".format(1000/float(sampleSet[i].get('alexaRank'))))
        wotScore.append(sampleSet[i].get('wot'))

    return featurevalue, alexaScore, wotScore

import numpy as np

def getNoise(length):
    temp = []
    for i in range(0, length):
        # temp.append("{:.15f}".format(random.uniform(0, 0.00005)))
        temp.append(random.uniform(-1,1))
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
            alexaScoreSet.append(["{:.15f}".format(random.uniform(0, 10)/1000)])
            # print Featureset

            # sample = getjsonData()
            # featurevalue, alexaScore  = getFeatureValue([sample], FeaturesName)
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
                jsonData[var]['alexaRank'] = getAlexarank(jsonData[var].get('redirected'))
            else:
                jsonData[var]['alexaRank'] = getAlexarank(jsonData[var].get('url'))
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
    totalSample = int(subprocess.check_output(['wc', '-l', csv_filename]).split(' ')[0]) - 1
    filterKeys = ['url', 'wot', 'cookie', 'redirected']
    FeaturesName = list((set(jsonData[0].keys()) - set(filterKeys)))

    Featureset = []
    alexaScoreSet = []

    genre = {}

    for i in range(totalSets):
        count = 0
        sampleSet = []
        # select sample sets
        while True:
            sample = getjsonData()
            featurevalue, alexaScore, wotScore  = getFeatureValue([sample], FeaturesName)
            if checksimiliarData(featurevalue[0]):
                Featureset.append(featurevalue[0])
                alexaScoreSet.append(alexaScore)
                count += 1
                if count == len(FeaturesName)-1:
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
    # [2.2236760132294826, -7.914215741530812, 13.670499590165207, 0.6997838591507087, -18.92453210550777, -2.1201375082255307, 3.47573168112091, -3.3656969095840408, 1.6417591589969007, -18.924532105507726, 29.79957873535698, -0.2610146676643253]

    # 0.9
    # [0.5618453533609132, 2.3648011206042603, 2.83712132712444, -3.7989143226214894, -3.284626108222308, 7.181750443471694, -1.0507277890932947, -4.82427142749968, 8.153725324824535, -3.284626108222303, 3.2085626854529594, -7.1646404991797255]

if __name__ == "__main__":

    print '''
    w == calculateWeightage
    bn = build Normalized_features matrix(Pickles under normlized directory)
    c = check corelation between features(Pickles under Webcred directory)
    b = build features matrix(Pickles under Webcred directory) for features
        corelation heatmap
    '''
    action = raw_input("what action would you like to perform?")


    if action == 'w':
        # calculateWeightage()
        FeaturesName = ['domain', 'ads', 'imgratio', 'inlinks', 'misspelled', 'pageloadtime', 'brokenlinks', 'hyperlinks', 'responsive', 'lastmod', 'langcount', 'outlinks']
        genre = {'Article': FeaturesName,}

        weightage = {}
        alexaSimilarity = {}
        wotSimilarity = {}


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
        totalSample = int(subprocess.check_output(['wc', '-l', csv_filename]).split(' ')[0]) - 1
        filterKeys = ['url', 'wot', 'cookie', 'redirected']
        FeaturesName = list((set(jsonData[0].keys()) - set(filterKeys)))
        count = 0
        tried = 0
        # building matrix wiht 1000 samples
        while True:
            tried += 1
            try:
                sample = getjsonData()
                featurevalue, alexaScore, wotScore  = getFeatureValue([sample], FeaturesName)
                if checksimiliarData(featurevalue[0]):
                    # TODO do we need checksimiliarData here?
                    Featureset.append(featurevalue[0])
                    alexaScoreSet.append(alexaScore)
                    wotScoreSet.append(wotScore[0])
                    count += 1
                    print count
            except:
                with open(r"normalized/Featureset.pickle", "wb") as output_file:
                    cPickle.dump(Featureset, output_file)

                with open(r"normalized/alexaScoreSet.pickle", "wb") as output_score:
                    cPickle.dump(alexaScoreSet, output_score)

                with open(r"normalized/wotScoreSet.pickle", "wb") as output_score:
                    cPickle.dump(wotScoreSet, output_score)

            if tried == totalSample:

                with open(r"normalized/Featureset.pickle", "w") as output_file:
                    cPickle.dump(Featureset, output_file)

                with open(r"normalized/alexaScoreSet.pickle", "w") as output_score:
                    cPickle.dump(alexaScoreSet, output_score)

                with open(r"normalized/wotScoreSet.pickle", "w") as output_score:
                    cPickle.dump(wotScoreSet, output_score)

                with open(r"normalized/Featureset.pickle", "rb") as input_file:
                    e = cPickle.load(input_file)
                    print e
                    print len(e)


                break

        # weightage = [0.5618453533609132, 2.3648011206042603, 2.83712132712444, -3.7989143226214894, -3.284626108222308, 7.181750443471694, -1.0507277890932947, -4.82427142749968, 8.153725324824535, -3.284626108222303, 3.2085626854529594, -7.1646404991797255]

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
        totalSample = int(subprocess.check_output(['wc', '-l', csv_filename]).split(' ')[0]) - 1
        filterKeys = ['url', 'wot', 'cookie', 'redirected']
        FeaturesName = list((set(jsonData[0].keys()) - set(filterKeys)))
        count = 0
        tried = 0

        # building matrix wiht 1000 samples
        while True:
            tried += 1
            try:
                sample = getjsonData()
                featurevalue, alexaScore, wotScore  = getFeatures([sample], FeaturesName)
                # if checksimiliarData(featurevalue[0]):
                # TODO do we need checksimiliarData here?
                Featureset.append(featurevalue[0])
                alexaScoreSet.append(alexaScore)
                wotScoreSet.append(wotScore[0])
                count += 1
                print count
            except:
                with open(r"Webcred_normalized/Featureset.pickle", "wb") as output_file:
                    cPickle.dump(Featureset, output_file)

                with open(r"Webcred_normalized/alexaScoreSet.pickle", "wb") as output_score:
                    cPickle.dump(alexaScoreSet, output_score)

                with open(r"Webcred_normalized/wotScoreSet.pickle", "wb") as output_score:
                    cPickle.dump(wotScoreSet, output_score)

            if tried == totalSample:

                with open(r"Webcred_normalized/Featureset.pickle", "w") as output_file:
                    cPickle.dump(Featureset, output_file)

                with open(r"Webcred_normalized/alexaScoreSet.pickle", "w") as output_score:
                    cPickle.dump(alexaScoreSet, output_score)

                with open(r"Webcred_normalized/wotScoreSet.pickle", "w") as output_score:
                    cPickle.dump(wotScoreSet, output_score)

                with open(r"Webcred_normalized/Featureset.pickle", "rb") as input_file:
                    e = cPickle.load(input_file)
                    # print e
                    print len(e)

                break

    elif action == "c":
        # with open(r"Webcred_normalized/Featureset.pickle", "rb") as input_file:
        #     e = cPickle.load(input_file)
        #     # print e
        #     print len(e)

        FeaturesName = ['domain', 'ads', 'imgratio', 'inlinks', 'misspelled', 'pageloadtime', 'brokenlinks', 'hyperlinks', 'responsive', 'lastmod', 'langcount', 'outlinks']

        dataframe = pd.DataFrame(data=np.asarray(e)[0:,0:], index=np.asarray(e)[0:,0],columns=FeaturesName)
        corr = dataframe.corr()

        with open(r"Webcred_normalized/correlation.pickle", "w") as output_score:
            cPickle.dump(corr, output_score)


        sns.heatmap(corr, xticklabels=FeaturesName, yticklabels= FeaturesName, cmap=sns.diverging_palette(220, 10, as_cmap=True))
        pl.show()
