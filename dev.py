# -*- coding: utf-8 -*-
'''
BELOW ARE THE WORKER FUNCTIONS TO COLLECTDATA
'''

from datetime import datetime
from random import randint
from utils import utils
from utils.pipeline import Pipeline
from utils.utils import Webcred

import json
import logging


logger = logging.getLogger('WEBCred.dev')
logging.basicConfig(level=logging.INFO)

# collectData, normalize, csv, json
work = 'collectData'
csv_filename = 'csvData.csv'
data = []

if work == 'collectData':
    # all urls
    link = open('APIs/urls.txt', 'r')
    links = link.readlines()
    link.close()

    # stitched request
    request = {
        'lastmod': 'true',
        'domain': 'true',
        'inlinks': 'false',
        'outlinks': 'false',
        'hyperlinks': 'true',
        'imgratio': 'true',
        'brokenlinks': 'false',
        'cookie': 'false',
        'langcount': 'true',
        'misspelled': 'true',
        'wot': 'true',
        'responsive': 'true',
        'pageloadtime': 'false',
        'ads': 'true',
    }

    now = datetime.now().time().isoformat()
    new_id = 'data.{}.{:04d}'.format(now, randint(0, 9999))
    new_id = 'DATA/json/' + str(new_id) + '.json'

    # while we recurring over urls
    # data_file = open(new_id, 'r')
    # tempData = data_file.readlines()
    # data_file.close()

    # count = len(links)
    # tempcounter = counter = len(tempData)
    for url in links[:10]:
        request['site'] = url[:-2]
        dt = Webcred()
        dt = dt.assess(request)
        data_file = open(new_id, 'a')
        data.append(dt)
        content = json.dumps(dt) + '\n'
        data_file.write(content)
        data_file.close()

if not data:
    file_ = 'DATA/json/data2.json'
    file_ = open(file_, 'r').read()
    file_ = file_.split('\n')

    import json

    truncate_char = 0
    for element in file_[:-1]:
        # print str(element[4:])
        try:
            data.append(json.loads(str(element[truncate_char:])))
        except ValueError:
            # it happens when len(data) changes to 100 from 99
            truncate_char += 1
            data.append(json.loads(str(element[truncate_char:])))

if work == 'normalize':
    # imgratio value are converted to int from float by multiple by 10^6
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
            'cookie': {
                'Yes': 0,
                'No': 1
            },
            'responsive': {
                'true': 1,
                'false': 0
            },
        },
        'not_sure': ['domain', 'langcount', 'lastmod'],
        'misc': ['hyperlinks'],
        'eval': ['wot']
    }

    for k in normalizeCategory['3'].items():
        norm = utils.Normalize(data, k)
        data = norm.normalize()
    # pdb.set_trace()

    for k in normalizeCategory['2'].items():
        # pdb.set_trace()
        norm = utils.Normalize(data, k)
        data = norm.factoise()

    for index in range(len(data)):
        if data[index].get(normalizeCategory['misc'][0]):
            tempData = data[index].get(normalizeCategory['misc'][0])
            del data[index][normalizeCategory['misc'][0]]
            for k, v in tempData.items():
                data[index][k] = v

    # print dt
    # pdb.set_trace()
    work = 'csv'
    csv_filename = 'normalized.csv'

if work == 'csv':
    # pdb.set_trace()
    # pdb.set_trace()
    pipe = Pipeline()
    csv = pipe.convertjson(data)
    # pdb.set_trace()
    f = open(csv_filename, 'w')
    f.write(csv)
    f.close()

if work == 'json':
    f = open(csv_filename, 'r')
    data = f.readlines()
    pipe = Pipeline()
    jsonData = pipe.converttojson(data)
    file_ = 'DATA/json/data.json'
    file_ = open(file_, 'a')
    for element in jsonData:
        element = json.dumps(element) + '\n'
        file_.write(element)
    file_.close()
