from zope.interface import Interface


class IJabberClient(Interface):
    """ Marker interface for the JabberClient utility.
    """


class IXMPPSettings(Interface):
    """ Marker interface for the XMPP tool.
    """

    def getUserPassword():
        pass

    def XMPPDomain():
        pass

    def BOSHUrl():
        pass
