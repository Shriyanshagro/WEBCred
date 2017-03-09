# _author_ = Shriyansh Agrawal

from bs4 import BeautifulSoup
import requests
import re
import nltk
from nltk.tag import pos_tag
from nltk.corpus import wordnet

import threading
global i,urls,check_hyperlink,check_ratio,check_link_ads,broken_links,cookie,language,spell_check,ads_list_flag,ads_list,iso_lang_flag
i=0
ads_list=[]
iso_lang_flag=0
ads_list_flag=0
cookie =1
check_ratio = 1
check_hyperlink=1
check_link_ads = 1
broken_links = 1
language = 1
spell_check = 1

urls = [
    "http://www.ffiec.gov/cybersecurity.htm",
    "https://www.openssl.org/docs/",
    "https://www.first.org",
    "https://securityblog.redhat.com/",
    "https://threatpost.com/",
    "http://www.sophos.com/en-us/security-news-trends",
    "https://blogs.rsa.com/",
    "https://apwg.org/",
    "http://www.cybersecurity.alabama.gov/",
    "http://www.symantec.com/connect/blogs/discover?community-id=691",
    "http://www.digitalthreat.net/2010/05/information-security-models-for-confidentiality-and-integrity/",
    "http://www.itsecurity.com/dictionary/all/",
    "https://www.schneier.com/cryptography.html",
    "http://www.iplocation.net/",
    "http://www.iso.org/iso/home/standards/management-standards/iso27001.htm",
    "https://www.kuppingercole.com/blog/kuppinger/information-rights-management-microsoft-gives-it-a-new-push-just-in-time-to-succeed",
    "http://www.cisco.com/c/en/us/td/docs/ios/sec_data_plane/configuration/guide/12_4/sec_data_plane_12_4_book.html",
    "https://www.freebsd.org/doc/handbook/index.html",
    "http://www.cgisecurity.com/owasp/html/index.html",
    "http://csrc.nist.gov/",
    "http://disa.mil/Network-Services/Data",
    "http://wiki.openssl.org/",
    "http://www.isg.rhul.ac.uk/tls/",
    "http://www.cryptographyworld.com/",
    "http://www.w3.org/TR/xmlsec-algorithms/",
    "http://niccs.us-cert.gov/glossary",
    "https://www.schneier.com/essays/",
    "http://securitywatch.pcmag.com/",
    "https://www.torproject.org/",
    "http://resources.infosecinstitute.com",
    "http://www.esslsecurity.com/",
    "http://stackoverflow.com/questions/tagged/security",
    "http://docs.saltstack.com/en/latest/",
    "https://saltthepass.com/#help-about",
    "http://crypto.stackexchange.com/",
    "http://www.biometrics.gov/",
    "http://www.biometricsinstitute.org/pages/types-of-biometrics.html",
    "http://support.microsoft.com/en-us/kb/246071",
    "http://www.garykessler.net/library/fsc_stego.html",
    "https://technet.microsoft.com/en-us/library/cc179103.aspx",
    "http://cs.stanford.edu/people/eroberts/courses/soco/projects/2000-01/risc/whatis/",
    "http://www.gammassl.co.uk/research/chinesewall.php",
    "http://www.softpanorama.org/Access_control/Security_models/",
    "http://www.openpgp.org/",
    "http://www.quadibloc.com/crypto/jscrypt.htm",
    "http://search.cpan.org/dist/Crypt-Loki97/Loki97.pm",
    "https://www.fastmail.com/help/technical/ssltlsstarttls.html",
    "http://www.ietf.org/rfc/rfc4880.txt",
    "https://tools.ietf.org/html/rfc2595",
    "http://www.pcmag.com/article2/0,2817,2407168,00.asp",
    "http://www.pcmag.com/article2/0,2817,2372364,00.asp",
    "https://technet.microsoft.com/en-us/library/hh994558%28v=ws.10%29.aspx",
    "https://technet.microsoft.com/en-us/library/hh994561(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/dd883248(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc755284(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc731416(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/ee706526(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc731004(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc731515(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc771395(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/jj865680(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/ff641731(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc753173(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc721923(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc731549(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc732077(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc772066(v=ws.10).aspx",
    "https://twitter.com/bruce_schneier",
    "http://www.isaccouncil.org/memberisacs.html",
    "https://tools.ietf.org/",
    "http://www.sqlsecurity.co",
    "https://technet.microsoft.com/en-us/library/security/dn610807.aspx",
    "http://searchsecurity.techtarget.in/",
    "http://www.bmc.com/support/security/",
    "https://portal.reisac.org/SitePages/Index.aspx",
    "http://www.infosecisland.com/",
    "http://www.infosecblog.org/",
    "https://isc.sans.edu/",
    "http://www.northropgrumman.com",
    "https://ics-cert.us-cert.gov/Standards-and-References",
    "http://www.information-age.com/",
    "https://europaysolutions.com/fraud-risk-management/fraud-prevention-suite/",
    "http://www.idrbt.ac.in/",
    "https://cve.mitre.org/",
    "http://www.ibm.com/developerworks/websphere/zones/was/security/",
    "https://cryptoworks21.uwaterloo.ca/cryptography",
    "http://www.fortinet.com",
    "https://crackstation.net/hashing-security.htm",
    "http://www.enterprisedb.com/docs/en/9.3/pg/sql-security-label.html",
    "http://www.arubanetworks.com/products/security/",
    "http://cyfy.org/tag/security/",
    "https://access.redhat.com/security/cve/",
    "http://www.crypto.com",
    "http://www2.schneider-electric.com/sites/corporate/en/support/cybersecurity/cybersecurity.page",
    "http://www.govinfosecurity.com",
    "http://www.wisegeek.com/what-is-tls.htm",
    "http://www.governmentsecurity.org/",
    "http://www.wired.com/category/threatlevel",
    "http://www.austinfosec.com",
    "http://www.wired.com/2014/11/hacker-lexicon-whats-dark-web/",
]


