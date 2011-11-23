import itertools
import string
import random

from BTrees.OOBTree import OOBTree
from persistent import Persistent
from zope.interface import implements

from jarn.xmpp.core.interfaces import IPubSubStorage
from jarn.xmpp.core.interfaces import IXMPPPasswordStorage

chars = string.letters + string.digits


class XMPPPasswordStorage(Persistent):

    implements(IXMPPPasswordStorage)

    def __init__(self):
        self._passwords = OOBTree()

    def get(self, user_id):
        if user_id in self._passwords:
            return self._passwords[user_id]
        return None

    def set(self, user_id):
        password = ''.join([random.choice(chars) for i in range(12)])
        self._passwords[user_id] = password
        return password

    def remove(self, user_id):
        if user_id in self._passwords:
            del self._passwords[user_id]

    def clear(self):
        self._passwords.clear()


class PubSubStorage(object):

    implements(IPubSubStorage)

    def __init__(self):
        self.items = dict()
        self.node_items = dict()
        self.collections = dict()
        self.leaf_nodes = []
        self.publishers = dict()
        self.comments = dict()

    def itemsFromNodes(self, nodes, start=0, count=20):
        if not isinstance(nodes, list):
            nodes = [nodes]
        all_items = [self.node_items[node]
                     for node in nodes
                     if node in self.node_items]
        ids = sorted(itertools.chain(*all_items),
                        key=lambda item_id: self.items[item_id]['updated'], reverse=True)
        return [self.items[item_id] for item_id in ids[start:count + start]]

    def getItemById(self, item_id):
        return self.items.get(item_id)

    def getNodeByItemId(self, item_id):
        for node in self.leaf_nodes:
            if item_id in self.node_items[node]:
                return node

    def getCommentsForItemId(self, item_id):
        if item_id not in self.comments:
            return []
        return [self.items[iid] for iid in self.comments[item_id]]