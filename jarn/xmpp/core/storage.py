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
        self.node_items = dict()
        self.collections = dict()
        self.leaf_nodes = []
        self.publishers = dict()
