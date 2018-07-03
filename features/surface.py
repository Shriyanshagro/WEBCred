from ast import literal_eval
from datetime import datetime
from nltk.corpus import wordnet
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from utils.utils import MyThread
from utils.utils import Urlattributes
from utils.utils import WebcredError

import ast
import json
import os
import re
import validators


def funcBrokenllinks(url):
    # pdb.set_trace()
    result = None
    if url:
        try:
            uri = Urlattributes(url)
            resp = uri.geturllibreq()
            if not resp.code / 100 < 4:
                result = 'True'
            uri.freemem()
        except WebcredError:
            result = 'True'
        except:
            result = 'True'
    return result


def funcImgratio(url):
    size = 0
    try:
        size = url.getsize()
        # print url.geturl(), size
    except WebcredError:
        pass
    except:
        pass
    return size


def getWot(url):

    result = (
        "http://api.mywot.com/0.4/public_link_json2?hosts=" + url.geturl() +
        "/&callback=&key=d60fa334759ae377ceb9cd679dfa22aec57ed998"
    )
    try:
        # pdb.set_trace()
        uri = Urlattributes(result)
        raw = uri.gettext()
        result = literal_eval(raw[1:-2])
        return list(result.values())[0]['0']
    except WebcredError as e:
        raise WebcredError(e.message)
    except:
        return 'NA'


def getResponsive(url):
    result = (
        "http://tools.mercenie.com/responsive-check/api/?format=json&url=" +
        url.geturl()
    )
    try:
        # pdb.set_trace()
        uri = Urlattributes(result)
        result = ast.literal_eval(re.search('({.+})', uri.gettext()).group(0))
        return result['responsive']
    except WebcredError as e:
        raise WebcredError(e.message)
    except:
        # pdb.set_trace()
        return 'Info not NA'


def getHyperlinks(url, attributes):

    try:
        soup = url.getsoup()
    except WebcredError as e:
        raise WebcredError(e.message)
    except:
        raise WebcredError('Error while parsing Page')

    data = {}
    for element in attributes:
        data[element] = 0
        '''
        Using wn.synset('dog.n.1').lemma_names is the correct way to access the
        synonyms of a sense. It's because a word has many senses and it's more
        appropriate to list synonyms of a particular meaning/sense
        '''
        syn = wordnet.synsets(element)
        if syn:
            syn = wordnet.synsets(element)[0].lemma_names()
        # pdb.set_trace()
        lookup = {'header': 0, 'footer': 0}
        percentage = 10

        # looking for element in lookup
        for tags in lookup.keys():
            if soup.find_all(tags, None) and not data[element]:
                lookup[tags] = 1

                text = soup.find_all(tags, None)
                text = text[0].find_all('a', href=True)
                for ss in syn:
                    for index in text:
                        if data[element]:
                            break
                        try:
                            pattern = url.getPatternObj().regexCompile([ss])
                            match, matched = url.getPatternObj().regexMatch(
                                pattern=pattern, data=str(index)
                            )
                        except:
                            # pdb.set_trace()
                            raise WebcredError('Error with patternmatching')

                        if match:
                            data[element] = 1
                            # print element, matched
                            break

        # pdb.set_trace()
        '''if lookup tags are not found, then we check in upper and lower
        percentage of text'''
        for tags in lookup.keys():
            # pdb.set_trace()
            if not data[element] and not lookup[tags]:
                text = soup.find_all('a', href=True)
                # text = url.gettext()
                if tags == 'header':
                    text = text[:(len(text) * (percentage / 100))]

                elif tags == 'footer':
                    text = text[(len(text) * ((100 - percentage) / 100)):]

                for ss in syn:
                    for index in text:
                        if data[element]:
                            break
                        try:
                            pattern = url.getPatternObj().regexCompile([ss])
                            match, matched = url.getPatternObj().regexMatch(
                                pattern=pattern, data=str(index)
                            )
                        except:
                            # pdb.set_trace()
                            raise WebcredError('Error with patternmatching')
                        if match:
                            data[element] = 1
                            break

                # such cases where syn is []
                # wordnet has no synonyms for sitemap
                if not data[element]:
                    for index in text:
                        if data[element]:
                            break
                        try:
                            pattern = url.getPatternObj().regexCompile([
                                element
                            ])
                            match, matched = url.getPatternObj().regexMatch(
                                pattern=pattern, data=str(index)
                            )
                        except:
                            # pdb.set_trace()
                            raise WebcredError('Error with patternmatching')
                        if match:
                            data[element] = 1
                            break

    # pdb.set_trace()
    return data


