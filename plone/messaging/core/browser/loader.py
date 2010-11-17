from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
class XMPPLoader(ViewletBase):
    """
    """
    index = ViewPageTemplateFile('loader.pt')

    @property
    def bosh(self):
        # XXX: Should go to registry
        return 'http://localhost:8080/http-bind/'

    @property
    def jdomain(self):
        # XXX: Should go to registry
        return 'localhost'

    @property
    def jid(self):
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember().getId()
        return "%s@%s" % (user, self.jdomain)

    @property
    def jpassword(self):
        # XXX: Should go to registry
        return 'admin'

    def settings(self):
        script = """
        var pmcxmpp = {
          connection : null,
          BOSH_SERVICE : '%s',
          jid : '%s',
          password : '%s',
        };
        """ % (self.bosh, self.jid, self.jpassword)
        return script