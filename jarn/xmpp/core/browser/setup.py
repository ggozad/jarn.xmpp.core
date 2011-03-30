import logging

from Products.ATContentTypes.interface import IATContentType
from Products.CMFCore.utils import getToolByName
from z3c.form import form
from z3c.form import field
from z3c.form import button
from zope.component import getUtility
from zope.interface import Interface

from jarn.xmpp.core import messageFactory as _
from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IXMPPPasswordStorage
from jarn.xmpp.core.interfaces import IXMPPUsers
from jarn.xmpp.core.subscribers.startup import populatePubSubStorage
from jarn.xmpp.core.utils.setup import setupXMPPEnvironment

logger = logging.getLogger('jarn.xmpp.core')


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

        xmpp_users = getUtility(IXMPPUsers)
        pass_storage = getUtility(IXMPPPasswordStorage)
        mt = getToolByName(self.context, 'portal_membership')
        member_ids = mt.listMemberIds()
        member_jids = []
        member_passwords = {}
        pass_storage.clear()
        for member_id in member_ids:
            member_jid = xmpp_users.getUserJID(member_id)
            member_jids.append(member_jid)
            member_passwords[member_jid] = pass_storage.set(member_id)

        admin = getUtility(IAdminClient)

        def initPubSubStorage(result):
            d = populatePubSubStorage()
            return d

        d = setupXMPPEnvironment(admin, member_jids, member_passwords)
        d.addCallback(initPubSubStorage)
        return d
