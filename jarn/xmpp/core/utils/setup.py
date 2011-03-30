import logging

from twisted.internet import defer
from twisted.words.protocols.jabber.jid import JID

from jarn.xmpp.core.utils.pubsub import getAllChildNodes
from jarn.xmpp.core.utils.users import setupPrincipal

logger = logging.getLogger('jarn.xmpp.core')


def setupXMPPEnvironment(client, member_jids=[],
                         member_passwords={}):

    def deleteAllNodes(result):
        nodes = sum(result.values(), [])
        # Reverse to delete the children first, then the parents.
        nodes.reverse()
        if nodes:
            d = defer.DeferredList([client.deleteNode(node)
                                    for node in nodes],
                                   consumeErrors=True)
            return d
        return True

    def createCollections(result):
        if not result:
            return False
        d = client.createNode('people',
            options={'pubsub#node_title': 'All personal feeds',
                     'pubsub#node_type': 'collection',
                     'pubsub#collection': ''})
        return d

    def createDummyItemNodes(result):
        """ XXX: This is necessary as ejabberd stupidly considers a node
        a collection only if it has children...
        """
        if not result:
            return False

        d = client.createNode('dummy_people_node',
                              options={'pubsub#collection': 'people'})
        return d

    def subscribeAdmin(result):
        if not result:
            return False

        d = client.subscribe('people',
                            JID(client.jid.userhost()),
                            options={'pubsub#subscription_type': 'items',
                                     'pubsub#subscription_depth': 'all'})
        return d

    def getExistingUsers(result):
        if not result:
            return False
        d = client.admin.getRegisteredUsers()
        return d

    def deleteUsers(result):
        if not result:
            return False
        jids = [user_dict['jid'] for user_dict in result]
        jids.remove(client.jid.userhost())
        if not jids:
            return True
        d = client.admin.deleteUsers(jids)
        return d

    def createUsers(result):
        if not result:
            return False
        if not member_jids:
            return True
        deferred_list = []
        roster_jids = []
        for member_jid in member_jids:
            d = setupPrincipal(client,
                               member_jid,
                               member_passwords[member_jid],
                               roster_jids)
            roster_jids.append(member_jid)
            deferred_list.append(d)
        if deferred_list:
            d = defer.DeferredList(deferred_list, consumeErrors=True)
            return d
        return True

    d = getAllChildNodes(client, None)
    d.addCallback(deleteAllNodes)
    d.addCallback(createCollections)
    d.addCallback(createDummyItemNodes)
    d.addCallback(subscribeAdmin)
    d.addCallback(getExistingUsers)
    d.addCallback(deleteUsers)
    d.addCallback(createUsers)
    return d
