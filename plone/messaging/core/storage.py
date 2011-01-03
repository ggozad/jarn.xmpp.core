from zope.interface import implements

from plone.messaging.core.interfaces import IPubSubStorage


class PubSubStorage(object):

    implements(IPubSubStorage)

    def __init__(self):
        self.node_items = dict()
        self.collections = dict()
        self.leaf_nodes = []
        self.publishers = dict()
        self.subscriptions = dict()