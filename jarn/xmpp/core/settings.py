import string
import random

from plone.registry.interfaces import IRegistry
from twisted.words.protocols.jabber.jid import JID
from zope.component import getUtility
from zope.interface import implements

from jarn.xmpp.core.interfaces import IXMPPSettings

chars = string.letters + string.digits


class XMPPSettings(object):

    implements(IXMPPSettings)

    def getUserJID(self, user_id):
        registry = getUtility(IRegistry)
        xmpp_domain = registry['jarn.xmpp.xmppDomain']
        return JID("%s@%s" % (user_id, xmpp_domain))

    def getUserPassword(self, user_id):
        if user_id == 'admin':
            return 'admin'
        else:
            # temp hack until I have a persistent password storage
            # if we need to create one:
            # return ''.join([random.choice(chars) for i in range(12)])
            return 'secret'
