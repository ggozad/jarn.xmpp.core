import logging
import time

from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.component import queryUtility
from zope.component import queryAdapter

from jarn.xmpp.core import messageFactory as _
from jarn.xmpp.core.browser.formwrapper import WrappedFormView
from jarn.xmpp.core.browser.pubsub import SubscribeToNodeForm
from jarn.xmpp.core.browser.pubsub import UnsubscribeFromNodeForm
from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IPubSubable
from jarn.xmpp.core.interfaces import IXMPPUsers

logger = logging.getLogger('jarn.xmpp.core')


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
        client = queryUtility(IAdminClient)
        if client is None:
            logger.error('Could not load AdminClient')
            self.available = False
            return
        pm = getToolByName(self.context, 'portal_membership')
        user_id = pm.getAuthenticatedMember().getId()

        if user_id is None:
            self.available = False
            return

        if IPubSubable.providedBy(self.context):
            self.node = self.context.nodeId
        else:
            wrapper = queryAdapter(self.context, IPubSubable)
            if wrapper:
                self.node = wrapper.nodeId
            else:
                self.available = False
                return

        self.available = True
        self._subscribed = None

        settings = getUtility(IXMPPUsers)
        self.user_jid = settings.getUserJID(user_id)

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
