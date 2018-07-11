# _author_ = Shriyansh Agrawal
'''
This script scrap through raw(method: Get and Head) data of url,
and collect various information(as factors) for WebCred to assess
credibility of website

Dependencies and Requirement:
Collect Urls from urls.txt file
Require Phantom.Js and yslow.js(in working directory)
Currently throwing data in CSV file generated in Working
'''
from bs4 import BeautifulSoup
from nltk.corpus import wordnet
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from urlparse import urlparse

import json
import os
import re
import requests
import threading
import unicodedata
import urllib2


global i, urls, check_hyperlink, check_ratio, \
    check_link_ads, broken_links, cookie, language,\
    spell_check, ads_list_flag, ads_list, iso_lang_flag,\
    iso_array
i = 0
ads_list = []
iso_lang_flag = 0
ads_list_flag = 0

# flags to Factors
check_hyperlink = 1
check_ratio = 1
check_link_ads = 1
broken_links = 1
cookie = 1
language = 1
spell_check = 1

# read sead urls from file urls.txt
temp = open('urls.txt', 'r')
urls = temp.read().split()
temp.close()

# file to be edited
temp2 = open('data.csv', 'w')
string = "URL , " + "Contact , " + "Email , " +\
         "Help , " + "Recommend , " + "Sitemap , " +\
         "Text:Page Ratio , " + "Ad Count , " + "Broken Links , " +\
         'Cookies , ' + "Total supported Lang , " + "Misspelled words , " +\
         "Last Modified , " + "Domain , " + "Inlinks , " + "Oulinks , "
temp2.write(string + '\n')


# urls = [
# #     # "http://www.ffiec.gov/cybersecurity.htm",
# #     # "https://www.openssl.org/docs/",
# #     # "https://www.first.org",
# #     # "https://securityblog.redhat.com/",
# #     # 'https://threatpost.com/',
# #     # "http://www.sophos.com/en-us/security-news-trends",
#     # "https://blogs.rsa.com/",
# #     # "https://apwg.org/,"
# #     # "http://www.cybersecurity.alabama.gov/",
# ]
#
def check_hyperlinks(url):
    data = {
        'contact': 'Page NA',
        'email': 'Page NA',
        'help': 'Page NA',
        'recommend': 'Page NA',
        'sitemap': 'Page NA'
    }

    # need to specify header for kit otherwise some
    # websites doesn't allow bot to scrap
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this,
    # it asks the webserver for the headers without the body.
    try:
        raw = requests.get(url, headers=hdr)
    except:
        # print "cannot extract raw of",url
        return data

    data = raw.text
    soup = BeautifulSoup(data, "html.parser")

    data = {
        'contact': 'NA',
        'email': 'NA',
        'help': 'NA',
        'recommend': 'NA',
        'sitemap': 'NA'
    }
    for link in soup.find_all('a', string=re.compile("contact", re.I),
                              href=True):
        links = link.get('href')
        if links:
            # print 'contact',
            data['contact'] = 1
            break

    for link in soup.find_all('a', string=re.compile("email", re.I),
                              href=True):
        links = link.get('href')
        if links:
            # print 'email',
            data['email'] = 1
            break

    for link in soup.find_all('a', string=re.compile("help", re.I), href=True):
        links = link.get('href')
        if links:
            # print 'help',
            data['help'] = 1
            break

    for link in soup.find_all('a', string=re.compile("recommend", re.I),
                              href=True):
        links = link.get('href')
        if links:
            # print 'recommend',
            data['recommend'] = 1
            break

    for link in soup.find_all('a', string=re.compile("sitemap", re.I),
                              href=True):
        links = link.get('href')
        if links:
            # print 'sitemap',
            data['sitemap'] = 1
            break

    # print data,url

    return data


