import logging
from zope.component import getUtility
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