# urls = [
#     "https://www.first.org",
#     # "http://9gag.com/gif?ref=9nav"
#     # "http://www.ct.gov/dds/lib/dds/images/ddslogo.jpg"
# ]


def crawler(threadName):
    global urls,i,check_hyperlink,check_ratio,check_ads
    while i<len(urls):
        # print urls
        url = urls[i]
        # print "Started", i
        i+=1
        if url!="" and not ( url.startswith('http://') or url.startswith('https://') ):
            print "Nope"
        else:
            # need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
            hdr = {'User-Agent': 'Mozilla/5.0'}
            # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
            raw  = requests.get(url,headers=hdr)

            data = raw.text
            # to write page in a file
            # filename = url.split("/")[-1] + '.html'
            # with open(filename, 'wb') as f:
                # f.write(data.encode('utf-8'))
            # pass

            # Contact,Help,Email,Recommendations,Sitemap - check for hyperlink
            # idea ->  Scrap web>> parse using Soup>> find_all_lines(having='anchor tag', string=="contacts|Help|Email|Recommendations|Sitemap")>> check if href?>>
            if check_hyperlink==1:
                count = check_hyperlinks(url)
                print url,count

            # No of Ads links, Image to text ratio - check for img / text size
            if check_ratio==1:
                count = check_size_ratio(url)
                print url,count


            if check_link_ads==1:
                count = check_ads(url)
                print url,count


            if broken_links == 1:
                count  = check_brokenlinks(url)
                print url,count

            if cookie==1:
                check_cookie(url)
                print url,count

            if language==1:
                count = check_language(url)
                print url,count

            if spell_check==1:
                count = spell_checker(url)
                print url,count



            # print url

class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        crawler(self.name)

# limited to single thread otherwise it become asynchronous
for i in range(1):
    thread = myThread(1, i)
    thread.start()

def check_language(url):
    global iso_lang_flag
    if iso_lang_flag==0:
        # print "scanning array"
        iso = open("lang_iso.txt", "r")
        iso_array = iso.read().split(",")
        iso.close()
        iso_lang_flag=1
    # need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
    try:
        raw  = requests.get(url,headers=hdr)
    except:
        print "cannot extract raw of",url
        return

    count = 0
    done = {}
    data = raw.text
    soup = BeautifulSoup(data,"html.parser")
    tags = soup.find_all(href=True)
    for tag in tags:
        tag = str(tag)
        match = re.search("lang",tag)
        if match:
            # print tag
            tag = re.split(' |\"',tag)
            # print tag
            for code in  iso_array:
                if code in tag:
                    if not code in done.keys():
                        done[code]=1
                        # print code
                        count +=1

    # some uni-lang websites didn't mention lang tags
    if count==0:
        count = 1
    count = {"Total supported Lang":count}
    return count

def check_hyperlinks(url):
    # need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
    try:
        raw  = requests.get(url,headers=hdr)
    except:
        print "cannot extract raw of",url
        return

    data = raw.text
    soup = BeautifulSoup(data,"html.parser")

    data = {'contact':0,'email':0,'help':0,'recommend':0,'sitemap':0}
    for link in soup.find_all('a', string=re.compile("contact",re.I),href=True):
        links = link.get('href')
        if links:
            # print 'contact',
            data['contact']=1
            break

    for link in soup.find_all('a', string=re.compile("email",re.I),href=True):
        links = link.get('href')
        if links:
            # print 'email',
            data['email']=1
            break

    for link in soup.find_all('a', string=re.compile("help",re.I),href=True):
        links = link.get('href')
        if links:
            # print 'help',
            data['help']=1
            break

    for link in soup.find_all('a', string=re.compile("recommend",re.I),href=True):
        links = link.get('href')
        if links:
            # print 'recommend',
            data['recommend']=1
            break

    for link in soup.find_all('a', string=re.compile("sitemap",re.I),href=True):
        links = link.get('href')
        if links:
            # print 'sitemap',
            data['sitemap']=1
            break

    # print data,url
    return data

