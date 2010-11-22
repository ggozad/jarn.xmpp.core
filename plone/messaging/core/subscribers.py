from zope.component import getUtility
from zope.component import getSiteManager
from plone.messaging.core.jabberadmin import JabberAdmin
from plone.messaging.core.interfaces import IJabberAdmin


def initJabberAdmin(event):
    reactor = event.object
    sm = getSiteManager()
    jabber_admin = JabberAdmin(reactor)
    sm.registerUtility(jabber_admin, IJabberAdmin)
    d, admin = jabber_admin.getAdminClientDeferred()
    from twisted.internet import reactor, defer
    pd = defer.Deferred()
    from wokkel.xmppim import AvailablePresence

    def sendPresence(res):
        admin.send(AvailablePresence(priority=-10))
        admin.addUser('asd@localhost', 'asdasd')
    pd.addCallback(sendPresence)
    d.chainDeferred(pd)
    #import pdb; pdb.set_trace( )
def onUserCreation(event):
    """Create a jabber account for new user
    """
    principal = event.principal
    jabber_admin = getUtility(IJabberAdmin).getAdminClient()

    def genPasswd():
        import string
        import random
        chars = string.letters + string.digits
        return ''.join([random.choice(chars) for i in range(12)])

    jid = u'%s@%s' % (principal.getUserId(), jabber_admin.parent.jid.host)
    jabber_admin.addUser(jid, genPasswd())


def onUserDeletion(event):
    principal = event.principal
    jabber_admin = getUtility(IJabberAdmin).getAdminClient()
    jid = u'%s@%s' % (principal, jabber_admin.parent.jid.host)
    jabber_admin.deleteUsers([jid])
