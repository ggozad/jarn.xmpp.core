from BTrees.OOBTree import OOBTree
from persistent import Persistent
from zope.interface import implements

from jarn.xmpp.core.interfaces import IPubSubStorage
from jarn.xmpp.core.interfaces import IXMPPPasswordStorage

class XMPPPasswordStorage(Persistent):

    implements(IXMPPPasswordStorage)

    def __init__(self):
        self._passwords = OOBTree()

    def get(self, jid):
        if jid in self._passwords:
            return self._passwords[jid]
        return None

    def set(self, jid, password):
        self._passwords[jid] = password


class PubSubStorage(object):

    implements(IPubSubStorage)

    def __init__(self):
        self.node_items = dict()
        self.collections = dict()
        self.leaf_nodes = []
        self.publishers = dict()
