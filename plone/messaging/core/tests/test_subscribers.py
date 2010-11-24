from twisted.trial import unittest
from plone.messaging.core.testing import PMCORE_INTEGRATION_TESTING
import twisted
twisted.internet.base.DelayedCall.debug = True

class SubscriberTests(unittest.TestCase):

    layer = PMCORE_INTEGRATION_TESTING

    def test_add_user(self):
        portal = self.layer['portal']
        #portal.portal_membership.addMember('joe', 'secret', ('Member',), [])
        from zope.event import notify
        from Products.PluggableAuthService.events import PrincipalCreated
        from AccessControl import getSecurityManager
        user = getSecurityManager().getUser()
        ev = PrincipalCreated(user)
        from plone.messaging.core.subscribers import onUserCreation
        def res(result):
            self.assertEqual(result, True)
        d = onUserCreation(ev)
        d.addCallback(res)
        return d