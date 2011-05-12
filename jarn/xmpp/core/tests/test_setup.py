import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

from jarn.xmpp.twisted.testing import wait_on_client_deferreds

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.testing import XMPPCORE_INTEGRATION_TESTING
from jarn.xmpp.core.utils.pubsub import getAllChildNodes


class LayerSetupTests(unittest.TestCase):

    layer = XMPPCORE_INTEGRATION_TESTING
    level = 2

    def test_nodes(self):
        portal = self.layer['portal']
        mt = getToolByName(portal, 'portal_membership')
        member_ids = set(mt.listMemberIds())

        client = getUtility(IAdminClient)
        d = getAllChildNodes(client, None)
        wait_on_client_deferreds(client)
        tree = d.result

        self.assertEqual(tree[''], ['people'])
        self.assertTrue(member_ids.issubset(set(tree['people'])))
