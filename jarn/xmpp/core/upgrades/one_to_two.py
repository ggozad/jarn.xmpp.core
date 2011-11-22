import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('jarn.xmpp.core')


def cleanJSRegistry(context):
    js_registry = getToolByName(context, 'portal_javascripts')
    if '++resource++jarn.xmpp.core.js/strophe.pubsub.js' in js_registry.getResourceIds():
        js_registry.unregisterResource('++resource++jarn.xmpp.core.js/strophe.pubsub.js')
    context.runImportStepFromProfile('profile-jarn.xmpp.core:default',
                                     'jsregistry')


def updateActions(context):
    context.runImportStepFromProfile('profile-jarn.xmpp.core:default',
                                     'actions')


def installJSi18n(context):
    context.runAllImportStepsFromProfile('profile-jarn.jsi18n:default')


def upgrade(context):
    installJSi18n(context)
    cleanJSRegistry(context)
    updateActions(context)
