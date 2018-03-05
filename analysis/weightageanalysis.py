import sys
sys.path.insert(0,r'../')
from pipeline import Pipeline
from fnmatch import fnmatch
import json
import random
import subprocess

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
    for i in range(len(sampleSet)):
        temp = []
        for j in FeaturesName:
            temp.append(sampleSet[i].get(j))

        # row - feature values of individial sampels
        featurevalue.append(temp)
        # appending alexa score of each sample
        # 1000 is acting as a proportinality constant
        alexaScore.append("{:.15f}".format(1000/float(sampleSet[i].get('alexaRank'))))
    return featurevalue, alexaScore

import numpy as np

def getWeightage(Featureset, alexaScoreSet):
    global FeaturesName
    global repetetion

    while True:
        try:
            features = np.array(Featureset)
            alexa = np.array(alexaScoreSet, dtype='float')
            weightage = np.linalg.solve(features, alexa)
            break
        except:
            import pdb; pdb.set_trace()
            repetetion += 1
            print repetetion

            sample = getjsonData()
            featurevalue, alexaScore  = getFeatureValue([sample], FeaturesName)
            if checksimiliarData(featurevalue[0]):
                Featureset.append(featurevalue[0])
                alexaScoreSet.append(alexaScore)


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
            jsonData[var]['dataNoise'] = var
            return jsonData[var]

csv_filename = "WebcredNormalized.csv"

f = open(csv_filename, 'r')
data = f.readlines()
pipe = Pipeline()
# get json data
jsonData = pipe.converttojson(data)
totalSets = 10
# sets of possible weightages
weightage = {}
totalSample = int(subprocess.check_output(['wc', '-l', csv_filename]).split(' ')[0]) - 1
filterKeys = ['url', 'wot', 'cookie', 'redirected']
FeaturesName = list((set(jsonData[0].keys()) - set(filterKeys)))
FeaturesName.append('dataNoise')

Featureset = []
alexaScoreSet = []

for i in range(totalSets):
    weightage[i] = {}
    count = 0
    sampleSet = []
    # select sample sets
    while True:
        sample = getjsonData()
        featurevalue, alexaScore  = getFeatureValue([sample], FeaturesName)
        if checksimiliarData(featurevalue[0]):
            Featureset.append(featurevalue[0])
            alexaScoreSet.append(alexaScore)
            count += 1
            if count == len(FeaturesName):
                break

    # get weightage of individual feature
    weightage[i] = getWeightage(Featureset, alexaScoreSet)
    import pdb; pdb.set_trace()
