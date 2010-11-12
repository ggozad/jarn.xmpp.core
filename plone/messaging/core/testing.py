from zope.configuration import xmlconfig
from plone.testing import z2
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.messaging.twisted.testing import REACTOR_FIXTURE


class PMCoreFixture(PloneSandboxLayer):

    defaultBases = (REACTOR_FIXTURE, PLONE_FIXTURE)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.messaging.core
        import pas.plugins.userdeletedevent
        xmlconfig.file('configure.zcml', plone.messaging.core, context=configurationContext)
        xmlconfig.file('configure.zcml', pas.plugins.userdeletedevent, context=configurationContext)
        z2.installProduct(app, 'pas.plugins.userdeletedevent')

    def setUpPloneSite(self, portal):
            # Install into Plone site using portal_setup
            applyProfile(portal, 'plone.messaging.core:default')

    def tearDownZope(self, app):
            # Uninstall product
            z2.uninstallProduct(app, 'pas.plugins.userdeletedevent')

PMCORE_FIXTURE = PMCoreFixture()

PMCORE_INTEGRATION_TESTING = IntegrationTesting(bases=(PMCORE_FIXTURE,), name="PMCoreFixture:Integration")
PMCORE_FUNCTIONAL_TESTING = FunctionalTesting(bases=(PMCORE_FIXTURE,), name="PMCoreFixture:Functional")
