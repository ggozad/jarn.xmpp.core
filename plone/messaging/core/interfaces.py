from zope.interface import Interface
from zope.component.interfaces import IObjectEvent, implements


class IXMPPSettings(Interface):
    """ Marker interface for the XMPP tool.
    """

    def getUserPassword():
        pass

    def XMPPDomain():
        pass

    def BOSHUrl():
        pass


class IAdminClient(Interface):
    """Marker interface for the PubSub twisted client.
    """


class IAdminClientConnected(IObjectEvent):
    """Pubsub client has connected.
    """
    pass


class AdminClientConnected(object):
    implements(IAdminClientConnected)

    def __init__(self, obj):
        self.object = obj
