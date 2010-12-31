import logging

from zope.component import getUtility

from plone.messaging.core.interfaces import IAdminClient, IXMPPSettings

logger = logging.getLogger('plone.messaging.core')


def createDefaultPubSubNodes():
    pubsub = getUtility(IAdminClient)
    jsettings = getUtility(IXMPPSettings)
    jid = jsettings.getUserJID('admin')

    def finalResult(result):
        if result == False:
            logger.error("Failed to subscribe admin to 'people'")
            return
        logger.info("Subscribed admin to 'people'")

    def subscribeAdmin(result):
        if result == False:
            logger.error("Failed to add pubsub node 'people'")
            return
        logger.info("Add pubsub node 'people'")

        d = pubsub.subscribe('people', jid,
            options={'pubsub#subscription_type': 'items',
                  'pubsub#subscription_depth': 'all'})
        d.addCallback(finalResult)
        return d

    d = pubsub.createNode('people',
        options={'pubsub#node_title': 'All personal feeds',
                 'pubsub#node_type': 'collection',
                 'pubsub#collection': ''})
    d.addCallback(subscribeAdmin)
    return d
