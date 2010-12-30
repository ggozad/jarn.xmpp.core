from zope.component import getUtility

from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.interfaces import IAdminClient


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

    def affiliateUser(result):
        d = client.setNodeAffiliations(
            principal_id, [(jsettings.getUserJID(principal_id), 'publisher')])
        return d

    def configureUserPubSubNode(result):
        d = client.configureNode(principal_id,
                                 options={'pubsub#collection': 'people'})
        d.addCallback(affiliateUser)
        return d

    def addUserPubSubNode(add_result):
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