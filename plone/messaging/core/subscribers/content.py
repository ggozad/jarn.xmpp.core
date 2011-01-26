from datetime import datetime

from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.utils import getToolByName
from twisted.words.xish.domish import Element
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from wokkel.pubsub import Item

from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.pubsub_utils import content_node_config


def pubsubObjectModified(obj, event):
    uid = obj.UID()
    pm = getToolByName(obj, 'portal_membership')
    author = pm.getAuthenticatedMember().getId()
    message = ''
    if IObjectModifiedEvent.providedBy(event):
        message = "'%s' modified." % obj.Title()
    elif IActionSucceededEvent.providedBy(event):
        message = "Workflow action '%s' on '%s'" % (event.action, obj.Title())
    entry = Element(('http://www.w3.org/2005/Atom', 'entry'))
    entry.addElement('content', content=message)
    entry.addElement('author', content=author)
    now = datetime.now().isoformat()
    entry.addElement('updated', content=now)
    entry.addElement('published', content=now)
    item = Item(payload=entry)

    client = getUtility(IAdminClient)
    d = client.publish(uid, items=[item])
    return d


def pubsubObjectAdded(obj, event):
    if 'portal_factory' in obj.getPhysicalPath():
        return
    client = getUtility(IAdminClient)
    d = client.createNode(obj.UID(), options=content_node_config)
    return d


def pubsubObjectRemoved(obj, event):
    client = getUtility(IAdminClient)
    d = client.deleteNode(obj.UID())
    return d
