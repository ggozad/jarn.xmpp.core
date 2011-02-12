import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

from jarn.xmpp.twisted.testing import wait_on_deferred
from jarn.xmpp.twisted.testing import wait_on_client_deferreds

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.testing import XMPPCORE_INTEGRATION_TESTING
from jarn.xmpp.core.utils.pubsub import getAllChildNodes


class UserManagementTests(unittest.TestCase):

    layer = XMPPCORE_INTEGRATION_TESTING

    def test_add_user(self):
        portal = self.layer['portal']
        rt = getToolByName(portal, 'portal_registration')
        user_properties = {'username': 'stpeter',
                           'fullname': 'Peter Saint-Andre',
                           'email': 'stpeter@jabber.org'}
        rt.addMember('stpeter', 'secret', properties=user_properties)
        client = getUtility(IAdminClient)
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
