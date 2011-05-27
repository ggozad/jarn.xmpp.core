from datetime import datetime
import logging

from plone.registry.interfaces import IRegistry
from twisted.internet import defer
from twisted.words.protocols.jabber.jid import JID
from twisted.words.xish.domish import Element
from wokkel.pubsub import Item
from jarn.xmpp.twisted.interfaces import IDeferredXMPPClient
from jarn.xmpp.twisted.protocols import PubSubHandler
from zope.component import getUtility

from jarn.xmpp.core.interfaces import IXMPPUsers

logger = logging.getLogger('jarn.xmpp.core')


def publishItemToNode(identifier, content, user_id):
    """ Publish an item to a pubsub node.
        XXX: This uses the deferred xmpp client. Cand and should entirely be
        replaced by js, making the deferred client not used anywhere.
    """

    settings = getUtility(IRegistry)
    xmpp_domain = settings['jarn.xmpp.xmppDomain']
    pubsub_jid = JID(settings['jarn.xmpp.pubsubJID'])
    xmpp_users = getUtility(IXMPPUsers)
    user_jid = xmpp_users.getUserJID(user_id)
    password = xmpp_users.getUserPassword(user_id)
    entry = Element(('http://www.w3.org/2005/Atom', 'entry'))
    entry.addElement('content', content=content)
    entry.addElement('author', content=user_id)
    now = datetime.now().isoformat()
    entry.addElement('updated', content=now)
    entry.addElement('published', content=now)
    item = Item(payload=entry)

    def publishItem(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.publish(pubsub_jid, identifier, items = [item])
        return result

    def resultCb(result):
        if result:
            logger.info("Successfully published to node %s" % identifier)
        else:
            logger.error("Failure in publishing to node %s" % identifier)

    jabber_client = getUtility(IDeferredXMPPClient)
    d = jabber_client.execute(user_jid, password, xmpp_domain,
                              publishItem, extra_handlers=[PubSubHandler()])
    d.addCallback(resultCb)
    return d


def getAllChildNodes(client, root):
    """ XXX TODO:
    This would have been simpler if ejabberd supported retrieving
    collection items as it should. Argue in the mailing list.
    """
    tree = {}

    def getChildNodes(parent):

        def gotNodeTypes(result):
            deferred_list = []
            for success, res in result:
                if success:
                    node, node_type = res
                    if node_type == 'collection':
                        tree[node] = []
                        if parent is not None:
                            tree[parent].append(node)
                        else:
                            tree[''].append(node)
                        deferred_list.append(getChildNodes(node))
                    else:
                        if parent is not None:
                            tree[parent].append(node)
                        else:
                            tree[''].append(node)
            if deferred_list:
                return defer.DeferredList(deferred_list)
            return True

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

    def returnResult(result):
        return tree

    if root is None:
        tree[''] = []
    else:
        tree[root] = []

    d = getChildNodes(root)
    d.addCallback(returnResult)
    return d
