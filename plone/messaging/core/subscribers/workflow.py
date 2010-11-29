from zope.component import getUtility
from twisted.words.protocols.jabber.jid import JID
from Products.CMFCore.utils import getToolByName
from plone.messaging.core.interfaces import IJabberClient


def onWorkflowChange(event):
    """
    Handle workflow changes.
    If a document is published then we notify the owner.
    If a document is submitted for review we notify all reviewers.
    """
    context = event.object
    action = event.action
    wt = getToolByName(context, 'portal_workflow')
    mt = getToolByName(context, 'portal_membership')

    #if action == 'publish':
    last_action = wt.getInfoFor(context, 'review_history')[-1]
    actor_id = last_action['actor']
    actor_name = mt.getMemberInfo(actor_id)['fullname'] or actor_id
    owner_id = context.getOwner().getId()
    jid_from = JID("%s@localhost"%actor_id)
    jid_to = JID("%s@localhost"%owner_id)
    jabber_client = getUtility(IJabberClient)
    message = 'kaka'

    def sendNotification(xmlstream):
        result = xmlstream.send(message)
        return result
    d = jabber_client.execute(jid_from, 'admin',
                              sendNotification)
    #import pdb; pdb.set_trace( )
    return d
