from twisted.internet import defer
from zope.component import getGlobalSiteManager
from zope.component import getUtility

from plone.messaging.core.client import AdminClient
from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.interfaces import IPubSubStorage


def setupAdminClient(event):
    gsm = getGlobalSiteManager()
    gsm.registerUtility(AdminClient(), IAdminClient)


def adminConnected(event):
    client = event.object
    populatePubSubStorage()
    client.admin.sendAnnouncement("Instance started")


def populatePubSubStorage():
    """ TODO: This would have been simpler if ejabberd supported retrieving
    collection items. Enter recursive deferred nightmare ;)
    """

    client = getUtility(IAdminClient)
    storage = getUtility(IPubSubStorage)

    def getChildNodes(parent):

        def gotNodeItems(result):
            node, items = result
            storage.node_items[node] = items
            if parent:
                storage.node_items[parent] = storage.node_items[parent] + (items)
                storage.node_items[parent].sort(key=lambda item: item['updated'],
                                                reverse=True)

        def gotSubscriptions(result):
            node, subscriptions = result
            storage.subscriptions[node] = {}
            for jid, state in subscriptions:
                storage.subscriptions[node][jid.user] = state

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
            for node in cNodes + lNodes:
                d = client.getSubscriptions(node)
                d.addCallback(gotSubscriptions)
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

    d = getChildNodes(None)
    return d
