import logging

from plone.registry.interfaces import IRegistry
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from twisted.words.protocols.jabber.jid import JID
from zope.component import getUtility

from jarn.xmpp.twisted.client import randomResource
from jarn.xmpp.twisted.httpb import BOSHClient

from jarn.xmpp.core.interfaces import IXMPPSettings

logger = logging.getLogger('jarn.xmpp.core')


class XMPPLoader(ViewletBase):
    """
    """

    def update(self):
        super(XMPPLoader, self).update()
        self.settings = getUtility(IXMPPSettings)
        self.registry = getUtility(IRegistry)
        pm = getToolByName(self.context, 'portal_membership')
        self.user_id = pm.getAuthenticatedMember().getId()
        self.resource = randomResource()

    @property
    def bosh(self):
        return self.registry['jarn.xmpp.boshURL']

    @property
    def jdomain(self):
        return self.registry['jarn.xmpp.xmppDomain']

    @property
    def jid(self):
        return JID("%s@%s/%s" % (self.user_id, self.jdomain, self.resource))

    @property
    def jpassword(self):
        return self.settings.getUserPassword(self.user_id)

    @property
    def pubsub_jid(self):
        return self.registry['jarn.xmpp.pubsubJID']

    def prebind(self):
        b_client = BOSHClient(self.jid, self.jpassword, self.bosh)
        if b_client.startSession():
            return b_client.rid, b_client.sid
        return ('', '')

    def boshSettings(self):
        if not self.user_id:
            return ""
        rid, sid = self.prebind()
        if rid and sid:
            logger.info('Pre-binded %s' % self.jid.full())

            return """
            var jarnxmpp = {
              connection : null,
              BOSH_SERVICE : '%s',
              rid: %i,
              sid: '%s',
              jid : '%s',
              pubsub_jid : '%s',
            };
            """ % (self.bosh, int(rid), sid, self.jid.full(), self.pubsub_jid)
        else:
            logger.error('Could not pre-bind %s' % self.jid.full())
            return """
            var jarnxmpp = {
              connection : null,
              BOSH_SERVICE : '%s',
              jid : '%s',
              password : '%s',
              pubsub_jid : '%s',
            };
            """ % (self.bosh,
                   self.jid.userhost(),
                   self.jpassword,
                   self.pubsub_jid)
