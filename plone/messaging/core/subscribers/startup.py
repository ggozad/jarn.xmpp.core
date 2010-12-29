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

    def cb(result):
        import pdb; pdb.set_trace( )

    d = pubsub.getDefaultNodeConfiguration()
    d.addCallback(cb)
    return
    def ccb(result):

        def icb(result):
            import pdb; pdb.set_trace( )
            pubsub.deleteNode('gogonode')

        d2 = pubsub.getNodeType('gogonode')
        d2.addCallback(icb)
        return d2

    d = pubsub.createNode('gogonode', options={'pubsub#node_type':'collection'})
    d.addCallback(ccb)

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
