from plone.z3cform.layout import FormWrapper
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class WrappedFormView(FormWrapper):
   """ Form view which renders z3c.forms embedded in a portlet.

   Subclass FormWrapper so that we can use custom frame template. """

   index = ViewPageTemplateFile("formwrapper.pt")
