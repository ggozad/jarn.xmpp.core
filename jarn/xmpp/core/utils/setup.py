import logging

from twisted.internet import defer
from twisted.words.protocols.jabber.jid import JID

from jarn.xmpp.core.utils.pubsub import content_node_config
from jarn.xmpp.core.utils.pubsub import getAllChildNodes
from jarn.xmpp.core.utils.users import setupPrincipal

logger = logging.getLogger('jarn.xmpp.core')


def setupXMPPEnvironment(admin, member_jids=[],
                         member_passwords={},
                         content_nodes=[]):

    def deleteAllNodes(result):
        nodes = sum(result.values(), [])
        if nodes:
            d = defer.DeferredList([admin.deleteNode(node)
                                    for node in nodes],
                                   consumeErrors=True)
            return d
        return True

    def createCollections(result):
        if not result:
            return False
        d1 = admin.createNode('people',
            options={'pubsub#node_title': 'All personal feeds',
                     'pubsub#node_type': 'collection',
                     'pubsub#collection': ''})
        d2 = admin.createNode('content',
            options={'pubsub#node_title': 'All content feeds',
                     'pubsub#node_type': 'collection',
                     'pubsub#collection': ''})
        d = defer.DeferredList([d1, d2])
        return d

    def createContentNodes(result):
        if not result:
            return False

        deferred_list = []
        for uid in content_nodes:
            d = admin.createNode(uid, options=content_node_config)
            deferred_list.append(d)
        if deferred_list:
            d = defer.DeferredList(deferred_list, consumeErrors=True)
            return d
        return True

    def createDummyItemNodes(result):
        """ XXX: This is necessary as ejabberd stupidly considers a node
        a collection only if it has children...
        """
        if not result:
            return False

        d1 = admin.createNode('dummy_people_node',
                              options={'pubsub#collection': 'people'})
        d2 = admin.createNode('dummy_content_node',
                              options={'pubsub#collection': 'content'})
        d = defer.DeferredList([d1, d2], consumeErrors=True)
        return d

    def subscribeAdmin(result):
        if not result:
            return False

        d = admin.subscribe('people',
                            JID(admin.jid.userhost()),
                            options={'pubsub#subscription_type': 'items',
                                     'pubsub#subscription_depth': 'all'})
        return d

    def createUsers(result):
        if not result:
            return False
        if not member_jids:
            return True
        deferred_list = []
        roster_jids = []
        for member_jid in member_jids:
            d = setupPrincipal(admin,
                               member_jid,
                               member_passwords[member_jid],
                               roster_jids)
            roster_jids.append(member_jid)
            deferred_list.append(d)
        if deferred_list:
            d = defer.DeferredList(deferred_list, consumeErrors=True)
            return d
        return True

    d = getAllChildNodes(admin, None)
    d.addCallback(deleteAllNodes)
    d.addCallback(createCollections)
    d.addCallback(createContentNodes)
    d.addCallback(createDummyItemNodes)
    d.addCallback(subscribeAdmin)
    d.addCallback(createUsers)
    return d
