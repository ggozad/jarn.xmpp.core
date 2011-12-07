import re
from urlparse import urlparse

from zope.component import getUtility

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from jarn.xmpp.core.interfaces import IPubSubStorage


class PubSubItem(BrowserView):

    item_template = ViewPageTemplateFile("pubsub_item.pt")

    def __init__(self, context, request):
        super(PubSubItem, self).__init__(context, request)
        self.mt = getToolByName(self.context, 'portal_membership')
        self.host = urlparse(getToolByName(self.context, 'portal_url')()).netloc
        self.storage = getUtility(IPubSubStorage)

    def fullname(self, author):
        member = self.mt.getMemberById(author)
        return member.getProperty('fullname', None)

    def isLeaf(self):
        return self._isLeaf

    def comments(self):
        return self.storage.getCommentsForItemId(self.item['id'])

    def __call__(self, item=None, isLeaf=False):
        if item is None:
            item = {
                'node': self.request.get('node'),
                'id': self.request.get('id'),
                'content': self.request.get('content'),
                'author': self.request.get('author'),
                'published': self.request.get('published'),
                'updated': self.request.get('updated'),
                'parent': self.request.get('parent')}

            if ('geolocation[latitude]' in self.request and
                'geolocation[longitude]' in self.request):
                item['geolocation'] = {
                    'latitude': self.request.get('geolocation[latitude]'),
                    'longitude': self.request.get('geolocation[longitude]')}
            if self.request.get('isLeaf') == 'false':
                isLeaf = False
        self.item = item
        self.isLeaf = isLeaf

        # Calculate magic links
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', item['content'])
        self.item['urls'] = [url
                             for url in urls
                             if url.startswith('http')
                             and urlparse(url).netloc != self.host]
        return self.item_template()


class PubSubItems(BrowserView):

    def __init__(self, context, request):
        super(PubSubItems, self).__init__(context, request)
        self.storage = getUtility(IPubSubStorage)

    def __call__(self, nodes, start=0, count=20):
        start = int(start)
        count = int(count)
        items = self.storage.itemsFromNodes(nodes, start=start, count=count)
        item_view = PubSubItem(self.context, self.request)
        html = '\n'.join(['<li class="pubsubItem">' + item_view(item) + "</li>"
                         for item in items]).encode('utf-8')
        return html


class PubSubFeedMixIn(object):

    def __init__(self, context):
        self.storage = getUtility(IPubSubStorage)
        if self.node in self.storage.leaf_nodes:
            self.nodeType = 'leaf'
        else:
            self.nodeType = 'collection'
        self.mt = getToolByName(self.context, 'portal_membership')

    def fullname(self, author):
        member = self.mt.getMemberById(author)
        if member:
            return member.getProperty('fullname', None)

    def postNode(self):
        """
        Checks whether the user can publish in this node. If it's a leaf
        node check whether the user is in the publishers. If it's a collection
        node check if there is a unique node for this collection where the
        user has publisher rights.
        """

        if self.mt.isAnonymousUser():
            return
        if self.node is None:
            return self.mt.getAuthenticatedMember().id
        user_id = self.mt.getAuthenticatedMember().id
        if self.nodeType == 'leaf':
            if user_id in self.storage.publishers[self.node]:
                return self.node
        else:
            publisher_nodes = [node
                               for node in self.storage.collections[self.node]
                               if user_id in self.storage.publishers[node]]
            if len(publisher_nodes) == 1:
                return publisher_nodes[0]

    def items(self, node=None, start=0, count=20):
        if node is None:
            node = self.node
        return self.storage.itemsFromNodes([node], start=start, count=count)


class PubSubFeed(BrowserView, PubSubFeedMixIn):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.node = request.get('node', None)
        PubSubFeedMixIn.__init__(self, context)
