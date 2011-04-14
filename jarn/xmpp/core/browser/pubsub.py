from z3c.form import form
from z3c.form import field
from z3c.form import button

from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.component import getUtility
from zope.interface import Interface

from jarn.xmpp.core import messageFactory as _
from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IXMPPUsers
from jarn.xmpp.core.utils.pubsub import publishItemToNode


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
        self.node = node or request.get('node', None)

    def updateWidgets(self):
        form.Form.updateWidgets(self)

        if self.node:
            # Hide fields which we don't want to bother the user with
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

    def __init__(self, context, request, node=None, user_jid=None):
        super(SubscribeUnsubscribeForm, self).__init__(context, request)
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


class SubscribeToNodeForm(SubscribeUnsubscribeForm):

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


class UnsubscribeFromNodeForm(SubscribeUnsubscribeForm):

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
