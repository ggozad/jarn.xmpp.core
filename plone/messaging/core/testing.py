import commands
from zope.configuration import xmlconfig
from plone.testing import z2, Layer
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.messaging.twisted.testing import REACTOR_FIXTURE
from plone.app.testing import ploneSite
from plone.app.testing import pushGlobalRegistry
from plone.app.testing import popGlobalRegistry

class EJabberdLayer(Layer):

    def setUp(self):
        """Start ejabberd
        Hopefully, the tests are run through the current buildout, which also
        installs ejabberd...
        """
        import os
        if 'EJABBERDCTL' in os.environ:
            self.ejabberdctl = os.environ['EJABBERDCTL']
        else:
            print """
            You need to make available a running ejabberd server in order
            to run the functional tests, as well as give the user with JID
            admin@localhost administrator privileges. Make sure the environment
            variable EJABBERDCTL is set pointing to the ejabberdctl command path.
            Aborting tests...
            """
            exit(1)

        # Remove all users
        self._delAllUsers()
        addadmin = "%s register admin localhost admin" % self.ejabberdctl
        commands.getoutput(addadmin)

    def tearDown(self):
        pass

    def testSetUp(self):
        self._delAllUsers(exceptions=['admin'])

    def testTearDown(self):
        self._delAllUsers(exceptions=['admin'])

    def _delAllUsers(self, exceptions=[]):
        listusers = "%s registered_users localhost" % self.ejabberdctl
        users = commands.getoutput(listusers).split()
        for user in users:
            if user not in exceptions:
                deluser = "%s unregister %s localhost" % \
                           (self.ejabberdctl, user)
                commands.getoutput(deluser)


EJABBERD_LAYER = EJabberdLayer()


class PMCoreFixture(PloneSandboxLayer):

    defaultBases = (REACTOR_FIXTURE,)

    def setUp(self):
        from plone.app.testing import ploneSite
        with ploneSite() as portal:
            pushGlobalRegistry(portal)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        print "CORE context: %s" %configurationContext
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

    def tearDown(self):

           with ploneSite() as portal:
               popGlobalRegistry(portal)
PMCORE_FIXTURE = PMCoreFixture()

PMCORE_INTEGRATION_TESTING = IntegrationTesting(bases=(PMCORE_FIXTURE,), name="PMCoreFixture:Integration")
PMCORE_FUNCTIONAL_TESTING = FunctionalTesting(bases=(PMCORE_FIXTURE,), name="PMCoreFixture:Functional")
