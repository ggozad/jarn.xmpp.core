from zope.interface import Interface
from zope.component.interfaces import IObjectEvent, implements
from zope.viewlet.interfaces import IViewletManager


class IXMPPUsers(Interface):
    """ Marker interface for the XMPP tool.
    """


class IXMPPPasswordStorage(Interface):
    """ Marker interface for the xmmp user passwords
    """


class IPubSubable(Interface):
    """Interface for objects that can be uniquely linked to pubsub nodes.
    """


class IPubSubStorage(Interface):
    """Marker interface for the PubSub storage
    """


class IAdminClient(Interface):
    """Marker interface for the PubSub twisted client.
    """


class IAdminClientConnected(IObjectEvent):
    """Admin client has connected.
    """


class AdminClientConnected(object):
    implements(IAdminClientConnected)

    def __init__(self, obj):
        self.object = obj


class IAdminClientDisconnected(IObjectEvent):
    """Admin client has connected.
    """


class AdminClientDisconnected(object):
    implements(IAdminClientConnected)

    def __init__(self, obj):
        self.object = obj


class IXMPPLoaderVM(IViewletManager):
    """Viewlet manager for the loader viewlet.
    """

class INodeEscaper(Interface):
    """ Utility that provides basic escape mechanism for node (XEP-0106).""" 

    def escape(self, node):
        """Replaces all disallowed characters according to the algorithm 
        described in XEP-0106.
        """

    def unescape(self, node):
        """Replaces all disallowed characters that were escaped  
        with unescaped ones.
        """

