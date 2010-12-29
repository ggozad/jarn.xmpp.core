from datetime import datetime
import logging

from twisted.words.xish.domish import Element
from zope.component import getUtility
from zope.event import notify
from zope.interface import implements
from wokkel.pubsub import Item

from plone.messaging.twisted.client import PubSub, XMPPClient
from plone.messaging.twisted.interfaces import IDeferredXMPPClient
from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.interfaces import IPubSubClient
from plone.messaging.core.interfaces import PubSubClientConnected

logger = logging.getLogger('plone.messaging.core')


class PubSubItem(object):

    def __init__(self, text, author, date):
        self.text = text
        self.author = author
        self.date = date


class PubSubClient(XMPPClient):

    implements(IPubSubClient)

    def __init__(self):
        jsettings = getUtility(IXMPPSettings)
        jid = jsettings.getUserJID('admin')
        jdomain = jsettings.XMPPDomain
        password = jsettings.getUserPassword('admin')

        super(PubSubClient, self).__init__(jid,
                                           password,
                                           extra_handlers=[PubSub()],
                                           host=jdomain)
        self.pubsub = self.handlers[0]
        self.pubsub_jid = jsettings.PubSubJID

    def _authd(self, xs):
        super(PubSubClient, self)._authd(xs)
        ev = PubSubClientConnected(self)
        notify(ev)

    def getNodes(self, identifier=None):
        d = self.pubsub.getNodes(self.pubsub_jid, identifier)
        return d

    def getNodeType(self, identifier):
        d = self.pubsub.getNodeType(self.pubsub_jid, identifier)
        return d

    def createNode(self, identifier, options=None):

        def cb(result):
            if result == identifier:
                logger.info("Successfully created pubsub node %s" % identifier)
            else:
                logger.error("Failure in creating pubsub node %s" % identifier)

        d = self.pubsub.createNode(self.pubsub_jid,
                                   identifier,
                                   options=options)
        d.addCallback(cb)
        return d

    def deleteNode(self, identifier):

        def cb(result):
            if result:
                logger.info("Successfully deleted pubsub node %s" % identifier)
            else:
                logger.error("Failure in deleting pubsub node %s" % identifier)

        d = self.pubsub.deleteNode(self.pubsub_jid, identifier)
        d.addCallback(cb)
        return d

    def getDefaultNodeConfiguration(self):
        d = self.pubsub.getDefaultNodeConfiguration(self.pubsub_jid)
        return d

    def getNodeConfiguration(self, node):
        d = self.pubsub.getNodeConfiguration(self.pubsub_jid, node)
        return d

    def configureNode(self, node, options):
        d = self.pubsub.configureNode(self.pubsub_jid, node, options)
        return d

    def associateNodeToCollection(self, nodeIdentifier, collectionIdentifier):
        d = self.pubsub.associateNodeToCollection(self.pubsub_jid,
                                                  nodeIdentifier,
                                                  collectionIdentifier)
        return d


    def getNodeAffiliations(self, identifier):
        d = self.pubsub.getAffiliations(self.pubsub_jid,
                                        identifier)
        return d

    def setNodeAffiliations(self, identifier, affiliations):
        d = self.pubsub.modifyAffiliations(self.pubsub_jid,
                                           identifier,
                                           affiliations)
        return d

    def getNodeItems(self, identifier, maxItems=10):

        def cb(result):
            items = []
            for item in result:
                entry = item.entry
                content = entry.content.children[0]
                updated = entry.updated.children[0]
                author = entry.author.children[0]
                items.append(PubSubItem(content, author, updated))
            return items

        d = self.pubsub.items(self.pubsub_jid,
                                      identifier,
                                      maxItems=10)
        d.addCallback(cb)
        return d


def subscribeUserToNode(identifier, subscriber_id):
    jsettings = getUtility(IXMPPSettings)
    subscriber_jid = jsettings.getUserJID(subscriber_id)
    password = jsettings.getUserPassword(subscriber_id)

    def subscribeUser(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.subscribe(jsettings.PubSubJID,
                                          identifier,
                                          subscriber_jid)
        return result

    def resultCb(result):
        if result:
            logger.info("Successfully subscribed user %s to pubsub node %s" % (subscriber_jid, identifier))
        else:
            logger.error("Failure in subscribing user %s to pubsub node %s" % (subscriber_jid, identifier))

    jabber_client = getUtility(IDeferredXMPPClient)
    d = jabber_client.execute(subscriber_jid, password,
                              subscribeUser, extra_handlers=[PubSub()])
    d.addCallback(resultCb)
    return d


def publishItemToNode(identifier, content, user_id):

    jsettings = getUtility(IXMPPSettings)
    user_jid = jsettings.getUserJID(user_id)
    password = jsettings.getUserPassword(user_id)

    entry = Element(('http://www.w3.org/2005/Atom', 'entry'))
    entry.addElement('content', content=content)
    entry.addElement('author', content=user_id)
    now = datetime.now()
    entry.addElement('updated', content=now.isoformat())
    item = Item(payload=entry)

    def publishItem(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.publish(jsettings.PubSubJID,
                                          identifier,
                                          items = [item])
        return result

    def resultCb(result):
        if result:
            logger.info("Successfully published item pubsub node %s" % identifier)
        else:
            logger.error("Failure in publishing item to pubsub node %s" % identifier)

    jabber_client = getUtility(IDeferredXMPPClient)
    d = jabber_client.execute(user_jid, password,
                              publishItem, extra_handlers=[PubSub()])
    d.addCallback(resultCb)
    return d
