from zope.component import getUtility
from zope.component import getGlobalSiteManager

from plone.messaging.twisted.client import Admin
from plone.messaging.twisted.interfaces import IDeferredXMPPClient

from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.interfaces import IPubSubClient
from plone.messaging.core.pubsub import PubSubClient


def setupPubSubClient(event):
    gsm = getGlobalSiteManager()
    gsm.registerUtility(PubSubClient(), IPubSubClient)


def pubsubConnected(event):
    pubsub = event.object
    #pubsub.createNode('gogonode')
    #pubsub.deleteNode('gogonode')

    def cb(result):
        import pdb; pdb.set_trace( )
    #d = pubsub.getNodeItems('testing')
    #d.addCallback(cb)

def announceStart(event):
    client = getUtility(IDeferredXMPPClient)
    jsettings = getUtility(IXMPPSettings)
    jid = jsettings.getUserJID('admin')
    password = jsettings.getUserPassword('admin')

    def announceStart(xmlstream):
        result = xmlstream.factory.streamManager. \
            handlers[0].sendAnnouncement("Instance started.")
        return result

    d = client.execute(jid, password, announceStart, extra_handlers=[Admin()])
    return d
