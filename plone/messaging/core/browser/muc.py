from Products.Five.browser import BrowserView


class MUCView(BrowserView):

    def __init__(self, context, request):
        super(MUCView, self).__init__(context, request)

