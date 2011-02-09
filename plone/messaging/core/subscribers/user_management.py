import logging

from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.interfaces import IPubSubStorage
from plone.messaging.core.interfaces import IAdminClient

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

    def subscribeToAllUsers(result):
        if result == False:
            return False
        client.chat.sendRosterItemAddSuggestion(principal_jid, members_jids)
        return result

    def addUserPubSubNode(result):
        if result == False:
            return False
        d = client.createNode(principal_id)
        return d

    def configureUserPubSubNode(result):
        if result == False:
            return False
        storage.leaf_nodes.append(principal_id)
        storage.node_items[principal_id] = []
        d = client.configureNode(principal_id,
            options={'pubsub#collection': 'people'})
        return d

    def affiliateUser(result):
        if result == False:
            return False
        storage.collections['people'].append(principal_id)
        d = client.setNodeAffiliations(
            principal_id, [(jsettings.getUserJID(principal_id), 'publisher')])
        return d

    def subscribeToMainFeed(result):
        if result == False:
            return False
        storage.publishers[principal_id] = [principal_id]
        d = client.setSubscriptions('people',
            [(jsettings.getUserJID(principal_id), 'subscribed')])
        return d

    def finalResult(result):
        if result == False:
            logger.error("Failed onUserCreation for user %s" % principal_id)
        else:
            logger.info("Succesful onUserCreation for user %s" % principal_id)
        return result

    d = client.admin.addUser(principal_jid.userhost(), genPasswd())
    d.addCallback(subscribeToAllUsers)
    d.addCallback(addUserPubSubNode)
    d.addCallback(configureUserPubSubNode)
    d.addCallback(affiliateUser)
    d.addCallback(subscribeToMainFeed)
    d.addCallback(finalResult)
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
