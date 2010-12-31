from zope.component import getGlobalSiteManager

from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.client import AdminClient


def setupAdminClient(event):
    gsm = getGlobalSiteManager()
    gsm.registerUtility(AdminClient(), IAdminClient)


def adminConnected(event):
    client = event.object
    client.admin.sendAnnouncement("Instance started")
