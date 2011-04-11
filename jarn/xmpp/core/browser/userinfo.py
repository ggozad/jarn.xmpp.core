import json

from AccessControl import Unauthorized
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class XMPPUserInfoView(BrowserView):

    def __call__(self, user_id):
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized
        info = pm.getMemberInfo(user_id)
        if info is None:
            return None
        fullname = info.get('fullname') or user_id
        portrait_url = pm.getPersonalPortrait(user_id).absolute_url()
        return json.dumps({'fullname': fullname, 'portrait_url': portrait_url})
