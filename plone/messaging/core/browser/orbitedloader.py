from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class OrbitedLoader(ViewletBase):
    """
    """
    index = ViewPageTemplateFile('orbitedloader.pt')