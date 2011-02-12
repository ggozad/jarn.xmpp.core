import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

from jarn.xmpp.twisted.testing import wait_on_deferred

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.testing import XMPPCORE_INTEGRATION_TESTING
from jarn.xmpp.core.utils.pubsub import getAllChildNodes


class LayerSetupTests(unittest.TestCase):

    layer = XMPPCORE_INTEGRATION_TESTING

    def test_nodes(self):
        portal = self.layer['portal']
        mt = getToolByName(portal, 'portal_membership')
        member_ids = set(mt.listMemberIds())

        client = getUtility(IAdminClient)
        d = getAllChildNodes(client, None)
        self.assertTrue(wait_on_deferred(d))
        tree = d.result

        self.assertEqual(tree[''], ['content', 'people'])
        self.assertTrue(member_ids.issubset(set(tree['people'])))
        self.assertEqual(tree['content'], ['dummy_content_node'])
