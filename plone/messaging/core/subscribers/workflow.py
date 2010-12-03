from zope.component import getUtility
from twisted.words.protocols.jabber.jid import JID
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _mergedLocalRoles
from plone.messaging.twisted.interfaces import IJabberClient
from plone.messaging.twisted.client import Chatter


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

    if action == 'publish':
        last_action = wt.getInfoFor(context, 'review_history')[-1]
        actor_id = last_action['actor']
        actor_name = mt.getMemberInfo(actor_id)['fullname'] or actor_id
        owner_id = context.getOwner().getId()
        jid_from = JID("%s@localhost"%actor_id)
        jid_to = JID("%s@localhost"%owner_id)
        jabber_client = getUtility(IJabberClient)
        text = '%s %s at %s has been published by %s.' % \
               (context.Type(), context.Title(),
                context.absolute_url(), actor_name)

        xhtml = '<p>%s <a  xmlns="http://www.w3.org/1999/xhtml" href="%s">%s</a> has been published by %s.</p>' % \
            (context.Type(), context.absolute_url(),
             context.Title(), actor_name)

        def sendNotification(xmlstream):
            xmlstream.factory.streamManager. \
                handlers[0].sendXHTMLMessage(jid_to, text, xhtml)
            return True

        d = jabber_client.execute(jid_from, 'secret',
                                  sendNotification, [Chatter()])
        return d

    elif action == 'submit':
        last_action = wt.getInfoFor(context, 'review_history')[-1]
        actor_id = last_action['actor']
        actor_name = mt.getMemberInfo(actor_id)['fullname'] or actor_id
        jid_from = JID("%s@localhost"%actor_id)
        jabber_client = getUtility(IJabberClient)
        text = '%s %s at %s has been submitted for review by %s.' % \
               (context.Type(), context.Title(),
                context.absolute_url(), actor_name)

        xhtml = '<p>%s <a  xmlns="http://www.w3.org/1999/xhtml" href="%s">%s</a> has been submitted for publication by %s.</p>' % \
            (context.Type(), context.absolute_url(),
             context.Title(), actor_name)

        local_roles = _mergedLocalRoles(context)
        reviewer_ids = [key
                        for key in local_roles
                        if u'Reviewer' in local_roles[key]]

        def sendNotification(xmlstream):
            for rid in reviewer_ids:
                jid_to = JID("%s@localhost"%rid)
                xmlstream.factory.streamManager. \
                handlers[0].sendXHTMLMessage(jid_to, text, xhtml)
            return True
        d = jabber_client.execute(jid_from, 'secret',
                                  sendNotification, [Chatter()])
        return d
