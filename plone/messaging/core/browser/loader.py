import logging

from plone.app.layout.viewlets.common import ViewletBase
from plone.messaging.twisted.client import randomResource
from plone.messaging.twisted.httpb import BOSHClient
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from twisted.words.protocols.jabber.jid import JID
from zope.component import getUtility

from plone.messaging.core.interfaces import IXMPPSettings

logger = logging.getLogger('plone.messaging.core')


class XMPPLoader(ViewletBase):
    """
    """
    index = ViewPageTemplateFile('loader.pt')

    def update(self):
        super(XMPPLoader, self).update()
        self.settings = getUtility(IXMPPSettings)
        pm = getToolByName(self.context, 'portal_membership')
        self.user_id = pm.getAuthenticatedMember().getId()
        self.resource = randomResource()

    @property
    def bosh(self):
        return self.settings.BOSHUrl

    @property
    def jdomain(self):
        return self.settings.XMPPDomain

    @property
    def jid(self):
        return JID("%s@%s/%s" % (self.user_id, self.jdomain, self.resource))

    @property
    def jpassword(self):
        return self.settings.getUserPassword(self.user_id)

    @property
    def pubsub_jid(self):
        return self.settings.PubSubJID

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
            var pmcxmpp = {
              connection : null,
              BOSH_SERVICE : '%s',
              rid: %i,
              sid: '%s',
              jid : '%s',
              pubsub_jid : '%s',
            };
            """ % (self.bosh, int(rid), sid, self.jid.full(), self.pubsub_jid)
        else:
            logger.info('Could not pre-bind %s' % self.jid.full())
            return """
            var pmcxmpp = {
              connection : null,
              BOSH_SERVICE : '%s',
              jid : '%s',
              password : '%s',
              pubsub_jid : '%s',
            };
            """ % (self.bosh, self.jid.userhost(), self.jpassword, self.pubsub_jid)
