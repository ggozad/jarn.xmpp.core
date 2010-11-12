"""
XMPP subprotocol handler that for:
    * XMPP admin.
"""
import logging
from zope.interface import implements
from twisted.words.protocols.jabber.jid import JID
from wokkel import client
from wokkel.xmppim import AvailablePresence
from wokkel.pubsub import PubSubClient
from plone.messaging.twisted.protocols import AdminClient
from plone.messaging.core.interfaces import IJabberAdmin

logger = logging.getLogger('plone.messaging.core')


class Admin(AdminClient):

    def connectionInitialized(self):
        logger.info("Admin user %s has logged in." % self.parent.jid.full())
        self.send(AvailablePresence(priority=-10))


class PubSub(PubSubClient):

    def connectionInitialized(self):
        logger.info("Pubsub user %s has logged in" % self.parent.jid.full())
        self.send(AvailablePresence(priority=-10))


class JabberAdmin(object):

    implements(IJabberAdmin)

    def __init__(self, reactor):
        jid = JID("admin@localhost")
        password = 'admin'
        self._reactor = reactor
        self._client = client.XMPPClient(jid, password)
        self._adminHandler = Admin()
        self._adminHandler.setHandlerParent(self._client)
        factory = self._client.factory
        self._reactor.connectTCP("localhost", 5222, factory)

    def getAdminClient(self):
        return self._adminHandler
