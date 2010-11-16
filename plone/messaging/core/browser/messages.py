from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Messages(ViewletBase):
    """
    """
    index = ViewPageTemplateFile('messages.pt')
