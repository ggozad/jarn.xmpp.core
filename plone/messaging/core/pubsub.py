import logging
from zope.component import getUtility
from twisted.words.xish.domish import Element
from wokkel.pubsub import Item
from plone.messaging.twisted.client import PubSub
from plone.messaging.twisted.interfaces import IJabberClient
from plone.messaging.core.interfaces import IXMPPSettings

logger = logging.getLogger('plone.messaging.core')


def createNode(identifier, access_model='whitelist'):
    jsettings = getUtility(IXMPPSettings)
    admin_jid = jsettings.getUserJID('admin')
    admin_password = jsettings.getUserPassword('admin')

    def createChannel(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.createNode(jsettings.PubSubJID,
            nodeIdentifier=identifier, options={'access_model': access_model})
        return result

    def resultCb(result):
        if result == identifier:
            logger.info("Successfully created pubsub node %s" % identifier)
        else:
            logger.error("Failure in creating pubsub node %s" % identifier)

    jabber_client = getUtility(IJabberClient)
    d = jabber_client.execute(admin_jid, admin_password,
                              createChannel, extra_handlers=[PubSub()])
    d.addCallback(resultCb)
    return d


def deleteNode(identifier):
    jsettings = getUtility(IXMPPSettings)
    admin_jid = jsettings.getUserJID('admin')
    admin_password = jsettings.getUserPassword('admin')

    def deleteChannel(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.deleteNode(jsettings.PubSubJID,
            nodeIdentifier=identifier)
        return result

    def resultCb(result):
        if result:
            logger.info("Successfully deleted pubsub node %s" % identifier)
        else:
            logger.error("Failure in deleting pubsub node %s" % identifier)

    jabber_client = getUtility(IJabberClient)
    d = jabber_client.execute(admin_jid, admin_password,
                              deleteChannel, extra_handlers=[PubSub()])
    d.addCallback(resultCb)
    return d


def subscribeUserToNode(identifier, subscriber_id):
    jsettings = getUtility(IXMPPSettings)
    subscriber_jid = jsettings.getUserJID(subscriber_id)
    password = jsettings.getUserPassword(subscriber_id)

    def subscribeUser(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.subscribe(jsettings.PubSubJID,
                                          identifier,
                                          subscriber_jid)
        return result

    def resultCb(result):
        if result:
            logger.info("Successfully subscribed user %s to pubsub node %s" % (subscriber_jid, identifier))
        else:
            logger.error("Failure in subscribing user %s to pubsub node %s" % (subscriber_jid, identifier))

    jabber_client = getUtility(IJabberClient)
    d = jabber_client.execute(subscriber_jid, password,
                              subscribeUser, extra_handlers=[PubSub()])
    d.addCallback(resultCb)
    return d


def publishItemToNode(identifier, content, user_id):

    jsettings = getUtility(IXMPPSettings)
    user_jid = jsettings.getUserJID(user_id)
    password = jsettings.getUserPassword(user_id)

    entry = Element(('http://www.w3.org/2005/Atom', 'entry'))
    entry.addElement('content', content=content)
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

    jabber_client = getUtility(IJabberClient)
    d = jabber_client.execute(user_jid, password,
                              publishItem, extra_handlers=[PubSub()])
    d.addCallback(resultCb)
    return d
