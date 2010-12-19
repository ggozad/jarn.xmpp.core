from twisted.internet import reactor
from twisted.trial import unittest
from Products.PluggableAuthService.events import PrincipalCreated
from AccessControl import getSecurityManager
from plone.messaging.core.subscribers.user_management import onUserCreation
from plone.messaging.core.testing import PMCORE_INTEGRATION_TESTING


class SubscriberTests(unittest.TestCase):

    layer = PMCORE_INTEGRATION_TESTING

    def cleanup(self):
        # XXX
        # Clean up hanging DelayedCalls that originate from twisted.
        # <bound method Resolver.maybeParseConfig of <twisted.names.client.Resolver instance at ...>>
        # Go figure...
        for delayed_call in reactor.getDelayedCalls():
            delayed_call.cancel()

    def test_add_user(self):
        self.addCleanup(self.cleanup)

        user = getSecurityManager().getUser()
        ev = PrincipalCreated(user)
        d = onUserCreation(ev)

        def res(result):
            self.assertEqual(result, True)

        d.addCallback(res)
        return d
