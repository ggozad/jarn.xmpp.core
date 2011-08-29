from BeautifulSoup import BeautifulSoup
import json
import urllib2
from urlparse import urlparse

from Products.Five.browser import BrowserView


class MagicLinksView(BrowserView):

    def __call__(self, url):
        try:
            doc = urllib2.urlopen(url).read()
        except urllib2.URLError:
            return None
        doc = BeautifulSoup(urllib2.urlopen(url).read())
        title = u''
        description = u''

        # title
        title = doc.title.string
        if not title:
            title = doc.first('meta', attrs={'name': 'title'})
            if title:
                title = title.get('content')

        # description
        description = doc.first('meta', attrs={'name': 'description'})
        if description:
            description = description.get('content')

        # Find favicon
        favicon_url = doc.first('link', rel='shortcut icon')
        if favicon_url:
            favicon_url = favicon_url.get('href')
        else:
            host_url = urlparse(url)
            favicon_url = host_url[0] + u'://' + host_url[1] + u'/favicon.ico'

        return json.dumps({
            'title': title,
            'description': description,
            'favicon_url': favicon_url})