def check_language(url):
    global iso_lang_flag, iso_array
    if iso_lang_flag == 0:
        # print "scanning array"
        iso = open("APIs/lang_iso.txt", "r")
        iso_array = iso.read().split(",")
        iso.close()
        iso_lang_flag = 1

    count = {"Total supported Lang": "Page NA"}
    # need to specify header for kit otherwise
    #  some websites doesn't allow bot to scrap
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this,
    # it asks the webserver for the headers without the body.
    try:
        raw = requests.get(url, headers=hdr)
    except:
        # print "cannot extract raw of",url
        return count

    count = 0
    done = {}
    data = raw.text
    soup = BeautifulSoup(data, "html.parser")
    tags = soup.find_all(href=True)
    for tag in tags:
        tag = str(tag)
        match = re.search("lang", tag)
        if match:
            # print tag
            tag = re.split(' |\"', tag)
            # print tag
            for code in iso_array:
                if code in tag:
                    if code not \
                            in done.keys():
                        done[code] = 1
                        # print code
                        count += 1

    # some uni-lang websites didn't mention lang tags
    if count == 0:
        count = 1
    count = {"Total supported Lang": count}
    return count


def check_size_ratio(url):
    ratio = "Page NA"
    # need to specify header for kit
    # otherwise some websites doesn't allow bot to scrap
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this,
    # it asks the webserver for the headers without the body.
    try:
        raw = requests.get(url, headers=hdr)
    except:
        # print "cannot extract raw of",url
        return {'Text:Page Ratio': ratio}

    total_img_size = int(0)
    txt_size = int(0)

    try:
        data = raw.text
        txt_size = int(raw.headers['Content-Length'])
    except:
        # txt_size ='NA'
        # print 'text size not available, page is dynamically created',
        return {'Text:Page Ratio': ratio}

    soup = BeautifulSoup(data, "html.parser")

    # total_img_size of images
    for link in soup.find_all('img', src=True):
        links = link.get('src')
        if links != "":
            if not links.startswith('http://') or links.startswith('https://'):
                links = url + links
                # print links

            hdr = {'User-Agent': 'Mozilla/5.0'}
            try:
                r = requests.get(links, headers=hdr)
                size = r.headers['Content-Length']
            except:
                size = 0
            finally:
                total_img_size += int(size)
            # print size,link

            try:
                ratio = str(txt_size) + '/' + str(total_img_size + txt_size)
            except ValueError:
                ratio = 'Page Na'
    # print total_img_size,url,txt_size
    # print ratio
    ratio = {'Text:Page Ratio': ratio}
    return ratio


# compiling all regular expressions of ads
def compile_ads():
    global ads_list_flag, ads_list
    if ads_list_flag == 1:
        return
    # print "compiling ads regex"
    easylist = open("easylist.txt", "r")
    ads_list_raw = easylist.read().split()
    '''
        [Adblock Plus 2.0]
        ! Version: 201702151753
        ! Title: EasyList
        ! Last modified: 15 Feb 2017 17:53 UTC
        ! Expires: 4 days (update frequency)
        ! Homepage: https://easylist.to/
        ! Licence: https://easylist.to/pages/licence.html
        !
        ! Please report any unblocked adverts or problems
        ! in the forums (https://forums.lanik.us/)
        ! or via e-mail (easylist.subscription@gmail.com).
        ! GitHub issues: https://github.com/easylist/easylist/issues
        ! GitHub pull requests: https://github.com/easylist/easylist/pulls
        !
        ! -----------------------General advert blocking filters!
        ! *** easylist:easylist/easylist_general_block.txt ***
    '''
    easylist.close()
    for ads in ads_list_raw:
        # use of re.escape so that
        # if your text has special characters(#,?,/,\,.),
        #  they won't be interpreted as such.
        ads = re.compile(re.escape(ads), re.X)
        ads_list.append(ads)
    ads_list_flag = 1
    return


def check_ads(url):
    # get compiled list of ads regex
    compile_ads()
    # print ads_list

    count = {"ad count": "Page NA"}
    hdr = {'User-Agent': 'Mozilla/5.0'}
    try:
        raw = requests.get(url, headers=hdr)
    except:
        # print "cannot extract raw of",url
        return count

    data = raw.text
    soup = BeautifulSoup(data, 'html.parser')
    count = 0

    for link in soup.find_all('a', href=True):
        # print link
        href = link.get('href')
        if href.startswith('http://') or href.startswith('https://'):
            # print href
            try:
                href = str(href)
            except:
                return {"ad count": "Page NA"}

            for ads in ads_list:
                # ads = str(ads)
                # print ads
                match = ads.search(href)
                # print ads
                if match:
                    # print href
                    count += 1
                    break

    # if count!=0:
    #     print 'ad count=',count,url
    count = {"ad count": count}
    return count


