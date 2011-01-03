from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider

from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements

from plone.messaging.core import messageFactory as _
from plone.messaging.core.interfaces import IPubSubStorage
from plone.messaging.core.browser.pubsub import PublishToNodeForm
from plone.messaging.core.browser.pubsub import SubscribeToNodeForm
from plone.messaging.core.browser.pubsub import UnsubscribeFromNodeForm
from plone.messaging.core.browser.portlets.formwrapper import PortletFormView


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

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.createForms()

    def createForms(self):
        context = self.context.aq_inner
        publish_form = PublishToNodeForm(context, self.request, node=self.data.node)
        # Wrap a form in Plone view
        publish_view = PortletFormView(context, self.request)
        publish_view = publish_view.__of__(context) # Make sure acquisition chain is respected
        publish_view.form_instance = publish_form
        self.publish_form_wrapper = publish_view

        subscribe_form = None
        if self.isSubscribed:
            subscribe_form = UnsubscribeFromNodeForm(context, self.request, node=self.data.node)
        else:
            subscribe_form = SubscribeToNodeForm(context, self.request, node=self.data.node)
        # Wrap a form in Plone view
        subscribe_view = PortletFormView(context, self.request)
        subscribe_view = subscribe_view.__of__(context) # Make sure acquisition chain is respected
        subscribe_view.form_instance = subscribe_form
        self.subscribe_form_wrapper = subscribe_view

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return len(self.items()) or self.showPublishForm

    @property
    def title(self):
        return self.data.node

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

    @property
    def subscribers(self):
        storage = getUtility(IPubSubStorage)
        if self.data.node not in storage.subscriptions:
            return []
        return [user_id
                for user_id, state in
                storage.subscriptions[self.data.node].items()
                if state=='subscribed']

    @property
    def isSubscribed(self):
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            return False
        user = str(pm.getAuthenticatedMember())
        return user in self.subscribers

    @property
    def showSubscriptionForm(self):
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            return False
        return True


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
