from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.registry.interfaces import IRegistry
from plone.testing import z2
from twisted.words.protocols.jabber.jid import JID
from zope.component import getUtility
from zope.configuration import xmlconfig

from jarn.xmpp.twisted.interfaces import IZopeReactor
from jarn.xmpp.twisted.testing import REACTOR_FIXTURE, NO_REACTOR_FIXTURE
from jarn.xmpp.twisted.testing import wait_on_client_deferreds
from jarn.xmpp.twisted.testing import wait_for_client_state

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.subscribers.startup import setupAdminClient
from jarn.xmpp.core.utils.setup import setupXMPPEnvironment


class XMPPCoreNoReactorFixture(PloneSandboxLayer):

    defaultBases = (NO_REACTOR_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import jarn.xmpp.core
        import pas.plugins.userdeletedevent

        xmlconfig.file('configure.zcml', jarn.xmpp.core,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', pas.plugins.userdeletedevent,
                       context=configurationContext)
        z2.installProduct(app, 'pas.plugins.userdeletedevent')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'jarn.xmpp.core:default')
        registry = getUtility(IRegistry)
        registry['jarn.xmpp.adminJID'] = 'admin@localhost'
        registry['jarn.xmpp.pubsubJID'] = 'pubsub.localhost'
        registry['jarn.xmpp.conferenceJID'] = 'conference.localhost'
        registry['jarn.xmpp.xmppDomain'] = 'localhost'

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'pas.plugins.userdeletedevent')


XMPPCORE_NO_REACTOR_FIXTURE = XMPPCoreNoReactorFixture()

XMPPCORE_NO_REACTOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(XMPPCORE_NO_REACTOR_FIXTURE, ),
    name="XMPPCoreNoReactorFixture:Integration")
XMPPCORE_NO_REACTOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(XMPPCORE_NO_REACTOR_FIXTURE, ),
    name="XMPPCoreNoReactorFixture:Functional")


def _doNotUnregisterOnDisconnect(event):
    pass


class XMPPCoreFixture(PloneSandboxLayer):

    defaultBases = (REACTOR_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import jarn.xmpp.core
        import pas.plugins.userdeletedevent

        # Normally on a client disconnect we unregister the AdminClient
        # utility. We can't do that here as we need to disconnect the
        # client and clean up to keep twisted happy.
        jarn.xmpp.core.subscribers.startup.adminDisconnected = \
            _doNotUnregisterOnDisconnect

        xmlconfig.file('configure.zcml', jarn.xmpp.core,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', pas.plugins.userdeletedevent,
                       context=configurationContext)
        z2.installProduct(app, 'pas.plugins.userdeletedevent')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'jarn.xmpp.core:default')
        registry = getUtility(IRegistry)
        registry['jarn.xmpp.adminJID'] = 'admin@localhost'
        registry['jarn.xmpp.pubsubJID'] = 'pubsub.localhost'
        registry['jarn.xmpp.conferenceJID'] = 'conference.localhost'
        registry['jarn.xmpp.xmppDomain'] = 'localhost'
        setupAdminClient(None, None)
        client = getUtility(IAdminClient)
        wait_for_client_state(client, 'authenticated')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'pas.plugins.userdeletedevent')

    def testSetUp(self):
        client = getUtility(IAdminClient)
        if client._state == 'disconnected':
            zr = getUtility(IZopeReactor)
            zr.reactor.callFromThread(client.connect)

        wait_for_client_state(client, 'authenticated')
        setupXMPPEnvironment(client,
            member_jids=[JID('test_user_1_@localhost')],
            member_passwords={JID('test_user_1_@localhost'): 'secret'})
        wait_on_client_deferreds(client)

    def testTearDown(self):
        client = getUtility(IAdminClient)
        client.disconnect()
        wait_for_client_state(client, 'disconnected')


XMPPCORE_FIXTURE = XMPPCoreFixture()

XMPPCORE_INTEGRATION_TESTING = IntegrationTesting(bases=(XMPPCORE_FIXTURE, ),
    name="XMPPCoreFixture:Integration")
XMPPCORE_FUNCTIONAL_TESTING = FunctionalTesting(bases=(XMPPCORE_FIXTURE, ),
    name="XMPPCoreFixture:Functional")
