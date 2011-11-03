import json

from twisted.words.protocols.jabber.jid import JID

from AccessControl import Unauthorized
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class XMPPUserProfile(BrowserView):
    pass
