import logging

from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

from jarn.xmpp.core.interfaces import IXMPPSettings
from jarn.xmpp.core.interfaces import IPubSubStorage
from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.utils.users import setupPrincipal
from jarn.xmpp.core.utils.users import deletePrincipal

logger = logging.getLogger('jarn.xmpp.core')


def onUserCreation(event):
    """Create a jabber account for new user.
    """
    client = getUtility(IAdminClient)
    jsettings = getUtility(IXMPPSettings)
    storage = getUtility(IPubSubStorage)

    principal = event.principal
    principal_id = principal.getUserId()
    principal_jid = jsettings.getUserJID(principal_id)
    principal_pass = jsettings.getUserPassword(principal_id)
    mtool = getToolByName(principal, 'portal_membership')
    members_jids = [jsettings.getUserJID(member.getUserId())
                    for member in mtool.listMembers()]

    storage.leaf_nodes.append(principal_id)
    storage.node_items[principal_id] = []
    storage.collections['people'].append(principal_id)
    storage.publishers[principal_id] = [principal_id]

    d = setupPrincipal(client, principal_jid, principal_pass, members_jids)
    return d


def onUserDeletion(event):
    """Delete jabber account when a user is removed.
    """
    client = getUtility(IAdminClient)
    jsettings = getUtility(IXMPPSettings)
    storage = getUtility(IPubSubStorage)

    principal_id = event.principal
    principal_jid = jsettings.getUserJID(principal_id)

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
