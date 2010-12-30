from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import queryUtility
from zope.formlib import form
from zope.interface import implements

from plone.messaging.core.interfaces import IAdminClient

ITEMS = {}


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
        return len(self._data())

    @property
    def title(self):
        return self.data.node

    def items(self):
        return self._data()

    def _updateItems(self):

        def cb(result):
            ITEMS[self.data.node] = result

        pubsub = queryUtility(IAdminClient)
        if pubsub:
            d = None
            if self.data.node_type == 'leaf':
                d = pubsub.getNodeItems(self.data.node, self.data.count)
            else:
                d = pubsub.getCollectionNodeItems(self.data.node, self.data.count)
            d.addCallback(cb)
            return d

    def _data(self):
        self._updateItems()
        if self.data.node in ITEMS:
            return ITEMS[self.data.node]
        return []


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
