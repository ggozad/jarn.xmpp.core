from zope.component import getUtility
from zope.component import getSiteManager
from plone.messaging.core.jabberadmin import JabberAdmin
from plone.messaging.core.interfaces import IJabberAdmin


def initJabberAdmin(event):
    reactor = event.object
    sm = getSiteManager()
    jabber_admin = JabberAdmin(reactor)
    sm.registerUtility(jabber_admin, IJabberAdmin)

    def announceStart(xmlstream):
        d = xmlstream.factory.streamManager. \
            handlers[0].sendAnnouncement("Instance started.")
        return d
    jabber_admin.execute(announceStart)


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
        d = xmlstream.factory.streamManager. \
            handlers[0].addUser(jid, genPasswd())
        return d

    jabber_admin = getUtility(IJabberAdmin)
    jabber_admin.execute(addUser)


def onUserDeletion(event):
    principal = event.principal
    jabber_admin = getUtility(IJabberAdmin)
    jid = u'%s@%s' % (principal, 'localhost')

    def deleteUser(xmlstream):
        d = xmlstream.factory.streamManager. \
            handlers[0].deleteUsers([jid])
        return d

    jabber_admin.execute(deleteUser)
