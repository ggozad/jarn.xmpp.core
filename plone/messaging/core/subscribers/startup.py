from zope.component import getUtility
from plone.messaging.twisted.client import Admin
from plone.messaging.twisted.interfaces import IJabberClient
from plone.messaging.core.interfaces import IXMPPSettings
from twisted.words.protocols.jabber.jid import JID


def announceStart(event):
    from plone.messaging.core.pubsub import createNode, deleteNode, \
    subscribeUserToNode, publishItemToNode, getNodeAffiliations, setNodeAffiliations
    #test = deleteNode('testing')
    #test = createNode('testing', access_model='open')
    #test = subscribeUserToNode('testing', 'areviewer')
    publishItemToNode('testing', 'Hello world!', 'areviewer')
    return

    def cb2(res):
        import pdb; pdb.set_trace( )

    def cb(res):
        import pdb; pdb.set_trace( )
        res2 = setNodeAffiliations('testing',
            [(JID(u'areviewer@localhost'), u'publisher')])
        res2.addCallback(cb2)
        return res2

    d = getNodeAffiliations('testing')
    d.addCallback(cb)
    return d
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
