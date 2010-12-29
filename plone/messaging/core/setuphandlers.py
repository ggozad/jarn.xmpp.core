from zope.component import getUtility

from plone.messaging.core.interfaces import IPubSubClient


def createDefaultPubSubNodes():
    pubsub = getUtility(IPubSubClient)
    pubsub.createNode('people',
        options={'pubsub#node_title': 'All personal feeds',
                 'pubsub#node_type': 'collection',
                 'pubsub#collection': ''})
