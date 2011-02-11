from plone.portlets.interfaces import IPortletDataProvider
from zope.component import getMultiAdapter
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base

class IOnlineUsers(IPortletDataProvider):
    """A portlet which displays online users.
    """

class Assignment(base.Assignment):
    implements(IOnlineUsers)

    title = u'Online users'

class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')

    @property
    def available(self):
        return not self.portal_state.anonymous()

    render = ViewPageTemplateFile('onlineusers.pt')

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
