from zope.component import getUtility
from twisted.words.protocols.jabber.jid import JID
from plone.messaging.twisted import clients

def connectAdminAccount(event):
    reactor = event.object
    jid = JID("admin@localhost")
    password = 'admin'
    admin = clients.adminClientFactory(jid, password)
    factory = admin.factory
    reactor.connectTCP("localhost", 5222, factory)

def onUserCreation(event):
    principal = event.principal
