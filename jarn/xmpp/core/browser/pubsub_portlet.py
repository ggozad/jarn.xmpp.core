from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.formlib import form
from zope.interface import implements

from jarn.xmpp.core import messageFactory as _
from jarn.xmpp.core.browser.pubsub import PubSubFeedMixIn


class IPubSubFeedPortlet(IPortletDataProvider):

    name = schema.TextLine(title=_(u'Title'), required=False)
    node = schema.ASCIILine(title=_(u'PubSub node'),
                            description=_(u"The name of the PubSub node displayed (typically a user id or 'people' in order to include all users). Leaving this empty, will populate the portlet with items from the users the user follows."),
                            required=False)


class Assignment(base.Assignment):
    implements(IPubSubFeedPortlet)

    def __init__(self, name='', node=''):
        self.name = name
        self.node = node

    @property
    def title(self):
        return self.name or 'PubSub feed'


class Renderer(base.Renderer, PubSubFeedMixIn):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        PubSubFeedMixIn.__init__(self, context)

    render = ViewPageTemplateFile('pubsub_portlet.pt')

    @property
    def title(self):
        return self.data.name

    @property
    def node(self):
        return self.data.node


class AddForm(base.AddForm):
    form_fields = form.Fields(IPubSubFeedPortlet)
    label = _(u"Add PubSub feed portlet")
    description = _(u"A portlet that renders the feed from a PubSub node.")

    def create(self, data):
        return Assignment(name=data.get('name', ''),
                          node=data.get('node', ''))


class EditForm(base.EditForm):
    form_fields = form.Fields(IPubSubFeedPortlet)
    label = _(u"Edit PubSub feed portlet")
    description = _(u"A portlet that renders the feed from a PubSub node.")
