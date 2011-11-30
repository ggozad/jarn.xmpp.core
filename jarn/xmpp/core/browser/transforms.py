import json
import re
import urllib2
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup

from plone.memoize import ram

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


@ram.cache(lambda method, url: url)
def getFavIcon(url):
    try:
        return urllib2.urlopen(url, timeout=5).read()
    except urllib2.URLError:
        return None


@ram.cache(lambda method, url: url)
def getURLData(url):

    try:
        doc = urllib2.urlopen(url, timeout=5).read()
    except urllib2.URLError:
        return None
    try:
        doc = BeautifulSoup(urllib2.urlopen(url).read())
    except UnicodeEncodeError:  # This is for links to files/images.
        doc = BeautifulSoup('')

    title = url
    description = u''

    # title
    if doc.title:
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
    host_url = urlparse(url)
    favicon_url = doc.first('link', rel='shortcut icon')
    if favicon_url:
        favicon_url = favicon_url.get('href')
        if not favicon_url.startswith('http'):
            favicon_url = host_url[0] + u'://' + host_url[1] + favicon_url
    else:
        favicon_url = host_url[0] + u'://' + host_url[1] + u'/favicon.ico'

    return {'title': title,
            'description': description,
            'favicon_url': favicon_url}


class MagicLinksView(BrowserView):

    def __call__(self, url):
        response = self.request.response
        response.setHeader('content-type', 'application/json')
        response.setBody(json.dumps(getURLData(url)))
        return response


class FavIconsView(BrowserView):

    def __call__(self, url):
        self.request.response.setHeader("Content-type", "image/x-icon")
        return getFavIcon(url)


class ContentTransform(BrowserView):

    def __call__(self, text):
        tr = getToolByName(self.context, 'portal_transforms')
        text = tr.convert('web_intelligent_plain_text_to_html', text).getData()
        user_pattern = re.compile(r'@[\w\.\-@]+')
        user_refs = user_pattern.findall(text)
        mt = getToolByName(self.context, 'portal_membership')
        portal_url = getToolByName(self.context, 'portal_url')()
        for user_ref in user_refs:
            user_id = user_ref[1:]
            if mt.getMemberById(user_id) is not None:
                link = '<a href="%s/pubsub-feed?node=%s">%s</a>' % \
                    (portal_url, user_id, user_ref)
                text = user_pattern.sub(link, text)

        response = self.request.response
        response.setHeader('content-type', 'application/json')
        response.setBody(json.dumps({'text': text}))
        return response