def getLangcount(url):
    '''
    idea is to find pattern 'lang' in tags and then iso_lang code in those tags
    there are 2 possible patterns, to match iso_lang -
        ="en"
        =en
    '''

    try:
        soup = url.getsoup()
    except WebcredError as e:
        raise WebcredError(e.message)

    count = 0
    matched = []
    tags = soup.find_all(href=True)

    for tag in tags:

        tag = str(tag)
        match = re.search("lang", tag, re.I)

        if match:
            pattern = url.patternMatching.getIsoPattern()
            match, pattern = url.getPatternObj().regexMatch(pattern, tag)
            if match:

                # iso_pattern = ="iso"|=iso
                pattern = pattern.split('=')[-1]

                if pattern.startswith('"'):
                    pattern = pattern.split('"')[1]

                if pattern not in matched:
                    matched.append(pattern)
                    count += 1
                # pdb.set_trace()

    # some uni-lang websites didn't mention lang tags
    if count == 0:
        count = 1
    return count


def getImgratio(url):

    total_img_size = 0
    threads = []

    try:
        text_size = url.getsize()
    except WebcredError as e:
        return e.message

    soup = url.getsoup()

    # total_img_size of images
    for link in soup.find_all('img', src=True):
        uri = link.get('src', None)
        if not uri.startswith('http://') and not uri.startswith('https://'):
            uri = url.geturl() + uri

        if validators.url(uri):
            try:
                uri = Urlattributes(uri)
                t = MyThread(Method='funcImgratio', Name='Imgratio', Url=uri)
                t.start()
                threads.append(t)
            except WebcredError as e:
                # even if particular image is not accessible, we don't mind it
                pass

    for t in threads:
        t.join()
        t.freemem()
        size = t.getResult()
        if isinstance(size, int):
            total_img_size += size
        # print total_img_size

    try:
        total_size = total_img_size + text_size
        ratio = float(text_size) / total_size
        # print ratio, text_size, total_size
    except ValueError:
        raise WebcredError('Error in fetching images')

    return ratio


def getAds(url):
    try:
        soup = url.getsoup()
    except WebcredError as e:
        raise WebcredError(e.message)

    count = 0

    for link in soup.find_all('a', href=True):
        href = str(link.get('href'))
        if href.startswith('http://') or href.startswith('https://'):

            # pdb.set_trace()
            try:
                pattern = url.getPatternObj().getAdsPattern()
                match, pattern = url.getPatternObj().regexMatch(pattern, href)
            except WebcredError as e:
                raise WebcredError(e.message)
            if match:
                count += 1
                # print pattern, href

    return count


def getCookie(url):
    try:
        header = url.getheader()
    except WebcredError as e:
        raise WebcredError(e.message)

    try:
        pattern = url.getPatternObj().regexCompile(['cookie'])
    except WebcredError as e:
        raise WebcredError(e.message)
    for key in header.keys():
        try:
            match, matched = url.getPatternObj().regexMatch(
                pattern=pattern, data=key
            )
        except WebcredError as e:
            # pdb.set_trace()
            raise WebcredError(e.message)

        if match:
            # print key
            return 'Yes'

    return 'No'


def getMisspelled(url):
    # pdb.set_trace()
    text = url.gettext()

    excluded_tags = [
        'NNP', 'NNPS', 'SYM', 'CD', 'IN', 'TO', 'CC', 'LS', 'POS', '(', ')',
        ':', 'EX', 'FW', 'RP'
    ]

    try:
        text = word_tokenize(text)
    except UnicodeDecodeError:
        text = unicode(text, 'utf-8')
        text = word_tokenize(text)

    tags = []
    # print text
    for texts in text:
        i = pos_tag(texts.split())
        i = i[0]
        if i[1] not in excluded_tags and i[0] != i[1]:
            tags.append(i[0])

    # count of undefined words
    count = 0
    for tag in tags:
        try:
            syns = wordnet.synsets(str(tag))
            if syns:
                # [0] is in the closest sense
                syns[0].definition()
        except Exception:
            # pdb.set_trace()
            count += 1

    # pdb.set_trace()
    return count


