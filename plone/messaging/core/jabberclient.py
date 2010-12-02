"""
XMPP subprotocol handler that for:
    * XMPP admin.
"""
import random
import string
import logging
from zope.interface import implements
from wokkel import client
from wokkel.xmppim import AvailablePresence
from wokkel.pubsub import PubSubClient
from plone.messaging.twisted.protocols import AdminHandler, ChatHandler
from plone.messaging.core.interfaces import IJabberClient

logger = logging.getLogger('plone.messaging.core')


class Admin(AdminHandler):

    def connectionInitialized(self):
        logger.info("Admin user %s has logged in." %
            self.xmlstream.factory.authenticator.jid.full())

    def connectionLost(self, reason):
        logger.info("Admin user %s has logged out." %
            self.xmlstream.factory.authenticator.jid.full())


class Chatter(ChatHandler):

    def connectionInitialized(self):
        logger.info("User %s has logged in." %
            self.xmlstream.factory.authenticator.jid.full())

    def connectionLost(self, reason):
        logger.info("User %s has logged out." %
            self.xmlstream.factory.authenticator.jid.full())


class PubSub(PubSubClient):

    def connectionInitialized(self):
        logger.info("Pubsub user %s has logged in" % self.parent.jid.full())
        self.send(AvailablePresence(priority=-10))


class JabberClient(object):

    implements(IJabberClient)

    def __init__(self, reactor):
        self._reactor = reactor

    def execute(self, jid, password,
                callback, extra_handlers=[], errback=None):
        chars = string.letters + string.digits
        resource = 'auto-' + ''.join([random.choice(chars) for i in range(10)])
        jid.resource=resource
        factory = client.DeferredClientFactory(jid, password)
        for handler in extra_handlers:
            handler.setHandlerParent(factory.streamManager)
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

        self._reactor.callFromThread(self._reactor.connectTCP, "localhost", 5222, factory)
        return d
