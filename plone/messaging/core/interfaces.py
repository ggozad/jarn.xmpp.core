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


class IPubSubClient(Interface):
    """Marker interface for the PubSub twisted client.
    """


class IPubSubClientConnected(IObjectEvent):
    """Pubsub client has connected.
    """
    pass


class PubSubClientConnected(object):
    implements(IPubSubClientConnected)

    def __init__(self, obj):
        self.object = obj
