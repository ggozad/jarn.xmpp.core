import logging
import json

from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.component import queryUtility

from jarn.xmpp.twisted.client import randomResource
from jarn.xmpp.twisted.httpb import BOSHClient

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IXMPPUsers

logger = logging.getLogger('jarn.xmpp.core')


class XMPPLoader(BrowserView):
    """
    """

    @property
    def available(self):
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

        self.xmpp_users = getUtility(IXMPPUsers)
        self.jid = self.xmpp_users.getUserJID(self.user_id)
        self.jid.resource = randomResource()
        self.jpassword = self.xmpp_users.getUserPassword(self.user_id)
        if self.jpassword is None:
            self._available = False
            return

        self.registry = getUtility(IRegistry)
        try:
            self.pubsub_jid = self.registry['jarn.xmpp.pubsubJID']
        except KeyError:
            self._available = False

        return self._available

    @property
    def bosh(self):
        return getToolByName(self.context, 'portal_url')() + '/http-bind'

    def prebind(self):
        b_client = BOSHClient(self.jid, self.jpassword, self.bosh)
        if b_client.startSession():
            return b_client.rid, b_client.sid
        return ('', '')

    def __call__(self):
        bosh_credentials = {}
        if self.available:
            rid, sid = self.prebind()
            if rid and sid:
                logger.info('Pre-binded %s' % self.jid.full())
                bosh_credentials = {
                    'BOSH_SERVICE': self.bosh,
                    'rid': int(rid),
                    'sid': sid,
                    'jid': self.jid.full(),
                    'pubsub_jid': self.pubsub_jid}

        response = self.request.response
        response.setHeader('content-type', 'application/json')
        response.setBody(json.dumps(bosh_credentials))
        return response