def check_brokenlinks(url):
    array = {
        'total_links': "Page NA",
        'total_external_links': "Page NA",
        'broken_links': "Page NA"
    }
    # need to specify header for kit otherwise
    # some websites doesn't allow bot to scrap
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this,
    # it asks the webserver for the headers without the body.
    try:
        raw = requests.get(url, headers=hdr)
    except:
        # print "cannot extract raw of",url
        return array

    data = raw.text
    soup = BeautifulSoup(data, 'html.parser')
    count = 0
    total_links = 0
    total_external_links = 0

    for link in soup.find_all('a', href=True):
        href = link.get('href')
        total_links += 1
        if href.startswith('http://') or href.startswith('https://'):
            total_external_links += 1
            # now only allowed for external links
            # header is mentioned because
            # some robots don't allow bot to crawl their pages
            hdr = {'User-Agent': 'Mozilla/5.0'}
            # You should use the HEAD Request for this,
            # it asks the webserver for the headers without the body.
            try:
                raw = requests.head(url, headers=hdr)
            except:
                # print "cannot extract raw of",url
                return {
                    'total_links': "Page NA",
                    'total_external_links': "Page NA",
                    'broken_links': "Page NA"
                }
            raw = ((str(raw).split(' ')[1]).split(']')[0])
            raw = int(raw.split('[')[1])
            # print  raw
            if raw > 300:
                #  success response code are only b/w 200-300
                count += 1

    array = {
        'total_links': total_links,
        'total_external_links': total_external_links,
        'broken_links': broken_links
    }
    return array


def check_cookie(url):

    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this,
    # it asks the webserver for the headers without the body.
    try:
        raw = requests.head(url, headers=hdr)
    except:
        # print "cannot extract raw of",url
        return {'cookies': "Page NA"}
    cookies = raw.cookies
    # print cookies
    if cookies:
        # print 'yes website installs cookie on client system'
        return {'cookies': 1}
    else:
        return {'cookies': 0}


def spell_checker(url):
    array = {"Misspelled words": "Page NA", "total words": "Page NA"}
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this,
    # it asks the webserver for the headers without the body.
    try:
        raw = requests.get(url, headers=hdr)
    except:
        # print "cannot extract raw of",url
        return array

    # give text with html tags
    text = raw.text
    # gives only  text of HTML, i.e removes all HTML tags
    text = BeautifulSoup(text, "html.parser")
    text = text.get_text()
    # print raw,text
    excluded_tags = [
        'NNP', 'NNPS', 'SYM', 'CD', 'IN', 'TO', 'CC', 'LS', 'POS', '(', ')',
        ':', 'EX', 'FW', 'RP'
    ]
    # text  = re.split(' {?}| ?:[ -]|\,|\.* |\\n|!|\?|\)|-
    # |\(|!|;|\[|\]|\"|',text)
    text = word_tokenize(text)
    tags = []
    # print text
    for texts in text:
        i = pos_tag(texts.split())
        i = i[0]
        if i[1] not in excluded_tags and i[0] != i[1]:
            tags.append(i[0])
            # print i
    # tags = [i[0] for i in pos_tag(text.split()) if
    # i[1] not in excluded_tags]

    total_tags = len(tags)
    # count of undefined words
    count = 0
    for tag in tags:
        flag = 1
        # print tag
        syns = wordnet.synsets(tag)
        try:
            syns[0].definition()
            # print tag,"=",defi
        except:
            # print tag,"naa ho paayega"
            flag = 0

        if flag == 0:
            count += 1
            # print tag

    # print count
    array = {"Misspelled words": count, "total words": total_tags}
    # print array,len(text)
    return array


def getDate(url):
    # print urllib2.urlopen(url).info().getdate('last-modified')
    if urllib2.urlopen(url).code / 100 < 4:
        lastmod = str(urllib2.urlopen(url).info().getdate('last-modified'))
        if lastmod == 'None':
            lastmod = 'cr' + str(urllib2.urlopen(url).info().getdate('date'))
    else:
        try:
            response = urllib2.urlopen(
                "http://archive.org/wayback/available?url=" + url
            )
            data = json.load(response)['archived_snapshots']['closest'
                                                             ]['timestamp']
            lastmod = 'wr' + '(' + data[0:4] + ', ' + data[4:6] + ', ' + data[
                6:8
            ] + ', ' + data[8:10] + ', ' + data[10:12] + ', ' + data[12:14
                                                                     ] + ')'
        except:
            lastmod = 'NA'
    return lastmod


