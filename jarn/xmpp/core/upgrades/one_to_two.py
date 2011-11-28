import logging
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('jarn.xmpp.core')


def cleanJSRegistry(context):
    js_registry = getToolByName(context, 'portal_javascripts')
    if '++resource++jarn.xmpp.core.js/strophe.pubsub.js' in js_registry.getResourceIds():
        js_registry.unregisterResource('++resource++jarn.xmpp.core.js/strophe.pubsub.js')
    context.runImportStepFromProfile('profile-jarn.xmpp.core:default',
                                     'jsregistry')


def clearRegistry(context):
    registry = getUtility(IRegistry)
    if 'jarn.xmpp.boshURL' in registry:
        del registry.records['jarn.xmpp.boshURL']


def updateActions(context):
    context.runImportStepFromProfile('profile-jarn.xmpp.core:default',
                                     'actions')


def installJSi18n(context):
    context.runAllImportStepsFromProfile('profile-jarn.jsi18n:default')


def updateRoles(context):
    context.runImportStepFromProfile('profile-jarn.xmpp.core:default',
                                     'rolemap')


def upgrade(context):
    installJSi18n(context)
    clearRegistry(context)
    cleanJSRegistry(context)
    updateActions(context)
