import logging

from zope.component import getUtility

from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.interfaces import IAdminClient

logger = logging.getLogger('plone.messaging.core')


def onUserCreation(event):
    """Create a jabber account for new user.
    """

    principal = event.principal
    principal_id = principal.getUserId()
    jsettings = getUtility(IXMPPSettings)
    jid = u'%s@%s' % (principal_id, jsettings.XMPPDomain)
    client = getUtility(IAdminClient)

    def genPasswd():
        return 'secret'
        import string
        import random
        chars = string.letters + string.digits
        return ''.join([random.choice(chars) for i in range(12)])

    def finalResult(result):
        if result == False:
            logger.error("Failed to associate user %s with node %s" % (principal_id, principal))
            return
        logger.info("Associated user %s with node %s" % (principal_id, principal))

    def affiliateUser(result):
        if result == False:
            logger.error("Failed to add pubsub node %s to 'people' collection" % principal_id)
            return
        logger.info("Add pubsub node %s to 'people' collection" % principal_id)
        d = client.setNodeAffiliations(
            principal_id, [(jsettings.getUserJID(principal_id), 'publisher')])
        d.addCallback(finalResult)
        return d

    def configureUserPubSubNode(result):
        if result == False:
            logger.error("Failed to add pubsub node  %s" % principal_id)
            return
        logger.info("Added pubsub node  %s" % principal_id)
        d = client.configureNode(principal_id, options={'pubsub#collection': 'people'})
        d.addCallback(affiliateUser)
        return d

    def addUserPubSubNode(result):
        if result == False:
            logger.error("Failed to add user %s" % jid)
            return
        logger.info("Added user %s" % jid)
        d = client.createNode(principal_id)
        d.addCallback(configureUserPubSubNode)
        return d

    d = client.admin.addUser(jid, genPasswd())
    d.addCallback(addUserPubSubNode)
    return d


def onUserDeletion(event):
    """Delete jabber account when a user is removed.
    """
    principal = event.principal
    client = getUtility(IAdminClient)
    jsettings = getUtility(IXMPPSettings)
    jid = u'%s@%s' % (principal, jsettings.XMPPDomain)

    def deleteUser(result):
        client.admin.deleteUsers([jid])

    d = client.deleteNode(principal)
    d.addCallback(deleteUser)
    return d