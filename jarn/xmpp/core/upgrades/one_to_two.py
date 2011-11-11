import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('jarn.xmpp.core')


def cleanJSRegistry(context):
    js_registry = getToolByName(context, 'portal_javascripts')
    if '++resource++jarn.xmpp.core.js/strophe.pubsub.js' in js_registry.getResourceIds():
        js_registry.unregisterResource('++resource++jarn.xmpp.core.js/strophe.pubsub.js')
    context.runImportStepFromProfile('profile-jarn.xmpp.core:default',
                                     'jsregistry')
    logger.info('Cleaned js registry.')


def upgrade(context):
    cleanJSRegistry(context)
