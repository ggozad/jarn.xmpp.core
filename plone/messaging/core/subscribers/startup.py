from zope.component import getUtility
from plone.messaging.twisted.client import Admin
from plone.messaging.twisted.interfaces import IJabberClient
from plone.messaging.core.interfaces import IXMPPSettings


def announceStart(event):
    from plone.messaging.core.pubsub import createNode, deleteNode
    #test = createNode('testing123', access_model='open')
    test = deleteNode('testing123')
    return
    client = getUtility(IJabberClient)
    jsettings = getUtility(IXMPPSettings)
    jid = jsettings.getUserJID('admin')
    password = jsettings.getUserPassword('admin')

    def announceStart(xmlstream):
        result = xmlstream.factory.streamManager. \
            handlers[0].sendAnnouncement("Instance started.")
        return result

    d = client.execute(jid, password, announceStart, extra_handlers=[Admin()])
    return d
