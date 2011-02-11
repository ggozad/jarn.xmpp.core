import logging

from Products.ATContentTypes.interface import IATContentType
from Products.CMFCore.utils import getToolByName
from z3c.form import form
from z3c.form import field
from z3c.form import button
from zope.component import getUtility
from zope.interface import Interface

from plone.messaging.core import messageFactory as _
from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.subscribers.startup import populatePubSubStorage
from plone.messaging.core.utils.setup import setupXMPPEnvironment

logger = logging.getLogger('plone.messaging.core')


class ISetupXMPP(Interface):
    pass


class SetupXMPPForm(form.Form):

    fields = field.Fields(ISetupXMPP)
    label = _("Setup XMPP")
    description = _("""
        Warning: This action should ONLY be run after the initial setup. It
        will create the necessary users and nodes on your XMPP server
        according to your plone site users. Unless you know what you are doing
        you do not need to run it again afterwards.
        Make sure you have set the correct settings for you XMPP server before
        submitting.
        """)

    ignoreContext = True

    @button.buttonAndHandler(_('Setup'), name='setup_xmpp')
    def setup_xmpp(self, action):
        data, errors = self.extractData()

        jsettings = getUtility(IXMPPSettings)
        ct = getToolByName(self.context, 'portal_catalog')
        content_nodes = [brain.UID for brain in
                         ct.unrestrictedSearchResults(
                            object_provides=IATContentType.__identifier__)]
        mt = getToolByName(self.context, 'portal_membership')
        member_ids = mt.listMemberIds()
        member_jids = []
        member_passwords = {}
        for member_id in member_ids:
            member_jid = jsettings.getUserJID(member_id)
            member_jids.append(member_jid)
            member_passwords[member_jid] = jsettings.getUserPassword(member_id)

        admin = getUtility(IAdminClient)

        def initPubSubStorage(result):
            d = populatePubSubStorage()
            return d

        d = setupXMPPEnvironment(admin,
                             member_jids, member_passwords,
                             content_nodes)
        d.addCallback(initPubSubStorage)
        return d