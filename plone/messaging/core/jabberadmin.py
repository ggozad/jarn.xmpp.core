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
        logger.info("Admin user %s has logged in." %
            self.xmlstream.factory.authenticator.jid.full())

    def connectionLost(self, reason):
        logger.info("Admin user %s has logged out." %
            self.xmlstream.factory.authenticator.jid.full())


class PubSub(PubSubClient):

    def connectionInitialized(self):
        logger.info("Pubsub user %s has logged in" % self.parent.jid.full())
        self.send(AvailablePresence(priority=-10))


class JabberAdmin(object):

    implements(IJabberAdmin)

    def __init__(self, reactor):
        self._reactor = reactor

    def execute(self, callback, errback=None):
        jid = JID("admin@localhost")
        password = 'admin'
        factory = client.DeferredClientFactory(jid, password)
        adminHandler = Admin()
        adminHandler.setHandlerParent(factory.streamManager)

        d = client.clientCreator(factory)
        d.addCallback(callback)

        def disconnect(result):
            factory.streamManager.xmlstream.sendFooter()
            factory.streamManager.xmlstream.transport.connector.disconnect()
            return result

        d.addCallback(disconnect)

        if errback:
            d.addErrback(errback)
        else:
            d.addErrback(logger.error)

        self._reactor.connectTCP("localhost", 5222, factory)
        return d
