from app import Features
from kit.weightageanalysis import Ranks
from sqlalchemy.orm import sessionmaker
from utils.essentials import Base
from utils.essentials import Correlation
from utils.essentials import Database
from utils.essentials import db
from utils.webcred import apiList

import json
import logging


logger = logging.getLogger('similarity_score')

Session = sessionmaker()
Session.configure(bind=db.engine)
session = Session()


class FeaturesSet(Base):
    __tablename__ = 'feature_set'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(), unique=True)
    error = db.Column(db.String())
    dataset = db.Column(db.String())

    def __init__(self, data):
        for key in data.keys():
            setattr(self, key, data[key])

    def __repr__(self):
        return self.url


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def prepareDataset():

    # qu = ''
    # for key in apiList.keys():
    #     qu += '.filter(Features.' + key + ' != None)'
    #
    # qu += '.filter(Ranks.wot != None)'
    # qu += '.filter(Ranks.wot_confidence != None)'
    # qu += '.filter(Ranks.wot_reputation != None)'
    # qu += '.filter(Ranks.alexa != None)'

    # get instances when none of the entry in invalid
    query = session.query(Ranks, Features).filter(
        Ranks.url == Features.url
    ).filter(Ranks.error == None).filter(Features.error == None).filter(
        Features.domain != None
    ).filter(Features.brokenlinks != None).filter(
        Features.langcount != None
    ).filter(Features.ads != None).filter(Features.imgratio != None).filter(
        Features.inlinks != None
    ).filter(Features.misspelled != None).filter(
        Features.pageloadtime != None
    ).filter(Features.responsive != None
             ).filter(Features.hyperlinks != None).filter(
                 Features.lastmod != None
             ).filter(Features.outlinks != None
                      ).filter(Ranks.wot != None
                               ).filter(Ranks.wot_confidence != None
                                        ).filter(Ranks.wot_reputation != None
                                                 ).filter(
                                                     Ranks.alexa != None
                                                 )  # noqa
    query.count()
    features_name = apiList.keys()

    features = Database(Features)
    ranks = Database(Ranks)
    features_set = Database(FeaturesSet)

    # append columns form Ranks class
    for i in ranks.getcolumns():
        features_name.append(i)

    # remove redundant columns
    # TODO get integer values of columns
    features_name.remove('cookie')
    features_name.remove('site')
    features_name.remove('domain')
    features_name.remove('hyperlinks')
    features_name.remove('responsive')
    features_name.remove('id')
    features_name.remove('error')
    features_name.remove('redirected')

    for i in query.all():
        url = i[0]
        temp = merge_two_dicts(
            features.getdata('url', str(url)), ranks.getdata('url', str(url))
        )
        dt = {}
        for j in features_name:
            dt[j] = temp.get(j)

        dbData = {'url': str(url), 'dataset': json.dumps(dt)}

        features_set.update('url', str(url), dbData)

    logger.info('Prepared table {}'.format(features_set.gettablename()))

    return True


def getsimilarity():
    # get data from Class FeaturesSet
    database = Database(FeaturesSet)
    temp = database.getcolumndata('dataset')
    # clean data in list format
    features_name = json.loads(temp.all()[0][0]).keys()
    features_name.remove('url')
    corr = Correlation()
    for j in range(1, 6):
        dump = temp.all()[:(50 * j)]
        data = []
        for i in dump:
            joker = json.loads(i[0])
            joker['alexa'] = float(1.0 / joker['alexa'])
            del joker['url']
            values = joker.values()
            data.append(values)

        print(corr.getcorr(data, features_name))
        print()


if __name__ == "__main__":

    while True:
        print(
            '''
            p = prepareDataset
            s = similarity_score
            q = quit
        '''
        )

        action = raw_input("what action would you like to perform: ")

        if action == 'p':
            prepareDataset()
        elif action == 's':
            getsimilarity()
        elif action == 'q':
            print('babaye')
            break
