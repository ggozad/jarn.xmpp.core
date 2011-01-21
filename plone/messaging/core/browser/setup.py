import logging

from twisted.internet import defer
from z3c.form import form
from z3c.form import field
from z3c.form import button
#from zope import schema
from zope.component import getUtility
from zope.interface import Interface

from plone.messaging.core import messageFactory as _
from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.interfaces import IXMPPSettings
from plone.messaging.core.interfaces import IPubSubStorage

logger = logging.getLogger('plone.messaging.core')


class ISetupXMPP(Interface):
    pass


class SetupXMPPForm(form.Form):

    fields = field.Fields(ISetupXMPP)
    label = _("Setup XMPP")
    description = _("""
        Warning: This action should ONLY be run after the initial setup. It
        will create the necessary users and nodes on your XMPP server
        according to your plone site users. Unless you know what you are doing
        you do not need to run it again afterwards.
        Make sure you have set the correct settings for you XMPP server before
        submitting.
        """)

    ignoreContext = True

    def __init__(self, context, request, node=None):
        super(SetupXMPPForm, self).__init__(context, request)
        self.settings = getUtility(IXMPPSettings)
        self.admin = getUtility(IAdminClient)

    @button.buttonAndHandler(_('Setup'), name='setup_xmpp')
    def setup_xmpp(self, action):
        data, errors = self.extractData()

        def deleteAllNodes(result):
            if result == []:
                return True
            d = defer.DeferredList(
                [self.admin.deleteNode(node_dict['node'])
                for node_dict in result],
                consumeErrors=True)
            return d

        def createCollections(result):
            if not result:
                return False
            d1 = self.admin.createNode('people',
                options={'pubsub#node_title': 'All personal feeds',
                         'pubsub#node_type': 'collection',
                         'pubsub#collection': ''})
            d2 = self.admin.createNode('content',
                options={'pubsub#node_title': 'All content feeds',
                         'pubsub#node_type': 'collection',
                         'pubsub#collection': ''})
            d = defer.DeferredList([d1, d2])
            return d

        def createDummyItemNodes(result):
            """ XXX: This is necessary as ejabberd stupidly considers a node
            a collection only if it has children...
            """
            if not result:
                return False
            d1 = self.admin.createNode('dummy_people_node',
                options={'pubsub#collection': 'people'})
            d2 = self.admin.createNode('dummy_content_node',
                options={'pubsub#collection': 'content'})
            d = defer.DeferredList([d1, d2])
            return d

        def subscribeAdmin(result):
            if not result:
                return False
            d = self.admin.subscribe('people',
                self.settings.getUserJID('admin'),
                options={'pubsub#subscription_type': 'items',
                         'pubsub#subscription_depth': 'all'})
            return d

        def initStorage(result):
            if not result:
                return False
            storage = getUtility(IPubSubStorage)
            storage.node_items = {'people': [], 'content': []}
            storage.collections = {'people': [], 'content': []}
            return True

        def createUsers(result):
            if not result:
                return False
            # XXX: FIX ME!!!!
            # I should iterate the members and create their accounts, nodes,
            # subscriptions. Same as onUserCreation...
            return True

        def finalResult(result):
            if result:
                logger.info('Succesfully setup xmpp server')
            else:
                logger.error('Failed to setup xmpp server')

        d = self.admin.getNodes()
        d.addCallback(deleteAllNodes)
        d.addCallback(createCollections)
        d.addCallback(createDummyItemNodes)
        d.addCallback(subscribeAdmin)
        d.addCallback(initStorage)
        d.addCallback(createUsers)
        d.addCallback(finalResult)
        return d
