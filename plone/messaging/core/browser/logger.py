from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class XMPPLogger(ViewletBase):
    """
    """
    index = ViewPageTemplateFile('logger.pt')