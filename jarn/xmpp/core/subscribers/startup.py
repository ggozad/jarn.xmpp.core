import logging

from plone.registry.interfaces import IRegistry
from twisted.internet import defer
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.component import queryUtility

from jarn.xmpp.twisted.interfaces import IZopeReactor

from jarn.xmpp.core.client import AdminClient
from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IPubSubStorage

logger = logging.getLogger('jarn.xmpp.core')


def setupAdminClient(portal, event):
    client = queryUtility(IAdminClient)
    if client is None:
        settings = getUtility(IRegistry)

        try:
            jid = settings['jarn.xmpp.adminJID']
            jdomain = settings['jarn.xmpp.xmppDomain']
            password = settings['jarn.xmpp.adminPassword']
            pubsub_jid = settings['jarn.xmpp.pubsubJID']
        except KeyError:
            return

        client = AdminClient(jid, jdomain, password, pubsub_jid)
        gsm = getGlobalSiteManager()
        gsm.registerUtility(client, IAdminClient)

        def checkAdminClientConnected():
            if client.state != 'authenticated':
                logger.error('XMPP admin client has not been able to authenticate. ' \
                    'Client state is "%s". Will retry on the next request.' % client.state)
                gsm.unregisterUtility(client, IAdminClient)

        zr = getUtility(IZopeReactor)
        zr.reactor.callLater(10, checkAdminClientConnected)


def adminConnected(event):
    logger.info('XMPP admin client has authenticated succesfully.')
    # Since this is our initial connection, populate ram storage with the
    # pubsub nodes.
    populatePubSubStorage()

    # Register user subscribers
    import user_management
    gsm = getGlobalSiteManager()
    gsm.registerHandler(user_management.onUserCreation)
    gsm.registerHandler(user_management.onUserDeletion)


def adminDisconnected(event):
    client = queryUtility(IAdminClient)
    logger.error('XMPP admin client disconnected.')
    if client:
        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(client, IAdminClient)


def populatePubSubStorage():

    client = getUtility(IAdminClient)
    storage = getUtility(IPubSubStorage)

    def getChildNodes(parent):

        def gotNodeItems(result):
            node, items = result
            storage.node_items[node] = []
            for item in items:
                item_id = item['id']
                storage.items[item_id] = item
                storage.node_items[node].append(item_id)
                if parent:
                    storage.node_items[parent].append(item_id)

        def gotNodeAffiliations(result):
            node, affiliations = result
            publishers = [jid.user
                          for jid, role in affiliations
                          if role=='publisher']
            storage.publishers[node] = publishers

        def gotNodeTypes(result):
            cNodes = []
            lNodes = []
            for success, res in result:
                if success:
                    node, node_type = res
                    if node_type == 'collection':
                        cNodes.append(node)
                    else:
                        lNodes.append(node)

            deferred_list = []
            for node in cNodes:
                storage.collections[node] = []
                storage.node_items[node] = []
                if parent:
                    storage.collections[parent].append(node)
                deferred_list.append(getChildNodes(node))

            for node in lNodes:
                storage.leaf_nodes.append(node)
                if parent:
                    storage.collections[parent].append(node)
                d = client.getNodeItems(node)
                d.addCallback(gotNodeItems)
                deferred_list.append(d)
                d = client.getNodeAffiliations(node)
                d.addCallback(gotNodeAffiliations)
                deferred_list.append(d)

            return defer.DeferredList(deferred_list)

        def gotNodes(result):
            d = defer.DeferredList(
                [client.getNodeType(node_dict['node'])
                 for node_dict in result],
                consumeErrors=True)
            d.addCallback(gotNodeTypes)
            return d

        d = client.getNodes(parent)
        d.addCallback(gotNodes)
        return d

    def postProcess(result):
        # Look for comments and take them out from the node's items while
        # putting them in the comments list.

        for node in storage.leaf_nodes:
            for item_id in storage.node_items[node][:]:
                item = storage.getItemById(item_id)
                if 'parent' in item:
                    storage.node_items[node].remove(item_id)
                    for cnode in storage.collections:
                        if node in storage.collections[cnode] and item_id in storage.node_items[cnode]:
                            storage.node_items[cnode].remove(item_id)
                    parent_id = item['parent']
                    if parent_id in storage.comments:
                        storage.comments[parent_id].append(item_id)
                    else:
                        storage.comments[parent_id] = [item_id]

        # Then sort them chronologically
        for node in storage.node_items:
            storage.node_items[node].sort(
                key=lambda item_id: storage.getItemById(item_id)['updated'],
                reverse=True)
        for thread in storage.comments:
            storage.comments[thread].sort(
                key=lambda item_id: storage.getItemById(item_id)['updated'])
        logger.info('Post-processing PubSub storage done.')

    d = getChildNodes(None)
    d.addCallback(postProcess)
    return d