def getDomain(url):
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain


def getLinks(url):
    outlinks = []
    try:
        html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    except:
        inlinks = "Page NA"
        outlinks = "Page NA"
        return inlinks, outlinks

    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a', href=True):
        outlinks.append(link['href'])
    API_KEY = 'AIzaSyB5L_ZZZKg9OeOVLQpmfOiqaHZMg8r9FCc'
    r = requests.get(
        'https://www.googleapis.com/customsearch/v1?key=' + API_KEY +
        '&cx=017576662512468239146:omuauf_lfve&q=link:' + url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    txt = r.text
    txt = unicodedata.normalize('NFKD', txt).encode('ascii', 'ignore')
    for line in txt.splitlines():
        if "totalResults" in line:
            break
    try:
        inlinks = int(re.sub("[^0-9]", "", line))
    except:
        inlinks = 0
    outlinks = len(outlinks)
    return inlinks, outlinks


'''install phantomjs and have yslow.js in the path to execute'''


def pageloadtime(url):
    response = os.popen('phantomjs yslow.js --info basic ' + url).read()
    response = json.loads(response.split('\n')[1])
    return (int)(response['lt']) / ((int)(response['r']))


def crawler(threadName):
    global urls, i, check_hyperlink, check_ratio, check_ads
    while i < len(urls):
        # print urls
        url = urls[i]
        # print "Started", i
        i += 1
        if url != "" and (not (url.startswith('http://')
                               or url.startswith('https://'))):
            print "Nope"
        else:

            # need to specify header for kit otherwise
            #  some websites doesn't allow bot to scrap
            # hdr = {'User-Agent': 'Mozilla/5.0'}
            # You should use the HEAD Request for this,
            # it asks the webserver for the headers without the body.
            # raw  = requests.get(url,headers=hdr)

            # data = raw.text
            # to write page in a file
            # filename = url.split("/")[-1] + '.html'
            # with open(filename, 'wb') as f:
            # f.write(data.encode('utf-8'))
            # pass

            string = str(url)
            # Contact,Help,Email,Recommendations,Sitemap - check for hyperlink
            # idea ->  Scrap web>> parse using Soup>>
            # find_all_lines(having='anchor tag',
            # string=="contacts|Help|Email|Recommendations|Sitemap")>>
            #  check if href?>>
            if check_hyperlink == 1:
                count = check_hyperlinks(url)
                # print url,count
                string += " , " + str(count['contact'])
                string += " , " + str(count['email'])
                string += " , " + str(count['help'])
                string += " , " + str(count['recommend'])
                string += " , " + str(count['sitemap'])

                # string+= " , " + str(count)

            # No of Ads links, Text Page text ratio - check for img / text size
            if check_ratio == 1:
                count = check_size_ratio(url)
                # print url,count
                string += " , " + str(count['Text:Page Ratio'])

            if check_link_ads == 1:
                count = check_ads(url)
                # print url,count
                string += " , " + str(count["ad count"])

            if broken_links == 1:
                count = check_brokenlinks(url)
                # print url,count
                string += " , " + str(count['broken_links'])

            if cookie == 1:
                count = check_cookie(url)
                # print url,count
                string += " , " + str(count['cookies'])

            if language == 1:
                count = check_language(url)
                # print url,count
                string += " , " + str(count["Total supported Lang"])

            if spell_check == 1:
                count = spell_checker(url)
                # print url,count
                string += " , " + str(count["Misspelled words"])

            # lastmod=getDate(url)
            # string+= " , " + str(lastmod)
            domain = getDomain(url)
            string += " , " + str(domain)
            inlinks, outlinks = getLinks(url)
            string += " , " + str(inlinks)
            string += " , " + str(outlinks)
            # plt=pageloadtime(url)
            # string+= " , " + str(plt)

            print string
            temp2.write(string + '\n')

            # print url


class myThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        crawler(self.name)
        temp2.close()


# limited to single thread otherwise it become asynchronous
for i in range(1):
    thread = myThread(1, i)
    thread.start()
