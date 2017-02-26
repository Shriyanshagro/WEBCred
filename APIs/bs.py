html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""

import httplib2
from bs4 import BeautifulSoup, SoupStrainer


# http = httplib2.Http(proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_HTTP_NO_TUNNEL, 'proxy.iiit.ac.in', 8080,))
# status, response = http.request('http://www.nytimes.com')
#
# for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
#     if link.has_attr('href'):
#         print link['href']

soup = BeautifulSoup(html_doc, 'html.parser')

# text = (soup.get_text())
print soup.find_all('a', string="Elsie")
