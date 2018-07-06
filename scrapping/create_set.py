'''
Prepare set of sheets for genre analysis
One can set total sets
One can set total urls to be present in each set
'''

from random import randint
from urlparse import urlparse
from utils.urls import PatternMatching

import copy
import logging
import os
import shutil


logger = logging.getLogger('WEBCred.scrapping')
logging.basicConfig(level=logging.DEBUG)

max_sets = 15
common_entries = 3


# return max_sets number of sets with each set having maxentr_perset entries
def geturl(max_sets, len_entries, common_entries):

    print('preparing sets')
    sets = {}

    # so as to ensure each set has equal number of entries
    len_entries -= (len_entries * common_entries) % max_sets
    maxentr_perset = len_entries * common_entries / max_sets

    print('len_entries=', len_entries, 'maxentr_perset=', maxentr_perset)
    # prepare list of sets
    for i in range(0, len_entries - 30):
        # if i==len_entries-2:
        # print(i)
        orderSet = []
        for j in range(0, common_entries):
            while True:
                set_num = randint(0, max_sets - 1)
                if not sets.get(set_num, None):
                    sets[set_num] = []
                    break
                if len(sets[set_num]) < maxentr_perset:
                    if set_num not in orderSet:
                        break
            sets[set_num].append(i)
            orderSet.append(set_num)

    print('sets prepared')
    return sets


def getSheets(max_sets, common_entries, filterList):

    print('preparing sheets')

    urlFile = open('../data/essentials/urls.txt', 'r')
    urlList = urlFile.read().split()
    urlFile.close()

    urlList = filterdomain(urlList, filterList)[:5000]

    sets = geturl(max_sets, len(urlList), common_entries)

    for i in sets.keys():
        dump_filename = '../data/Genre_Labels/survey/Survey' + str(i) + '.txt'
        dump_file = open(dump_filename, 'a')
        for j in sets[i]:
            # url_set.append((urlList[j]))
            content = str(urlList[j]) + str('\n')
            dump_file.write(content)
        dump_file.close()

    print('sheets prepared')


def filterdomain(urlList=None, filterList=None):

    urls = copy.deepcopy(urlList)
    for i in urlList:
        netloc = urlparse(i).netloc
        if netloc in filterList:
            urls.remove(i)

        # prepare list of netlocs present in urls.text
        # if netloc not in locs:
        #     locs.append(netloc)
        #     netloc = str(netloc) + '\n'
        #     fi.write(netloc)

    return urls


# prepare filter list
def prepare_filterList():
    # every netloc startswith '#' should be filtered

    fi = open('../data/Genre_Labels/netlocs_0.txt', 'r')
    fi_data = fi.read().split()
    di = open('../data/Genre_Labels/filtered_netlocs.txt', 'a')
    pattern_matching = PatternMatching()
    keywords = [
        'news',
        'article',
        'blog',
        'timesofindia',
        'eweek',
        'nytimes',
        'wiki',
        'books',
        'developer',
        'docs',
        'documents',
        'journals',
        'scholar.google',
        'dblp',
        'ieee',
        'acm',
        'archive.org',
        'microsoft.com',
        'youtube',
        'facebook',
        'economist',
        'indiatimes',
        'twitter',
        'post',
        'tribune',
    ]
    pattern = pattern_matching.regexCompile(keywords)

    for netloc in fi_data:
        if netloc.startswith('#'):
            # print(netloc.split('#')[-1])
            netloc = str(netloc.split('#')[-1]) + '\n'
            di.write(netloc.split('#')[-1])
        else:
            match, matched = pattern_matching.regexMatch(
                pattern=pattern, data=str(netloc)
            )
            if match:
                netloc = str(netloc) + '\n'
                di.write(netloc)

    fi.close()
    di.close()


# remove existing filterList and survey sheets
try:
    os.remove('../data/Genre_Labels/filtered_netlocs.txt')
    survey_path = '../data/Genre_Labels/survey'
    if os.path.exists(survey_path):
        shutil.rmtree(survey_path)
    os.makedirs(survey_path)
except Exception as er:
    logger.debug(er)

# prepare filterList
prepare_filterList()

filterList = open('../data/Genre_Labels/filtered_netlocs.txt', 'r')
filterList_data = filterList.read().split()
filterList.close()
getSheets(max_sets, common_entries, filterList_data)
