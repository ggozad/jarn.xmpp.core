import logging

from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.interfaces import IPubSubStorage
from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.utils.users import setupPrincipal

logger = logging.getLogger('plone.messaging.core')


def onUserCreation(event):
    """Create a jabber account for new user.
    """

    jsettings = getUtility(IXMPPSettings)
    client = getUtility(IAdminClient)
    storage = getUtility(IPubSubStorage)

    principal = event.principal
    principal_id = principal.getUserId()
    principal_jid = jsettings.getUserJID(principal_id)
    mtool = getToolByName(principal, 'portal_membership')
    members_jids = [jsettings.getUserJID(member.getUserId())
                    for member in mtool.listMembers()]

    def genPasswd():
        return 'secret'
        import string
        import random
        chars = string.letters + string.digits
        return ''.join([random.choice(chars) for i in range(12)])

    storage.leaf_nodes.append(principal_id)
    storage.node_items[principal_id] = []
    storage.collections['people'].append(principal_id)
    storage.publishers[principal_id] = [principal_id]

    d = setupPrincipal(client, principal_jid, genPasswd(), members_jids)
    return d


def onUserDeletion(event):
    """Delete jabber account when a user is removed.
    """
    client = getUtility(IAdminClient)
    jsettings = getUtility(IXMPPSettings)
    storage = getUtility(IPubSubStorage)

    principal_id = event.principal
    jid = u'%s@%s' % (principal_id, jsettings.XMPPDomain)

    def finalResult(result):
        if result == False:
            logger.error("Failed onUserDeletion for user %s" % principal_id)
        logger.info("Succesful onUserDeletion for user %s" % principal_id)

    def deleteUser(result):
        if result == False:
            return False
        if principal_id in storage.leaf_nodes:
            storage.leaf_nodes.remove(principal_id)
        if principal_id in storage.publishers:
            del storage.publishers[principal_id]
        if principal_id in storage.node_items:
            del storage.node_items[principal_id]
        if principal_id in storage.collections['people']:
            storage.collections['people'].remove(principal_id)

        d = client.admin.deleteUsers([jid])
        return d

    d = client.deleteNode(principal_id)
    d.addCallback(deleteUser)
    d.addCallback(finalResult)
    return d
