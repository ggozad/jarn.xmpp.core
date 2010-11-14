import unittest2 as unittest
from zope.component import getUtility
from twisted.internet import defer
from plone.messaging.core.testing import PMCORE_INTEGRATION_TESTING

class SubscriberTests(unittest.TestCase):

    layer = PMCORE_INTEGRATION_TESTING

    def test_add_user(self):
        portal = self.layer['portal']
        d = portal.portal_membership.addMember('joebar', 'secret', ['Member'], [])