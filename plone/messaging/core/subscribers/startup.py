from twisted.words.protocols.jabber.jid import JID
from twisted.internet import defer
from zope.component import getGlobalSiteManager
from zope.component import getUtility

from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.client import AdminClient


def setupAdminClient(event):
    gsm = getGlobalSiteManager()
    gsm.registerUtility(AdminClient(), IAdminClient)


def adminConnected(event):
    client = event.object
    populatePubSubStorage()
    #client.admin.sendAnnouncement("Instance started")
    #client.deleteNode('people')
    #return
    #from plone.messaging.core.setuphandlers import createDefaultPubSubNodes
    #createDefaultPubSubNodes()
    #from plone.messaging.core.client import publishItemToNode
    #publishItemToNode('gogo', 'hello there', 'gogo')
    return

    def cb(result):
        import pdb; pdb.set_trace( )
    d= client.getSubscriptions('ggozad')
    #d= client.setSubscriptions('ggozad', [(JID('admin@localhost'), 'subscribed')])

    d.addCallback(cb)
    return


def populatePubSubStorage():
    """ TODO: This DOES NOT support nested collections. In fact it's retarted.
    Needs to become recursive to stop being just that...
    """
    client = getUtility(IAdminClient)

    collections = {}
    leaf_nodes = []

    def gotChildNodes(node_types):
        for node_dict in node_types:
            for node in node_dict:
                if node_dict[node] == 'collection':
                    collections[node] = []
                else:
                   leaf_nodes.append(node)
            import pdb; pdb.set_trace( )

    def getChildNodes(parent):

        def gotNodeTypes(result):
            nodes = []
            for success, node_dict in result:
                if success:
                    nodes.append(node_dict)
            return nodes

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
    d.addCallback(gotChildNodes)

