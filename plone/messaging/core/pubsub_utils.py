import logging
from datetime import datetime

from twisted.words.xish.domish import Element
from wokkel.pubsub import Item
from plone.messaging.twisted.interfaces import IDeferredXMPPClient
from plone.messaging.twisted.protocols import PubSubHandler
from zope.component import getUtility

from plone.messaging.core.interfaces import IXMPPSettings


logger = logging.getLogger('plone.messaging.core')


def subscribeUserToNode(identifier, subscriber_id, unsubscribe=False):
    jsettings = getUtility(IXMPPSettings)
    subscriber_jid = jsettings.getUserJID(subscriber_id)
    password = jsettings.getUserPassword(subscriber_id)

    def subscribeUser(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        d = None
        if unsubscribe:
            d = pubsub_handler.unsubscribe(jsettings.PubSubJID,
                                              identifier,
                                              subscriber_jid)
        else:
            d = pubsub_handler.subscribe(jsettings.PubSubJID,
                                              identifier,
                                              subscriber_jid)
        return d

    jabber_client = getUtility(IDeferredXMPPClient)
    d = jabber_client.execute(subscriber_jid, password,
                              subscribeUser, extra_handlers=[PubSubHandler()])
    return d


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
            logger.info("Successfully published item pubsub node %s" % identifier)
        else:
            logger.error("Failure in publishing item to pubsub node %s" % identifier)

    jabber_client = getUtility(IDeferredXMPPClient)
    d = jabber_client.execute(user_jid, password,
                              publishItem, extra_handlers=[PubSubHandler()])
    d.addCallback(resultCb)
    return d
