from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class XMPPViewlet(ViewletBase):

    implements(IViewlet)
    index = ViewPageTemplateFile('viewlet.pt')

    def __init__(self, context, request, view, manager=None):
        super(XMPPViewlet, self).__init__(context, request, view, manager=manager)

    def update(self):
        super(XMPPViewlet, self).update()
        self.anonymous = self.portal_state.anonymous()
        if not self.anonymous:
            member = self.portal_state.member()
            self.pubsub_node = member.getId()

    def personal_node(self):
        return self.pubsub_node
