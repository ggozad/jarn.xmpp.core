import re
import json
from urlparse import urlparse

from z3c.form import form
from z3c.form import field
from z3c.form import button

from zope import schema
from zope.component import getUtility
from zope.interface import Interface

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from jarn.xmpp.core import messageFactory as _
from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IXMPPUsers
from jarn.xmpp.core.interfaces import IPubSubStorage


class IPublishToNode(Interface):

    node = schema.ASCIILine(title=_(u'Node'),
                          required=True)

    message = schema.TextLine(title=_(u'Message'),
                          required=True)


class ISubscribeToNode(Interface):

    node = schema.ASCIILine(title=_(u'Node'),
                            required=True)


class PubSubFeed(BrowserView):

    def __init__(self, context, request):
        super(PubSubFeed, self).__init__(context, request)
        self.storage = getUtility(IPubSubStorage)
        self.node = request.get('node', None)
        if self.node in self.storage.leaf_nodes:
            self.nodeType = 'leaf'
        else:
            self.nodeType = 'collection'
        self.mt = getToolByName(self.context, 'portal_membership')

    def fullname(self, author):
        member = self.mt.getMemberById(author)
        return member.getProperty('fullname', None)

    def canPublish(self):
        """
        Checks whether the user can publish in this node. If it's a leaf
        node check whether the user is in the publishers. If it's a collection
        node check if there is a unique node for this collection where the
        user has publisher rights.
        """

        if self.mt.isAnonymousUser() or self.node is None:
            return
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

    def items(self, node=None, count=100):
        if node is None:
            node = self.node
        if node not in self.storage.node_items:
            return []
        return self.storage.node_items[node][:count]


class PubSubItem(BrowserView):

    item_template = ViewPageTemplateFile("pubsub_item.pt")

    def fullname(self, author):
        member = self.mt.getMemberById(author)
        return member.getProperty('fullname', None)

    def isLeaf(self):
        return self._isLeaf

    def __call__(self, item=None, isLeaf=True):
        if item is None:
            item = {
                'node': self.request.get('node'),
                'item_id': self.request.get('item_id'),
                'content': self.request.get('content'),
                'author': self.request.get('author'),
                'published': self.request.get('published'),
                'updated': self.request.get('updated'),
            }
            if self.request.get('isLeaf') == 'false':
                isLeaf = False
        self.item = item
        self.isLeaf = isLeaf
        self.mt = getToolByName(self.context, 'portal_membership')

        # Calculate magic links
        portal_url_netloc = urlparse(
            getToolByName(self.context, 'portal_url')()).netloc
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', item['content'])
        self.item['urls'] = [url
                             for url in urls
                             if urlparse(url).netloc != portal_url_netloc]
        return self.item_template()


class SubscribeUnsubscribeBase(form.Form):

    fields = field.Fields(ISubscribeToNode)
    ignoreContext = True

    def __init__(self, context, request, node=None, user_jid=None):
        super(SubscribeUnsubscribeBase, self).__init__(context, request)
        self.node = node
        if user_jid is not None:
            self.user_jid = user_jid
        else:
            pm = getToolByName(self.context, 'portal_membership')
            user_id = pm.getAuthenticatedMember().getId()
            xmpp_users = getUtility(IXMPPUsers)
            self.user_jid = xmpp_users.getUserJID(user_id)

    def updateWidgets(self):
        form.Form.updateWidgets(self)
        if self.node:
            # Hide fields which we don't want to bother user with
            self.widgets["node"].value = self.node
            self.widgets["node"].mode = form.interfaces.HIDDEN_MODE


class SubscribeToNode(SubscribeUnsubscribeBase):

    label = _("Subscribe")

    @button.buttonAndHandler(_('Subscribe'), name='subscribe_node')
    def subscribe_handler(self, action):
        data, errors = self.extractData()
        if errors:
            return
        node = data['node']
        client = getUtility(IAdminClient)
        d = client.setSubscriptions(node, [(self.user_jid, 'subscribed')])
        return d


class UnsubscribeFromNode(SubscribeUnsubscribeBase):

    label = _("Unsubscribe")

    @button.buttonAndHandler(_('Unsubscribe'), name='unsubscribe_node')
    def unsubscribe_handler(self, action):
        data, errors = self.extractData()
        if errors:
            return
        node = data['node']
        client = getUtility(IAdminClient)
        d = client.setSubscriptions(node, [(self.user_jid, 'none')])
        return d
