from datetime import datetime
import logging

from twisted.words.xish.domish import Element
from wokkel.pubsub import Item
from plone.messaging.twisted.interfaces import IDeferredXMPPClient
from plone.messaging.twisted.protocols import PubSubHandler
from zope.component import getUtility

from plone.messaging.core.interfaces import IXMPPSettings

content_node_config = {'pubsub#send_last_published_item': 'never',
                       'pubsub#collection': 'content'}

logger = logging.getLogger('plone.messaging.core')


def publishItemToNode(identifier, content, user_id):

    jsettings = getUtility(IXMPPSettings)
    user_jid = jsettings.getUserJID(user_id)
    password = jsettings.getUserPassword(user_id)

    entry = Element(('http://www.w3.org/2005/Atom', 'entry'))
    entry.addElement('content', content=content)
    entry.addElement('author', content=user_id)
    now = datetime.now().isoformat()
    entry.addElement('updated', content=now)
    entry.addElement('published', content=now)
    item = Item(payload=entry)

    def publishItem(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.publish(jsettings.PubSubJID,
                                          identifier,
                                          items = [item])
        return result

    def resultCb(result):
        if result:
            logger.info("Successfully published to node %s" % identifier)
        else:
            logger.error("Failure in publishing to node %s" % identifier)

    jabber_client = getUtility(IDeferredXMPPClient)
    d = jabber_client.execute(user_jid, password,
                              publishItem, extra_handlers=[PubSubHandler()])
    d.addCallback(resultCb)
    return d
