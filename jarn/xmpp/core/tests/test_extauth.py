import unittest2 as unittest

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_PASSWORD

from jarn.xmpp.core.testing import XMPPCORE_NO_REACTOR_FUNCTIONAL_TESTING


class ExtAuthTests(unittest.TestCase):

    layer = XMPPCORE_NO_REACTOR_FUNCTIONAL_TESTING

    def test_plain_auth(self):
        portal = self.layer['portal']
        view = portal.restrictedTraverse('@@extauth')
        view = view.__of__(portal)
        result = view(TEST_USER_ID, TEST_USER_PASSWORD)
        self.assertTrue(result)

    def test_cookie_auth(self):
        portal = self.layer['portal']
        app = self.layer['app']
        from plone.app.testing import logout
        logout()
        browser = Browser(app)
        browser.handleErrors = False
        browser.open(portal.absolute_url() + '/login_form')
        browser.getControl(name='__ac_name').value = TEST_USER_ID
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name="submit").click()
        self.assertTrue(False, 'Somehow we have no cookies. Postpone for later.')