def check_size_ratio(url):
    # need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
    try:
        raw  = requests.get(url,headers=hdr)
    except:
        print "cannot extract raw of",url
        return

    ratio  = 'Not defined'
    total_img_size = int(0)
    txt_size = int(0)

    try:
        data = raw.text
        txt_size = int(raw.headers['Content-Length'])
    except:
        txt_size ='NA'
        print 'text size not available, page is dynamically created',
        return "NA"

    soup = BeautifulSoup(data,"html.parser")

    # total_img_size of images
    for link in soup.find_all('img',src=True):
        links = link.get('src')
        if links!="":
            if not links.startswith('http://') or links.startswith('https://'):
                links = url+links
                # print links

            hdr = {'User-Agent': 'Mozilla/5.0'}
            r  = requests.get(links,headers=hdr)
            try:
                size = r.headers['Content-Length']
            except:
                size=0
            finally:
                total_img_size += int(size)
            # print size,link

            try:
                ratio = total_img_size/txt_size
            except ValueError:
                ratio = 'Not defined'
    # print total_img_size,url,txt_size
    # print ratio
    ratio = {'Image:text Ratio':ratio}
    return ratio

# compiling all regular expressions of ads
def compile_ads():
    global ads_list_flag,ads_list
    if ads_list_flag==1:
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
        ! -----------------------General advert blocking filters-----------------------!
        ! *** easylist:easylist/easylist_general_block.txt ***
    '''
    easylist.close()
    for ads in ads_list_raw:
        # use of re.escape so that if your text has special characters(#,?,/,\,.), they won't be interpreted as such.
        ads = re.compile(re.escape(ads),re.X)
        ads_list.append(ads)
    ads_list_flag=1
    return

def check_ads(url):
    # get compiled list of ads regex
    compile_ads()
    # print ads_list


    hdr = {'User-Agent': 'Mozilla/5.0'}
    try:
        raw  = requests.get(url,headers=hdr)
    except:
        print "cannot extract raw of",url
        return

    data = raw.text
    soup = BeautifulSoup(data,'html.parser')
    count = 0

    for link in soup.find_all('a',href=True):
        # print link
        href = link.get('href')
        if  href.startswith('http://') or href.startswith('https://'):
            # print href
            href = str(href)

            for ads in ads_list:
                ads = str(ads)
                match = re.search(ads,href, re.X)
                # print ads
                if match:
                    print link
                    count += 1


    # if count!=0:
    #     print 'ad count=',count,url
    count = {"ad count":count}
    return count

def check_brokenlinks(url):
    # need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
    try:
        raw  = requests.get(url,headers=hdr)
    except:
        print "cannot extract raw of",url
        return

    data = raw.text
    soup = BeautifulSoup(data,'html.parser')
    count = 0
    total_links  = 0
    total_external_links=0

    for link in soup.find_all('a',href=True):
            href = link.get('href')
            total_links+=1
            if  href.startswith('http://') or href.startswith('https://'):
                total_external_links +=1
                # now only allowed for external links
                # header is mentioned because some robots don't allow bot to crawl their pages
                hdr = {'User-Agent': 'Mozilla/5.0'}
                # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
                try:
                    raw  = requests.head(url,headers=hdr)
                except:
                    print "cannot extract raw of",url
                    return
                raw  = ((str(raw).split(' ')[1]).split(']')[0])
                raw = int(raw.split('[')[1])
                # print  raw
                if raw>300:
                    #  success response code are only b/w 200-300
                    count +=1

    array = {'total_links':total_links,'total_external_links':total_external_links,'broken_links':broken_links}
    return  array

def check_cookie(url):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
    try:
        raw  = requests.head(url,headers=hdr)
    except:
        print "cannot extract raw of",url
        return
    cookies = raw.cookies
    # print cookies
    if cookies:
        # print 'yes website installs cookie on client system'
        return {'cookies':1}
    else:
        return {'cookies':0}

def spell_checker(url):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
    try:
        raw  = requests.get(url,headers=hdr)
    except:
        print "cannot extract raw of",url
        return

    # give text with html tags
    text = raw.text
    # gives only  text of HTML, i.e removes all HTML tags
    text = BeautifulSoup(text,"html.parser")
    text = text.get_text()
    # print raw,text
    tags =  [i[0] for i in pos_tag(text.split()) if i[1] != "NNP"]
    # print tags
    total_tags = len(tags)
    # count of undefined words
    count = 0
    for tag in tags:
        flag =1
        # print tag
        syns = wordnet.synsets(tag)
        try:
            defi = syns[0].definition()
            # print tag,"=",defi
        except:
            # print tag,"naa ho paayega"
            flag = 0

        if flag ==0:
            count+= 1

    array ={"Misspelled words":count,"total words":total_tags}
    return array
