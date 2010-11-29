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
