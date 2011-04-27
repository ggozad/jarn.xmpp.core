from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements

from jarn.xmpp.core import messageFactory as _
from jarn.xmpp.core.interfaces import IPubSubStorage


class IPubSubNodePortlet(IPortletDataProvider):

    node = schema.TextLine(
        title=_(u'Node'),
        description=_(u'The pubsub node.'),
        required=True,
        default=u'')

    count = schema.Int(
        title=_(u'Number of items to display'),
        required=True,
        default=5)

    node_type = schema.Choice(
        title=_(u'Node type'),
        default='leaf',
        required=True,
        values=['collection', 'leaf'])


class Assignment(base.Assignment):
    implements(IPubSubNodePortlet)

    def __init__(self, node='', count=5, node_type='leaf'):
        self.node = node
        self.count = count
        self.node_type = node_type

    @property
    def title(self):
        return self.node


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('pubsubnode.pt')

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return len(self.items()) or self.showPublishForm

    @property
    def title(self):
        return self.data.node

    @property
    def node(self):
        return self.data.node

    @property
    def nodeType(self):
        return self.data.node_type

    def items(self):
        storage = getUtility(IPubSubStorage)
        if self.data.node not in storage.node_items:
            return []
        return storage.node_items[self.data.node][:self.data.count]

    @property
    def publishers(self):
        storage = getUtility(IPubSubStorage)
        if self.data.node not in storage.publishers:
            return []
        return storage.publishers[self.data.node]

    @property
    def showPublishForm(self):
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            return False
        user = str(pm.getAuthenticatedMember())
        return user in self.publishers


class AddForm(base.AddForm):
    form_fields = form.Fields(IPubSubNodePortlet)
    label = _(u"Add pubsub node Portlet")
    description = _(u"This portlet displays items from a pubsub node.")

    def create(self, data):
        return Assignment(node=data.get('node'),
                          count=data.get('count', 5),
                          node_type=data.get('node_type', 'leaf'))


class EditForm(base.EditForm):
    form_fields = form.Fields(IPubSubNodePortlet)
    label = _(u"Edit News Portlet")
    description = _(u"This portlet displays recent News Items.")
