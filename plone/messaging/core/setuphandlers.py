from zope.component import getUtility

from plone.messaging.core.interfaces import IAdminClient


def createDefaultPubSubNodes():
    pubsub = getUtility(IAdminClient)
    pubsub.createNode('people',
        options={'pubsub#node_title': 'All personal feeds',
                 'pubsub#node_type': 'collection',
                 'pubsub#collection': ''})
