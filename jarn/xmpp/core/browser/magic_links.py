import html5lib
import json
import urllib2
from urlparse import urlparse

from Products.Five.browser import BrowserView


class MagicLinksView(BrowserView):

    def __call__(self, url):
        parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("dom"))
        doc = parser.parse(urllib2.urlopen(url).read())
        title = u''
        description = u''
        favicon_url = u'/favicon.ico'

        # Find title, description
        meta_elems = doc.getElementsByTagName('meta')
        for elem in meta_elems:
            name = elem.getAttribute('name').lower()
            if name == u'title':
                title = elem.getAttribute('content')
            elif name == u'description':
                description = elem.getAttribute('content')

        title_elems = doc.getElementsByTagName('title')
        if title_elems:
            for child in title_elems[0].childNodes:
                title = title + child.toxml()

        # Find favicon
        link_elems = doc.getElementsByTagName('link')
        for elem in link_elems:
            if elem.getAttribute('rel') == u'shortcut icon':
                favicon_url = elem.getAttribute('href')
        host_url = urlparse(url)
        favicon_url = host_url[0] + '://' + host_url[1] + favicon_url

        return json.dumps({
            'title': title,
            'description': description,
            'favicon_url': favicon_url})
