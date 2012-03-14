import json

from zope.component import getUtility

from twisted.words.protocols.jabber.jid import JID

from AccessControl import Unauthorized
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from jarn.xmpp.core.interfaces import INodeEscaper


class XMPPUserInfo(BrowserView):

    def __call__(self, user_id):
        user_id = getUtility(INodeEscaper).unescape(user_id)
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized
        info = pm.getMemberInfo(user_id)
        if info is None:
            return None
        fullname = info.get('fullname') or user_id
        portrait_url = pm.getPersonalPortrait(user_id).absolute_url()

        response = self.request.response
        response.setHeader('content-type', 'application/json')
        response.setBody(json.dumps({'fullname': fullname,
                                     'portrait_url': portrait_url}))
        return response


class XMPPUserDetails(BrowserView):

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.jid = request.get('jid')
        self.user_id = getUtility(INodeEscaper).unescape(JID(self.jid).user)
        self.bare_jid = JID(self.jid).userhost()
        self.pm = getToolByName(context, 'portal_membership')
        info = self.pm.getMemberInfo(self.user_id)
        if info:
            self._fullname = info.get('fullname') or self.user_id
            self._portrait_url = self.pm.getPersonalPortrait(self.user_id).absolute_url()
        else:
            self._fullname = ''
            self._portrait_url = ''

    @property
    def fullname(self):
        return self._fullname

    @property
    def portrait_url(self):
        return self._portrait_url
