import logging

from plone.registry.interfaces import IRegistry
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.component import queryUtility

from jarn.xmpp.twisted.client import randomResource
from jarn.xmpp.twisted.httpb import BOSHClient

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IXMPPSettings

logger = logging.getLogger('jarn.xmpp.core')


class XMPPLoader(ViewletBase):
    """
    """

    def update(self):
        super(XMPPLoader, self).update()
        self._available = True
        client = queryUtility(IAdminClient)
        if client is None:
            self._available = False
            return

        pm = getToolByName(self.context, 'portal_membership')
        self.user_id = pm.getAuthenticatedMember().getId()
        if self.user_id is None:
            self._available = False
            return
        self.settings = getUtility(IXMPPSettings)
        self.jid = self.settings.getUserJID(self.user_id)
        self.jid.resource = randomResource()
        self.jpassword = self.settings.getUserPassword(self.user_id)

        self.registry = getUtility(IRegistry)
        try:
            self.bosh = self.registry['jarn.xmpp.boshURL']
            self.pubsub_jid = self.registry['jarn.xmpp.pubsubJID']
        except KeyError:
            self._available = False

    @property
    def available(self):
        return self._available

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
