from zope.component import getUtility
from twisted.words.protocols.jabber.jid import JID
from plone.messaging.twisted.client import Admin
from plone.messaging.twisted.interfaces import IJabberClient


def announceStart(event):

    client = getUtility(IJabberClient)

    def announceStart(xmlstream):
        result = xmlstream.factory.streamManager. \
            handlers[0].sendAnnouncement("Instance started.")
        return result

    admin_jid = JID("admin@localhost")
    admin_password = 'admin'
    d = client.execute(admin_jid, admin_password,
                              announceStart, extra_handlers=[Admin()])
    return d
