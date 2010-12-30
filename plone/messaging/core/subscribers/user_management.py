from zope.component import getUtility

from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.interfaces import IAdminClient


def onUserCreation(event):
    """Create a jabber account for new user.
    """

    principal = event.principal
    jsettings = getUtility(IXMPPSettings)
    jid = u'%s@%s' % (principal.getUserId(), jsettings.XMPPDomain)
    client = getUtility(IAdminClient)

    def genPasswd():
        return 'secret'
        import string
        import random
        chars = string.letters + string.digits
        return ''.join([random.choice(chars) for i in range(12)])

    def configureUserPubSubNode(result):
        d = client.configureNode(principal.getUserId(),
                                 options={'pubsub#collection': 'people'})
        return d

    def addUserPubSubNode(add_result):
        d = client.createNode(principal.getUserId())
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