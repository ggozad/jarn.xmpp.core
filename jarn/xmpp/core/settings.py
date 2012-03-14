import logging

from plone.registry.interfaces import IRegistry
from twisted.words.protocols.jabber.jid import JID
from zope.component import getUtility
from zope.interface import implements

from jarn.xmpp.core.interfaces import IXMPPPasswordStorage
from jarn.xmpp.core.interfaces import IXMPPUsers
from jarn.xmpp.core.interfaces import INodeEscaper

logger = logging.getLogger('jarn.xmpp.core')


class XMPPUsers(object):

    implements(IXMPPUsers)

    def getUserJID(self, user_id):
        registry = getUtility(IRegistry)
        xmpp_domain = registry['jarn.xmpp.xmppDomain']
        user_id = getUtility(INodeEscaper).escape(user_id)
        return JID("%s@%s" % (user_id, xmpp_domain))

    def getUserPassword(self, user_id):
        pass_storage = getUtility(IXMPPPasswordStorage)
        return pass_storage.get(user_id)
