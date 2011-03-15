import logging

from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.events import IPrincipalCreatedEvent
from Products.PluggableAuthService.interfaces.events import IPrincipalDeletedEvent
from zope.component import adapter
from zope.component import getUtility

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IPubSubStorage
from jarn.xmpp.core.interfaces import IXMPPUsers
from jarn.xmpp.core.utils.users import setupPrincipal
from jarn.xmpp.core.utils.users import deletePrincipal

logger = logging.getLogger('jarn.xmpp.core')


@adapter(IPrincipalCreatedEvent)
def onUserCreation(event):
    """Create a jabber account for new user.
    """
    client = getUtility(IAdminClient)
    settings = getUtility(IXMPPUsers)
    storage = getUtility(IPubSubStorage)
    principal = event.principal
    mtool = getToolByName(principal, 'portal_membership')

    principal_id = principal.getUserId()
    principal_jid = settings.getUserJID(principal_id)
    principal_pass = settings.getUserPassword(principal_id)
    members_jids = [settings.getUserJID(member.getUserId())
                    for member in mtool.listMembers()]

    storage.leaf_nodes.append(principal_id)
    storage.node_items[principal_id] = []
    storage.collections['people'].append(principal_id)
    storage.publishers[principal_id] = [principal_id]

    d = setupPrincipal(client, principal_jid, principal_pass, members_jids)
    return d


@adapter(IPrincipalDeletedEvent)
def onUserDeletion(event):
    """Delete jabber account when a user is removed.
    """
    client = getUtility(IAdminClient)
    settings = getUtility(IXMPPUsers)
    storage = getUtility(IPubSubStorage)

    principal_id = event.principal
    principal_jid = settings.getUserJID(principal_id)

    if principal_id in storage.leaf_nodes:
        storage.leaf_nodes.remove(principal_id)
    if principal_id in storage.publishers:
        del storage.publishers[principal_id]
    if principal_id in storage.node_items:
        del storage.node_items[principal_id]
    if principal_id in storage.collections['people']:
        storage.collections['people'].remove(principal_id)

    d = deletePrincipal(client, principal_jid)
    return d
