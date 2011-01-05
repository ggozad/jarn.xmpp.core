import logging

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.interfaces import IPubSubStorage
from plone.messaging.core.interfaces import IAdminClient

logger = logging.getLogger('plone.messaging.core')


def onUserCreation(event):
    """Create a jabber account for new user.
    """
    portal = getUtility(ISiteRoot)

    principal = event.principal
    principal_id = principal.getUserId()
    jsettings = getUtility(IXMPPSettings)
    jid = u'%s@%s' % (principal_id, jsettings.XMPPDomain)
    client = getUtility(IAdminClient)
    storage = getUtility(IPubSubStorage)

    def genPasswd():
        return 'secret'
        import string
        import random
        chars = string.letters + string.digits
        return ''.join([random.choice(chars) for i in range(12)])

    def finalResult(result):
        if result == False:
            logger.error("Failed to subscribe user %s to node 'people'" % principal_id)
            return
        logger.info("Subscribed user %s to node 'people'" % principal_id)

    def subscribeToMainFeed(result):
        if result == False:
            logger.error("Failed to associate user %s with node %s" % (principal_id, principal))
            return
        storage.publishers[principal_id] = [principal_id]
        logger.info("Associated user %s with node %s" % (principal_id, principal))
        d = client.setSubscriptions('people', [(jsettings.getUserJID(principal_id), 'subscribed')])
        d.addCallback(finalResult)
        return d

    def affiliateUser(result):
        if result == False:
            logger.error("Failed to add pubsub node %s to 'people' collection" % principal_id)
            return
        storage.collections['people'].append(principal_id)
        logger.info("Add pubsub node %s to 'people' collection" % principal_id)
        d = client.setNodeAffiliations(
            principal_id, [(jsettings.getUserJID(principal_id), 'publisher')])
        d.addCallback(subscribeToMainFeed)
        return d

    def configureUserPubSubNode(result):
        if result == False:
            logger.error("Failed to add pubsub node  %s" % principal_id)
            return
        storage.leaf_nodes.append(principal_id)
        storage.node_items[principal_id] = []
        logger.info("Added pubsub node  %s" % principal_id)
        d = client.configureNode(principal_id, options={'pubsub#collection': 'people'})
        d.addCallback(affiliateUser)
        return d

    def addUserPubSubNode(result):
        if result == False:
            logger.error("Failed to add user %s" % principal_id)
            return
        logger.info("Added user %s" % principal_id)
        d = client.createNode(principal_id)
        d.addCallback(configureUserPubSubNode)
        return d

    def subscribeToAllUsers(result):
        mtool = getToolByName(portal,'portal_membership')
        principal_jid = jsettings.getUserJID(principal_id)
        members_jids = [jsettings.getUserJID(member.getUserId())
                        for member in mtool.listMembers()]
        client.chat.sendRosterItemAddSuggestion(principal_jid, members_jids)
        return result

    d = client.admin.addUser(jid, genPasswd())
    d.addCallback(subscribeToAllUsers)
    d.addCallback(addUserPubSubNode)
    return d


def onUserDeletion(event):
    """Delete jabber account when a user is removed.
    """
    principal_id = event.principal
    client = getUtility(IAdminClient)
    jsettings = getUtility(IXMPPSettings)
    jid = u'%s@%s' % (principal_id, jsettings.XMPPDomain)
    storage = getUtility(IPubSubStorage)

    def finalResult(result):
        if result == False:
            logger.error("Failed to delete account  %s" % principal_id)
        logger.info("Deleted account %s" % principal_id)

    def deleteUser(result):
        if result == False:
            logger.error("Failed to delete pubsub node  %s" % principal_id)
        if principal_id in storage.leaf_nodes:
            storage.leaf_nodes.remove(principal_id)
        if principal_id in storage.publishers:
            del storage.publishers[principal_id]
        if principal_id in storage.node_items:
            del storage.node_items[principal_id]
        if principal_id in storage.collections['people']:
            storage.collections['people'].remove(principal_id)
        logger.info("Deleted pubsub node  %s" % principal_id)

        d = client.admin.deleteUsers([jid])
        d.addCallback(finalResult)
    d = client.deleteNode(principal_id)
    d.addCallback(deleteUser)
    return d
