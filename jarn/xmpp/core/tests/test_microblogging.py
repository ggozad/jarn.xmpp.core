import time
import transaction
import unittest2 as unittest

from plone.testing.z2 import Browser
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

from jarn.xmpp.twisted.testing import wait_on_client_deferreds

from jarn.xmpp.core.interfaces import IAdminClient
from jarn.xmpp.core.interfaces import IPubSubStorage
from jarn.xmpp.core.testing import XMPPCORE_FUNCTIONAL_TESTING


class MicroBloggingTests(unittest.TestCase):

    layer = XMPPCORE_FUNCTIONAL_TESTING
    level = 2

    def test_publish_to_node(self):
        portal = self.layer['portal']
        client = getUtility(IAdminClient)

        # Add a member
        mt = getToolByName(portal, 'portal_membership')
        mt.addMember('stpeter', 'secret', ['Member'], [])
        wait_on_client_deferreds(client)
        transaction.commit()
        app = self.layer['app']
        portalURL = portal.absolute_url()
        browser = Browser(app)
        browser.addHeader('Authorization',
                          'Basic %s:%s' % ('stpeter', 'secret', ))
        browser.open(portalURL+'/@@pubsub-publish')
        browser.getControl('Node').value='stpeter'
        browser.getControl('Message').value='Hello pubsub'
        browser.getControl('Post').click()

        # This is the only case where we do not have a deferred to wait on,
        # as it's the DeferredClient that acts on behalf of the user.
        # Let's sleep it out.
        time.sleep(1.0)
        # Hopefully the pubsub events have been sent to the admin client...
        wait_on_client_deferreds(client)

        pubsub_storage = getUtility(IPubSubStorage)
        items = pubsub_storage.node_items
        self.assertTrue('stpeter' in items)
        self.assertEqual(1, len(items['stpeter']))

        personal_item = items['stpeter'][0]
        self.assertTrue('content' in personal_item)
        self.assertTrue('published' in personal_item)
        self.assertTrue('published' in personal_item)
        self.assertEqual(u'Hello pubsub', personal_item['content'])

        people_item = items['people'][0]
        self.assertEqual(people_item, personal_item)
