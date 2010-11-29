from zope.component import getUtility
from zope.component import getSiteManager
from twisted.words.protocols.jabber.jid import JID
from plone.messaging.core.jabberclient import JabberClient, Admin
from plone.messaging.core.interfaces import IJabberClient


def initJabberClient(event):
    reactor = event.object
    sm = getSiteManager()
    jabber_client = JabberClient(reactor)
    sm.registerUtility(jabber_client, IJabberClient)

    def announceStart(xmlstream):
        result = xmlstream.factory.streamManager. \
            handlers[0].sendAnnouncement("Instance started.")
        return result

    admin_jid = JID("admin@localhost")
    admin_password = 'admin'
    d = jabber_client.execute(admin_jid, admin_password,
                              announceStart, extra_handlers=[Admin()])
    return d

def onUserCreation(event):
    """Create a jabber account for new user
    """
    principal = event.principal
    jid = u'%s@%s' % (principal.getUserId(), 'localhost')

    def genPasswd():
        import string
        import random
        chars = string.letters + string.digits
        return ''.join([random.choice(chars) for i in range(12)])

    def addUser(xmlstream):
        result = xmlstream.factory.streamManager. \
            handlers[0].addUser(jid, genPasswd())
        return result

    jabber_client = getUtility(IJabberClient)
    admin_jid = JID("admin@localhost")
    admin_password = 'admin'
    d = jabber_client.execute(admin_jid, admin_password,
                              addUser, extra_handlers=[Admin()])
    return d

def onUserDeletion(event):
    principal = event.principal
    jid = u'%s@%s' % (principal, 'localhost')

    def deleteUser(xmlstream):
        result = xmlstream.factory.streamManager. \
            handlers[0].deleteUsers([jid])
        return result

    jabber_client = getUtility(IJabberClient)
    admin_jid = JID("admin@localhost")
    admin_password = 'admin'
    d = jabber_client.execute(admin_jid, admin_password,
                              deleteUser, extra_handlers=[Admin()])
    return d