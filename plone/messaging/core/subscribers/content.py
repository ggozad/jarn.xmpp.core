from datetime import datetime

from Products.CMFCore.interfaces import IActionSucceededEvent
from twisted.words.xish.domish import Element
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from wokkel.pubsub import Item

from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.interfaces import IPubSubStorage


def pubsubObjectModified(obj, event):
    uid = obj.UID()
    message = ''
    if IObjectModifiedEvent.providedBy(event):
        message = "'%s' modified." % obj.Title()
    elif IActionSucceededEvent.providedBy(event):
        message = "Workflow action '%s' on '%s'" % (event.action, obj.Title())
    entry = Element(('http://www.w3.org/2005/Atom', 'entry'))
    entry.addElement('content', content=message)
    entry.addElement('author', content=obj.getOwner().getId())
    now = datetime.now().isoformat()
    entry.addElement('updated', content=now)
    entry.addElement('published', content=now)
    item = Item(payload=entry)

    client = getUtility(IAdminClient)
    d = client.publish(uid, items=[item])
    return d