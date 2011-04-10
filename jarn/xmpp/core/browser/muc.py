import random

from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from twisted.words.protocols.jabber.jid import JID
from zope.component import getUtility


class MUCView(BrowserView):

    def __init__(self, context, request):
        super(MUCView, self).__init__(context, request)
        room = request.get('room', None)
        if room is not None:
            self.room_jid = JID(room)
        else:
            room = random.randint(0, 4294967295)
            registry = getUtility(IRegistry)
            self.room_jid = JID(registry['jarn.xmpp.conferenceJID'])
            self.room_jid.user = room

    def mucSettings(self):
        return """
            $(document).ready(function () {
            jarnxmpp.muc.room ='%s';
            });
        """ % self.room_jid.full()