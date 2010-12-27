import logging
from datetime import datetime

from twisted.words.xish.domish import Element
from zope.component import getUtility
from wokkel.pubsub import Item

from plone.messaging.twisted.client import PubSub
from plone.messaging.twisted.interfaces import IJabberClient
from plone.messaging.core.interfaces import IXMPPSettings

logger = logging.getLogger('plone.messaging.core')


class PubSubItem(object):

    def __init__(self, text, author, date):
        self.text = text
        self.author = author
        self.date = date

def createNode(identifier, access_model='whitelist'):
    jsettings = getUtility(IXMPPSettings)
    admin_jid = jsettings.getUserJID('admin')
    admin_password = jsettings.getUserPassword('admin')

    def createChannel(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.createNode(jsettings.PubSubJID,
            identifier, options={'access_model': access_model})
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


def getNodeAffiliations(identifier):
    jsettings = getUtility(IXMPPSettings)
    admin_jid = jsettings.getUserJID('admin')
    admin_password = jsettings.getUserPassword('admin')

    def getAffiliations(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.getAffiliations(jsettings.PubSubJID,
            identifier)
        return result

    def resultCb(result):
        return result

    jabber_client = getUtility(IJabberClient)
    d = jabber_client.execute(admin_jid, admin_password,
                              getAffiliations, extra_handlers=[PubSub()])
    d.addCallback(resultCb)
    return d


def setNodeAffiliations(identifier, affiliations):
    jsettings = getUtility(IXMPPSettings)
    admin_jid = jsettings.getUserJID('admin')
    admin_password = jsettings.getUserPassword('admin')

    def setAffiliations(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.modifyAffiliations(jsettings.PubSubJID,
            identifier, affiliations)
        return result

    def resultCb(result):
        return result

    jabber_client = getUtility(IJabberClient)
    d = jabber_client.execute(admin_jid, admin_password,
                              setAffiliations, extra_handlers=[PubSub()])
    d.addCallback(resultCb)
    return d


def deleteNode(identifier):
    jsettings = getUtility(IXMPPSettings)
    admin_jid = jsettings.getUserJID('admin')
    admin_password = jsettings.getUserPassword('admin')

    def deleteChannel(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.deleteNode(jsettings.PubSubJID,
            identifier)
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
    entry.addElement('author', content=user_id)
    now = datetime.now()
    entry.addElement('updated', content=now.isoformat())
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


def getNodeItems(identifier, user_id, maxItems=10):

    jsettings = getUtility(IXMPPSettings)
    user_jid = jsettings.getUserJID(user_id)
    password = jsettings.getUserPassword(user_id)

    def getItems(xmlstream):
        pubsub_handler = xmlstream.factory.streamManager.handlers[0]
        result = pubsub_handler.items(jsettings.PubSubJID,
                                      identifier,
                                      maxItems=10)
        return result

    def resultCb(result):
        items = []
        for item in result:
            entry = item.entry
            content = entry.content.children[0]
            updated = entry.updated.children[0]
            author = entry.author.children[0]
            items.append(PubSubItem(content, author, updated))
        return items

    jabber_client = getUtility(IJabberClient)
    d = jabber_client.execute(user_jid, password,
                              getItems, extra_handlers=[PubSub()])
    d.addCallback(resultCb)
    return d
