import unittest2 as unittest

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

from jarn.xmpp.twisted.testing import wait_on_deferred
from jarn.xmpp.twisted.testing import wait_on_client_deferreds

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IXMPPPasswordStorage
from jarn.xmpp.core.testing import XMPPCORE_INTEGRATION_TESTING
from jarn.xmpp.core.utils.pubsub import getAllChildNodes


class UserManagementTests(unittest.TestCase):

    layer = XMPPCORE_INTEGRATION_TESTING
    level = 2

    def test_add_delete_user(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        client = getUtility(IAdminClient)

        mt = getToolByName(portal, 'portal_membership')
        mt.addMember('stpeter', 'secret', ['Member'], [])
        wait_on_client_deferreds(client)

        # User has been added
        d = client.admin.getRegisteredUsers()
        self.assertTrue(wait_on_deferred(d))
        user_jids = [user_dict['jid'] for user_dict in d.result]
        self.assertTrue('stpeter@localhost' in user_jids)

        # User's pubsub node has been added
        d = getAllChildNodes(client, 'people')
        self.assertTrue(wait_on_deferred(d))
        self.assertTrue('stpeter' in d.result['people'])
        pass_storage = getUtility(IXMPPPasswordStorage)
        self.assertTrue(pass_storage.get('stpeter') is not None)

        mt.deleteMembers('stpeter')
        wait_on_client_deferreds(client)
        # User has been deleted
        d = client.admin.getRegisteredUsers()
        wait_on_client_deferreds(client)
        user_jids = [user_dict['jid'] for user_dict in d.result]
        self.assertTrue('stpeter@localhost' not in user_jids)
        self.assertTrue(pass_storage.get('stpeter') is None)

        # User's pubsub node has been removed
        d = getAllChildNodes(client, 'people')
        wait_on_client_deferreds(client)
        self.assertTrue('stpeter' not in d.result['people'])
