import time

from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility

from plone.messaging.core import messageFactory as _
from plone.messaging.core.browser.formwrapper import WrappedFormView
from plone.messaging.core.browser.pubsub import SubscribeToNodeForm
from plone.messaging.core.browser.pubsub import UnsubscribeFromNodeForm
from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.interfaces import IXMPPSettings


class ContentSubscriptionViewlet(ViewletBase):
    index = ViewPageTemplateFile('content_subscription.pt')

    def gotSubscriptions(self, result):
        node, subscriptions = result
        subscribers = [jid
                       for jid, state in subscriptions
                       if state=='subscribed']
        if self.user_jid in subscribers:
            self._subscribed = True
        else:
            self._subscribed = False


    def update(self):
        pm = getToolByName(self.context, 'portal_membership')
        user_id = pm.getAuthenticatedMember().getId()
        if user_id is None:
            self.available = False
            return
        self.available = True
        self._subscribed = None

        settings = getUtility(IXMPPSettings)
        client = getUtility(IAdminClient)
        self.user_jid = settings.getUserJID(user_id)
        self.node = self.context.UID()

        d = client.getSubscriptions(self.node)
        d.addCallback(self.gotSubscriptions)

        # XXX: EVIL: WE SHOILD NOT BLOCK
        # This should be ajaxified somehow.
        while self._subscribed is None:
            time.sleep(0.01)
        self.createForms()


    def createForms(self):
        form = None
        if self._subscribed:
            form = UnsubscribeFromNodeForm(self.context,
                                           self.request,
                                           node=self.node,
                                           user_jid=self.user_jid)
        else:
            form = SubscribeToNodeForm(self.context,
                                       self.request,
                                       node=self.node,
                                       user_jid=self.user_jid)

        # Wrap a form in Plone view
        form_view = WrappedFormView(self.context, self.request)
        # Make sure acquisition chain is respected
        form_view = form_view.__of__(self.context)
        form_view.form_instance = form
        self.form_wrapper = form_view
