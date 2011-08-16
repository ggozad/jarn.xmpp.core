import binascii
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from zope.publisher.browser import BrowserView


class ExtAuthView(BrowserView):

    def __call__(self, userid='', password=''):
        acl_users = getToolByName(self.context, 'acl_users')
        # Maybe a plain userid/password.
        if acl_users.authenticate(userid, password, {}):
            return True

        # Maybe it's the auth cookie value?
        creds = {}
        try:
            creds['cookie'] = binascii.a2b_base64(password)
        except binascii.Error:
            return False
        creds["source"]="plone.session"

        auth_plugins = acl_users.plugins.listPlugins(IAuthenticationPlugin)
        for plugin_id, plugin in auth_plugins:
            if plugin.authenticateCredentials(creds):
                return True
        return False
