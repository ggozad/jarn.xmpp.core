from zope.component import getUtility
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.messaging.core.interfaces import IXMPPSettings


class XMPPLoader(ViewletBase):
    """
    """
    index = ViewPageTemplateFile('loader.pt')

    def update(self):
        super(XMPPLoader, self).update()
        self.settings = getUtility(IXMPPSettings)
        pm = getToolByName(self.context, 'portal_membership')
        self.user_id = pm.getAuthenticatedMember().getId()

    @property
    def bosh(self):
        return self.settings.BOSHUrl

    @property
    def jdomain(self):
        return self.settings.XMPPDomain

    @property
    def jid(self):
        return "%s@%s" % (self.user_id, self.jdomain)

    @property
    def jpassword(self):
        return self.settings.getUserPassword(self.user_id)

    def boshSettings(self):
        script = """
        var pmcxmpp = {
          connection : null,
          BOSH_SERVICE : '%s',
          jid : '%s',
          password : '%s',
        };
        """ % (self.bosh, self.jid, self.jpassword)
        return script
