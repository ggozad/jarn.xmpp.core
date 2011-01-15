from plone.app.layout.viewlets.common import ViewletBase
from z3c.form import form
from z3c.form import field
from z3c.form import button
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.messaging.core import messageFactory as _
from plone.messaging.core.browser.portlets.formwrapper import PortletFormView
from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.interfaces import IPubSubStorage
from plone.messaging.core.interfaces import IXMPPSettings


class ChangeContentSubscriptionForm(form.Form):


    def __init__(self, context, request, node, user_jid, subscribe):
        super(ChangeContentSubscriptionForm, self).__init__(context, request)
        self.node = node
        self.user_jid = user_jid
        self.subscribe = subscribe

    @button.buttonAndHandler(_('Change subscription'), name='change_subscription')
    def change_subscribe_handler(self, action):

        client = getUtility(IAdminClient)

        def subscribe():
            def subscribeToNode(result):
                d = client.setSubscriptions(self.node, [(self.user_jid, 'subscribed')])
                return d
            d = client.createNode(self.node,
                options={'pubsub#collection': 'content'})
            d.addCallbacks(subscribeToNode, subscribeToNode)
            return d

        if self.subscribe:
            return subscribe()


class ContentSubscriptionViewlet(ViewletBase):
    index = ViewPageTemplateFile('content_subscription.pt')

    def update(self):
        pm = getToolByName(self.context, 'portal_membership')
        user_id = pm.getAuthenticatedMember().getId()
        if user_id is None:
            self.available = False
            return
        self.available = True

        settings = getUtility(IXMPPSettings)
        storage = getUtility(IPubSubStorage)
        client = getUtility(IAdminClient)
        self.user_jid = settings.getUserJID(user_id)
        self.node = self.context.UID()

        # If the node does not exist at all, then he is not subscribed.
        if self.node not in storage.leaf_nodes:
            self.subscribed = False
            self.createForms()
        self.createForms()
        return


    def createForms(self):
        form = None
        form = ChangeContentSubscriptionForm(self.context,
                                      self.request,
                                      node=self.node,
                                      user_jid=self.user_jid,
                                      subscribe=True)
        # Wrap a form in Plone view
        form_view = PortletFormView(self.context, self.request)
        # Make sure acquisition chain is respected
        form_view = form_view.__of__(self.context)
        form_view.form_instance = form
        self.form_wrapper = form_view
