from zope.interface import implements
from plone.messaging.core.interfaces import IXMPPSettings


class XMPPSettings(object):

    implements(IXMPPSettings)

    def getUserPassword(self, user_id):
        if user_id == 'admin':
            return 'admin'
        else:
            return 'secret'

    def XMPPDomain(self):
        return 'localhost'

    def BOSHUrl(self):
        return 'http://localhost:8080/http-bind/'
