from datetime import datetime

from twisted.words.xish.domish import Element
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from wokkel.pubsub import Item

from plone.messaging.core.interfaces import IAdminClient
from plone.messaging.core.interfaces import IPubSubStorage


def onObjectModified(obj, event):
    uid = obj.UID()
    storage = getUtility(IPubSubStorage)
    if uid not in storage.leaf_nodes:
        # We don't have subscribers for this content.
        return

    message = ''
    if IObjectModifiedEvent.providedBy(event):
        message = "'%s' modified." % obj.Title()
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