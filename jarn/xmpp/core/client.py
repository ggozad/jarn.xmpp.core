import logging

from twisted.internet import defer
from twisted.words.protocols.jabber.jid import JID
from zope.component import getUtility
from zope.event import notify
from zope.interface import implements
from wokkel.xmppim import PresenceClientProtocol

from jarn.xmpp.twisted.client import XMPPClient
from jarn.xmpp.twisted.protocols import AdminHandler
from jarn.xmpp.twisted.protocols import PubSubHandler
from jarn.xmpp.twisted.protocols import ChatHandler

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IPubSubStorage
from jarn.xmpp.core.interfaces import AdminClientConnected
from jarn.xmpp.core.interfaces import AdminClientDisconnected


logger = logging.getLogger('jarn.xmpp.core')


class PubSubClientMixIn(object):

    def _pubsubItemToDict(self, item):
        entry = item.entry
        atom = [(child.name, child.children[0])
            for child in entry.children
            if child.children]
        atom = dict(atom)
        atom['id'] = item['id']
        if entry.geolocation:
            atom['geolocation'] = {
                'latitude': entry.geolocation['latitude'],
                'longitude': entry.geolocation['longitude'],
            }
        return atom

    def itemsReceived(self, event):
        sender = event.sender
        items = event.items

        if sender != self.pubsub_jid or not items:
            return
        headers = event.headers
        collections = headers.get('Collection', [])
        node = event.nodeIdentifier
        items = [self._pubsubItemToDict(item)
                  for item in items
                  if item.name == 'item']
        storage = getUtility(IPubSubStorage)
        for item in items:
            storage.node_items[node].insert(0, item)
            for collection in collections:
                storage.node_items[collection].insert(0, item)

    def getNodes(self, identifier=None):
        d = self.pubsub.getNodes(self.pubsub_jid, identifier)
        return d

    def subscribe(self, identifier, subscriber, options=None, sender=None):
        return self.pubsub.subscribe(
            self.pubsub_jid, identifier, subscriber, options, sender)

    def getSubscriptions(self, identifier):

        def cb(result):
            return (identifier, result)

        d = self.pubsub.getSubscriptions(self.pubsub_jid, identifier)
        d.addCallback(cb)
        return d

    def setSubscriptions(self, identifier, delta):
        d = self.pubsub.setSubscriptions(self.pubsub_jid, identifier, delta)
        return d

    def getNodeType(self, identifier):

        def cb(result):
            return (identifier, result)

        d = self.pubsub.getNodeType(self.pubsub_jid, identifier)
        d.addCallback(cb)
        return d

    def createNode(self, identifier, options=None):
        d = self.pubsub.createNode(self.pubsub_jid,
                                   identifier,
                                   options=options)
        return d

    def deleteNode(self, identifier):
        d = self.pubsub.deleteNode(self.pubsub_jid, identifier)
        return d

    def publish(self, identifier, items):
        self.pubsub.publish(self.pubsub_jid, identifier, items=items)

    def getDefaultNodeConfiguration(self):
        d = self.pubsub.getDefaultNodeConfiguration(self.pubsub_jid)
        return d

    def getNodeConfiguration(self, node):
        d = self.pubsub.getNodeConfiguration(self.pubsub_jid, node)
        return d

    def configureNode(self, node, options):
        d = self.pubsub.configureNode(self.pubsub_jid, node, options)
        return d

    def getNodeAffiliations(self, identifier):

        def cb(result):
            return identifier, result

        d = self.pubsub.getAffiliations(self.pubsub_jid, identifier)
        d.addCallback(cb)
        return d

    def setNodeAffiliations(self, identifier, affiliations):
        d = self.pubsub.modifyAffiliations(self.pubsub_jid,
                                           identifier,
                                           affiliations)
        return d

    def getCollectionNodeItems(self, identifier, maxItems=10):
        """Currently ejabberd does not support this properly.
        It should work as per
        http://xmpp.org/extensions/xep-0248.html#retrieve-items
        In order to go around it, I get the child nodes of a collection,
        retrieve their items, and return.
        """

        def itemsCb(result):
            items = []
            for (success, value) in result:
                if success:
                    items = items + value
            return items

        def nodesCb(nodes):
            d = defer.DeferredList(
                [self.getNodeItems(node_dict['node'], maxItems=maxItems)
                for node_dict in nodes],
                consumeErrors=True)
            d.addCallback(itemsCb)
            return d

        d = self.getNodes(identifier=identifier)
        d.addCallback(nodesCb)
        return d

    def getNodeItems(self, identifier, maxItems=10):

        def cb(result):
            items = []
            for item in result:
                items.append(self._pubsubItemToDict(item))
            return (identifier, items)

        d = self.pubsub.items(self.pubsub_jid,
                                      identifier,
                                      maxItems=10)
        d.addCallback(cb)
        return d


class AdminClient(XMPPClient, PubSubClientMixIn):

    implements(IAdminClient)

    def __init__(self, jid, jdomain, password, pubsub_jid):

        jid = JID(jid)
        self.pubsub_jid = JID(pubsub_jid)
        self.admin = AdminHandler()
        self.pubsub = PubSubHandler()
        self.chat = ChatHandler()
        self.presence = PresenceClientProtocol()

        super(AdminClient, self).__init__(
            jid, password,
            extra_handlers=[self.admin,
                            self.pubsub,
                            self.chat,
                            self.presence],
            host=jdomain)

    def _authd(self, xs):
        super(AdminClient, self)._authd(xs)
        self.presence.available()
        ev = AdminClientConnected(self)
        notify(ev)

    def _disconnected(self, reason):
        super(AdminClient, self)._disconnected(reason)
        ev = AdminClientDisconnected(self)
        notify(ev)
