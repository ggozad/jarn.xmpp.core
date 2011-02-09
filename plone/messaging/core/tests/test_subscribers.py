import unittest2 as unittest

from AccessControl import getSecurityManager
from Products.PluggableAuthService.events import PrincipalCreated
from plone.messaging.twisted.testing import wait_on_deferred

from plone.messaging.core.subscribers.user_management import onUserCreation
from plone.messaging.core.testing import PMCORE_INTEGRATION_TESTING


class SubscriberTests(unittest.TestCase):

    layer = PMCORE_INTEGRATION_TESTING

    def test_add_user(self):
        user = getSecurityManager().getUser()
        ev = PrincipalCreated(user)
        ddd = onUserCreation(ev)

        self.assertTrue(wait_on_deferred(ddd))
        self.assertTrue(ddd.result)

