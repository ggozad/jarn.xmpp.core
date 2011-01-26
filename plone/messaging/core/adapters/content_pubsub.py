from Products.ATContentTypes.interface import IATContentType
from zope.interface import implements
from zope.component import adapts

from plone.messaging.core.interfaces import IPubSubable


class ATPubSubableAdapter(object):
    """Adapts AT-based content to IPubSubable.
    """

    implements(IPubSubable)
    adapts(IATContentType)

    def __init__(self, context):
        self.context = context

    def getNodeId(self):
        return self.context.UID()

    nodeId = property(getNodeId)
