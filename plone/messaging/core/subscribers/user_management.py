from zope.component import getUtility
from plone.messaging.twisted.client import Admin
from plone.messaging.twisted.interfaces import IDeferredXMPPClient
from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.interfaces import IPubSubClient

def onUserCreation(event):
    """Create a jabber account for new user.
    """

    principal = event.principal
    jsettings = getUtility(IXMPPSettings)
    jid = u'%s@%s' % (principal.getUserId(), jsettings.XMPPDomain)
    admin_jid = jsettings.getUserJID('admin')
    admin_password = jsettings.getUserPassword('admin')
    pubsub = getUtility(IPubSubClient)

    def genPasswd():
        return 'secret'
        import string
        import random
        chars = string.letters + string.digits
        return ''.join([random.choice(chars) for i in range(12)])

    def addUserPubSubNode(add_result):
        d = pubsub.createNode(principal.getUserId())
        d.addCallback(configureUserPubSubNode)
        return d

    def configureUserPubSubNode(result):
        d = pubsub.configureNode(principal.getUserId(), options={'pubsub#collection':'people'})
        return d

    def addUser(xmlstream):
        d = xmlstream.factory.streamManager. \
            handlers[0].addUser(jid, genPasswd())
        d.addCallback(addUserPubSubNode)
        return d

    jabber_client = getUtility(IDeferredXMPPClient)
    d = jabber_client.execute(admin_jid, admin_password,
                              addUser, extra_handlers=[Admin()])
    return d


def onUserDeletion(event):
    """Delete jabber account when a user is removed.
    """

    principal = event.principal
    jsettings = getUtility(IXMPPSettings)
    jid = u'%s@%s' % (principal, jsettings.XMPPDomain)
    admin_jid = jsettings.getUserJID('admin')
    admin_password = jsettings.getUserPassword('admin')

    def deleteUser(xmlstream):
        result = xmlstream.factory.streamManager. \
            handlers[0].deleteUsers([jid])
        return result

    jabber_client = getUtility(IDeferredXMPPClient)
    d = jabber_client.execute(admin_jid, admin_password,
                              deleteUser, extra_handlers=[Admin()])
    return d
