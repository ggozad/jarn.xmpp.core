from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class XMPPLoader(ViewletBase):
    """
    """
    index = ViewPageTemplateFile('loader.pt')