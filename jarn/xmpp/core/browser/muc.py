import random

from Products.Five.browser import BrowserView
from twisted.words.protocols.jabber.jid import JID
from zope.component import getUtility

from jarn.xmpp.core.interfaces import IXMPPSettings


class MUCView(BrowserView):

    def __init__(self, context, request):
        super(MUCView, self).__init__(context, request)
        room = request.get('room', None)
        if room is not None:
            self.room_jid = JID(room)
        else:
            room = random.randint(0, 4294967295)
            self.room_jid = getUtility(IXMPPSettings).ConferenceJID
            self.room_jid.user = room

    def mucSettings(self):
        return """
            pmcxmpp.muc.room ='%s';
        """ % self.room_jid.full()