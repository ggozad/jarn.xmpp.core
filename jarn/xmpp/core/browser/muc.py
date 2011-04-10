import random

from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from twisted.words.protocols.jabber.jid import JID
from zope.component import getUtility


class MUCView(BrowserView):

    def __init__(self, context, request):
        super(MUCView, self).__init__(context, request)
        room = request.get('room', None)
        self.invitee = request.get('invitee', None)
        if room is not None:
            self.room_jid = JID(room)
        else:
            room = random.randint(0, 4294967295)
            registry = getUtility(IRegistry)
            self.room_jid = JID(registry['jarn.xmpp.conferenceJID'])
            self.room_jid.user = room

    def mucSettings(self):
        script = "jarnxmpp.muc.joinRoom('%s');" % self.room_jid.full()
        if self.invitee:
            script+="jarnxmpp.muc.inviteToRoom('%s');" % self.invitee
        return script