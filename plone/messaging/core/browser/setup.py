from z3c.form import form
from z3c.form import field
from z3c.form import button

from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.component import getUtility
from zope.interface import Interface

from plone.messaging.core import messageFactory as _
from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.setuphandlers import createDefaultPubSubNodes


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

    def __init__(self, context, request, node=None):
        super(SetupXMPPForm, self).__init__(context, request)
        self.settings = getUtility(IXMPPSettings)
        self.admin = getUtility(IAdminClient)

    @button.buttonAndHandler(_('Setup'), name='setup_xmpp')
    def setup_xmpp(self, action):
        data, errors = self.extractData()
        import pdb; pdb.set_trace( )