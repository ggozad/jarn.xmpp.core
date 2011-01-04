from z3c.form import form
from z3c.form import field
from z3c.form import button

from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.component import getUtility
from zope.interface import Interface

from plone.messaging.core import messageFactory as _
from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.pubsub_utils import publishItemToNode


class IPublishToNode(Interface):

    node = schema.ASCIILine(title=_(u'Node'),
                          required=True)

    message = schema.Text(title=_(u'Message'),
                          required=True)


class ISubscribeToNode(Interface):

    node = schema.ASCIILine(title=_(u'Node'),
                            required=True)


class PublishToNodeForm(form.Form):

    fields = field.Fields(IPublishToNode)
    label = _("Post message")
    ignoreContext = True

    def __init__(self, context, request, node=None):
        super(PublishToNodeForm, self).__init__(context, request)
        self.node = node

    def updateWidgets(self):
        """ Make sure that return URL is not visible to the user.
        """
        form.Form.updateWidgets(self)

        if self.node:
            # Hide fields which we don't want to bother user with
            self.widgets["node"].value = self.node
            self.widgets["node"].mode = form.interfaces.HIDDEN_MODE

    @button.buttonAndHandler(_('Post'), name='publish_message')
    def publish(self, action):
        data, errors = self.extractData()
        if errors:
            return
        node = data['node']
        message = data['message']
        transforms = getToolByName(self.context, 'portal_transforms')
        message = transforms.convert('web_intelligent_plain_text_to_html',
                                     message).getData()
        pm = getToolByName(self.context, 'portal_membership')
        user = str(pm.getAuthenticatedMember())
        publishItemToNode(node, message, user)
        return self.request.response.redirect(self.context.absolute_url())


class SubscribeUnsubscribeForm(form.Form):

    fields = field.Fields(ISubscribeToNode)
    ignoreContext = True

    def __init__(self, context, request, node=None):
        super(SubscribeUnsubscribeForm, self).__init__(context, request)
        self.node = node

    def updateWidgets(self):
        """ Make sure that return URL is not visible to the user.
        """
        form.Form.updateWidgets(self)
        if self.node:
            # Hide fields which we don't want to bother user with
            self.widgets["node"].value = self.node
            self.widgets["node"].mode = form.interfaces.HIDDEN_MODE


class SubscribeToNodeForm(SubscribeUnsubscribeForm):

    label = _("Subscribe")

    @button.buttonAndHandler(_('Subscribe'), name='subscribe_node')
    def subscribe_handler(self, action):
        data, errors = self.extractData()
        if errors:
            return
        node = data['node']
        pm = getToolByName(self.context, 'portal_membership')
        user_id = str(pm.getAuthenticatedMember())
        settings = getUtility(IXMPPSettings)
        client = getUtility(IAdminClient)
        user_jid = settings.getUserJID(user_id)

        d = client.setSubscriptions(node, [(user_jid, 'subscribed')])
        return d


class UnsubscribeFromNodeForm(SubscribeUnsubscribeForm):

    label = _("Unsubscribe")

    @button.buttonAndHandler(_('Unsubscribe'), name='unsubscribe_node')
    def unsubscribe_handler(self, action):
        data, errors = self.extractData()
        if errors:
            return
        node = data['node']
        pm = getToolByName(self.context, 'portal_membership')
        user_id = str(pm.getAuthenticatedMember())
        settings = getUtility(IXMPPSettings)
        client = getUtility(IAdminClient)
        user_jid = settings.getUserJID(user_id)

        d = client.setSubscriptions(node, [(user_jid, 'none')])
        return d
