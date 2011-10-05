import re
import json

from z3c.form import form
from z3c.form import field
from z3c.form import button

from zope import schema
from zope.component import getUtility
from zope.interface import Interface

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

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
        self.fullnames = dict()

    def fullname(self, author):
        if author in self.fullnames:
            return self.fullnames[author]
        else:
            member = self.mt.getMemberById(author)
            if member is None:
                return ''
            fullname = member.getProperty('fullname', None)
            if fullname is None:
                return ''
            self.fullnames[author] = fullname
            return fullname

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
        result = self.storage.node_items[node][:count]
        for index, item in enumerate(result):
            urls = re.findall(r'href=[\'"]?([^\'" >]+)', item['content'])
            if urls:
                item['urls'] = urls
            result[index] = item
        return result


class ContentTransform(BrowserView):

    def __call__(self, text):
        tr = getToolByName(self.context, 'portal_transforms')
        text = tr.convert('web_intelligent_plain_text_to_html', text).getData()
        result = {'text': text}
        return json.dumps(result)


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
