import logging

from z3c.form import form
from z3c.form import field
from z3c.form import button
from zope.interface import Interface

from jarn.xmpp.core import messageFactory as _
from jarn.xmpp.core.utils.setup import setupXMPPEnvironment

logger = logging.getLogger('jarn.xmpp.core')


class ISetupXMPP(Interface):
    pass


class SetupXMPPForm(form.Form):

    fields = field.Fields(ISetupXMPP)
    label = _("Setup XMPP")
    description = _("label_setup_warning",
        """
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
        setupXMPPEnvironment(self.context)
