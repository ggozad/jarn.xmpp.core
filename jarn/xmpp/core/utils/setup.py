import logging

from twisted.internet import defer
from twisted.words.protocols.jabber.jid import JID

from zope.component import getUtility
from Products.CMFCore.utils import getToolByName

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IXMPPPasswordStorage
from jarn.xmpp.core.interfaces import IXMPPUsers

from jarn.xmpp.core.utils.pubsub import getAllChildNodes
from jarn.xmpp.core.utils.users import setupPrincipal
from jarn.xmpp.core.subscribers.startup import populatePubSubStorage


logger = logging.getLogger('jarn.xmpp.core')


def _setupXMPPEnvironment(client, member_jids=[],
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
            options={'pubsub#node_title': 'All personal nodes',
                     'pubsub#node_type': 'collection',
                     'pubsub#collection': '',
                     'pubsub#max_items': 1000})
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


def setupXMPPEnvironment(context):
    xmpp_users = getUtility(IXMPPUsers)
    pass_storage = getUtility(IXMPPPasswordStorage)
    mt = getToolByName(context, 'portal_membership')
    member_ids = mt.listMemberIds()
    member_jids = []
    member_passwords = {}
    pass_storage.clear()
    for member_id in member_ids:
        member_jid = xmpp_users.getUserJID(member_id)
        member_jids.append(member_jid)
        member_passwords[member_jid] = pass_storage.set(member_id)

    admin = getUtility(IAdminClient)

    def initPubSubStorage(result):
        d = populatePubSubStorage()
        return d

    d = _setupXMPPEnvironment(admin, member_jids, member_passwords)
    d.addCallback(initPubSubStorage)
    return d
