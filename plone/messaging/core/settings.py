import string
import random

from twisted.words.protocols.jabber.jid import JID
from zope.interface import implements

from plone.messaging.core.interfaces import IXMPPSettings

chars = string.letters + string.digits


class XMPPSettings(object):

    implements(IXMPPSettings)

    def getUserJID(self, user_id):
        return JID("%s@%s" % (user_id, self.XMPPDomain,))

    def getUserPassword(self, user_id):
        if user_id == 'admin':
            return 'admin'
        else:
            # temp hack until I have a persistent password storage
            # if we need to create one:
            # return ''.join([random.choice(chars) for i in range(12)])
            return 'secret'

    @property
    def XMPPDomain(self):
        return 'localhost'

    @property
    def PubSubJID(self):
        return JID('pubsub.localhost')

    @property
    def ConferenceJID(self):
        return JID('conference.localhost')

    @property
    def BOSHUrl(self):
        return 'http://localhost:8080/http-bind/'