def getDate(url):
    # pdb.set_trace()
    try:
        resp = url.geturllibreq()
    except WebcredError as e:
        raise WebcredError(e.message)
    # pdb.set_trace()
    if resp.code / 100 < 4:
        try:
            lastmod = str(resp.info().getdate('last-modified'))
            if lastmod == 'None':
                # some page has key 'date' for same
                lastmod = str(resp.info().getdate('date'))
            lastmod = datetime.strptime(
                str(lastmod), '(%Y, %m, %d, %H, %M, %S, %f, %W, %U)'
            )
            lastmod = lastmod.isoformat()
        except:
            raise WebcredError('Error with Requests')
    else:
        try:
            # fetching data form archive
            uri = "http://archive.org/wayback/available?url=" + url.geturl()
            uri = Urlattributes(uri)
            resp = uri.geturllibreq()
            data = (
                json.load(resp)['archived_snapshots']['closest']['timestamp']
            )
            lastmod = (
                'wr' + '(' + data[0:4] + ', ' + data[4:6] + ', ' + data[6:8] +
                ', ' + data[8:10] + ', ' + data[10:12] + ', ' + data[12:14] +
                ')'
            )
        except WebcredError as e:
            raise WebcredError(e.message)
        except:
            raise WebcredError(
                'Error in fetching last-modified date from archive'
            )
    return lastmod


def getDomain(url):
    # a fascinating use of .format() syntax
    try:
        domain = url.getdomain()
    except:
        raise WebcredError('urlparsing error')
    return domain


def getBrokenlinks(url):
    broken_links = 0
    threads = []
    try:
        soup = url.getsoup()
    except WebcredError as e:
        raise WebcredError(e.message)
    except:
        raise WebcredError('Url is broken')

    for link in soup.find_all('a', href=True):
        uri = link.get('href')

        # TODO should it inlude inner links as well?
        if not uri.startswith('http://') and not uri.startswith('https://'):
            uri = url.geturl() + uri

        if validators.url(uri):
            t = MyThread(
                Method='funcBrokenllinks', Name='brokenlinks', Url=uri
            )
            t.start()
            threads.append(t)

    for t in threads:
        # pdb.set_trace()
        t.join()
        # t.freemem()
        if t.getResult():
            broken_links += 1

    return broken_links


def getOutlinks(url):
    outlinks = 0

    try:
        soup = url.getsoup()
    except WebcredError as e:
        raise WebcredError(e.message)
    except:
        # pdb.set_trace()
        raise WebcredError('Url is broken')

    for link in soup.find_all('a', href=True):
        uri = link.get('href')
        if uri.startswith('https://') or uri.startswith('http://'):
            try:
                uri = Urlattributes(uri)
                if url.getnetloc() != uri.getnetloc():
                    outlinks += 1
                    # uri = uri.geturl()
                    # list_.append(uri)
            except WebcredError as e:
                pass
                # raise WebcredError(e.message)
    # pdb.set_trace()
    # f = open('outlinks.text','w')
    # f.write(links_)
    return outlinks


# total web-pages which redirect/mention url
def getInlinks(url):

    API_KEY = 'AIzaSyB5L_ZZZKg9OeOVLQpmfOiqaHZMg8r9FCc'
    try:
        uri = (
            'https://www.googleapis.com/customsearch/v1?key=' + API_KEY +
            '&cx=017576662512468239146:omuauf_lfve&q=link:' +
            url.getoriginalurl()
        )
        uri = Urlattributes(uri)
        txt = uri.gettext()
        # except WebcredError as e:
        # 	raise WebcredError(e.message)
    except:
        raise WebcredError('GoogleApi limit is exceeded')

    # txt=unicodedata.normalize('NFKD', txt).encode('ascii','ignore')

    for line in txt.splitlines():
        if "totalResults" in line:
            break
    try:
        inlinks = int(re.sub("[^0-9]", "", line))
    except:
        raise WebcredError('Inlinks are hard to get for this URL')

    return inlinks


'''install phantomjs and have yslow.js in the path to execute'''


def getPageloadtime(url):
    # pdb.set_trace()
    try:
        response = os.popen('phantomjs yslow.js --info basic ' +
                            url.geturl()).read()
        response = json.loads(response.split('\n')[1])
        return (int)(response['lt']) / ((int)(response['r']))
    except ValueError:
        raise WebcredError('FAIL to load')
    except:
        raise WebcredError('Fatal error')


def dimapi(url, api):
    # REVIEW
    try:
        # pdb.set_trace()
        uri = Urlattributes(api)
        raw = uri.gettext()
        # result = literal_eval(raw[1:-2])
        return raw
    except WebcredError:
        raise WebcredError("Give valid API")
    except:
        return 'NA'
